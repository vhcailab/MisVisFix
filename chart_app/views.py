import json
import os
import re
import concurrent
import time
import httpx
from django.conf import settings
from django.shortcuts import get_object_or_404, render
import openai
import io
import base64
from django.http import HttpResponse, JsonResponse
import matplotlib
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import uuid
import anthropic
from rest_framework.decorators import api_view

from .utils.api_key_helper import get_asst_id, get_claude_key, get_openai_key
from .utils.base_64_to_image_utils import save_base64_image
from .utils.issue_with_image_position_utils import get_claude_key_issues_with_image_position, get_gpt_key_issues_with_image_position
from .utils.secrets import decrypt_env_var, encrypt_value
from .utils.misleading_decision_user_instruction_utils import get_mislead_status_for_image_user_instructions, get_mislead_status_for_code_user_instructions

from .utils.pitfalls_helper import PitfallManager
from .utils.learn_message_helpr import get_learn_message
from .models import ChartData, ChatMessage, ClaudeImage, GptImage, ImageLearnContent
from .serializers import ImageLearnContentSerializer

from .constants.session_key import ASST_ID, CURRENT_CHART_ID, SESSSION_CURRENT_IMAGE_HASH, OPEN_AI_KEY, CLAUDE_KEY
from .utils.open_ai_assistant import ask_question, check_run_status_with_answer, create_thread, set_instructions, upload_image
from .pitfalls import get_pitfalls
from .model_helper import CLAUDE, CLAUDE_TOKEN, GPT, GPT_4o_Model, Claude_Ai, Claude_Ai_Model
from .prompt.misleading_decision_prompt import misleading_decision_cl_prompt, misleading_decision_gpt_prompt

from .prompt.key_issues_prompt import key_issues_cl_prompt, key_issues_gpt_prompt
from .prompt.key_issues_position_prompt import key_issues_position_cl_prompt, key_issues_position_gpt_prompt
from .utils.chat_image_claude_utils import get_chat_claude_image
from .utils.chat_image_combile_utils import get_chat_combine_image
from .utils.chat_image_gpt_utils import get_chat_gpt_image
from .utils.image_generation_utils import get_dataset, get_gpt_image, get_claude_image
from .utils.image_with_dataset_utils import get_image_for_dataset
from .utils.session_helper import get_hash_data, get_session, save_session, store_hash_thread

matplotlib.use('Agg')

import matplotlib.pyplot as plt

key_issues_threshhold_count = 1
temp = 0.2

MAX_RETRIES = 5
RETRY_DELAY = 3  # seconds


def home(request):
    return render(request, 'home_page.html', {
        'MEDIA_URL': settings.MEDIA_URL,
    })


@csrf_exempt
def set_image_session(request):
    if request.method == 'POST':
        open_ai_api_key = get_openai_key(request)
        claude_api_key = get_claude_key(request)
        asst_id = get_asst_id(request)

        if not all([open_ai_api_key, claude_api_key, asst_id]):
            return JsonResponse({
                'status': 'error',
                'message': 'Missing required API keys or assistant ID in session.'
            }, status=400)
        
        data = json.loads(request.body)
        open_ai_api_key = get_openai_key(request)
        image_base64 = data.get('image')
        firebase_image_url = data.get('firebaseUrl')
        hashCode = data.get('hashCode')
        thread_id = create_thread(open_ai_api_key)
        store_hash_thread(request, hashCode, thread_id)
        save_session(request, SESSSION_CURRENT_IMAGE_HASH, hashCode)
        save_session(request, 'uploaded_image', image_base64)
        save_session(request, 'firebase_image_url', firebase_image_url)
        return JsonResponse({'status': 'success', 'image': image_base64})

    return JsonResponse({'status': 'error'}, status=400)


def dashboard(request):
    uploaded_image = request.session.get('uploaded_image', '')
    firebase_image_url = request.session.get('firebase_image_url', '')
    return render(request, 'dashboard_page.html', {
        'MEDIA_URL': settings.MEDIA_URL,
        'image_url': uploaded_image,
        'firebase_image_url': firebase_image_url
    })


def get_issues_from_gpt(request, firebase_image_url):
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            response = openai.ChatCompletion.create(
                messages=key_issues_gpt_prompt(firebase_image_url),
                model=GPT_4o_Model,
                temperature=temp
            )
            issues_list_resp = response.choices[0].get('message', {}).get('content', '')
            cleaned_temp = issues_list_resp.strip('```json').strip('```').strip()
            return json.loads(cleaned_temp)
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            attempt += 1
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                raise RuntimeError("All retry attempts failed.") from e

def get_issues_from_claude(request, image_url):
    client = anthropic.Anthropic(api_key=get_claude_key(request))
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            response = client.messages.create(
                model=Claude_Ai_Model,
                max_tokens=CLAUDE_TOKEN,
                system="You are an AI assistant tasked with analyzing data visualization charts for potential pitfalls and issues. You will be provided with a checklist of common pitfalls in data visualization and an image of a chart to analyze. Your goal is to identify any issues present in the chart and provide a detailed analysis.",
                temperature=temp,
                messages=[
                    {
                        "role": "user",
                        "content": key_issues_cl_prompt(image_url)
                    }
                ]
            )
            issues_list_resp = response.content[0].text
            start_index = issues_list_resp.find("<output>") + len("<output>")
            end_index = issues_list_resp.find("</output>")
            json_part = issues_list_resp[start_index:end_index].strip()

            # Clean the extracted JSON part
            cleaned_json = json_part.strip('```json').strip('```').strip()
            return json.loads(cleaned_json)
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            attempt += 1
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                raise RuntimeError("All retry attempts failed.") from e


def convert_issue_name(issue_name):
    if issue_name.lower().startswith('3d'):
        return 'three_d'
    else:
        return issue_name.lower().replace(" ", "_")


def check_misleading_graph(request):
    client = anthropic.Anthropic(api_key=get_claude_key(request))
    image_url = request.session.get('firebase_image_url', '')
    model = GPT_4o_Model
    consecutive_false_count = 0  # Counter for consecutive false results
    max_attempt = 1
    for attempt in range(max_attempt):
        if model == Claude_Ai:
            response = client.messages.create(
                model=Claude_Ai_Model,
                max_tokens=CLAUDE_TOKEN,
                system="You are an AI tasked with analyzing graphs to determine if they are misleading. You will be provided with an image of a graph, and your job is to decide whether the graph is misleading or not.",
                temperature=temp,
                messages=[
                    {
                        "role": "user",
                        "content": misleading_decision_cl_prompt(image_url)
                    }
                ]
            )
            print(response.content[0].text)
            decision_match = re.search(r"<decision>\s*(.*?)\s*</decision>", response.content[0].text, re.DOTALL)
        else:
            response = openai.ChatCompletion.create(
                messages=misleading_decision_gpt_prompt(image_url),
                model=GPT_4o_Model,
                temperature=temp
            )
            print(response['choices'][0]['message']['content'])
            decision_match = re.search(r"<decision>\s*(.*?)\s*</decision>",
                                       response['choices'][0]['message']['content'])

        # Extract the decision value from the response

        if decision_match:
            decision = decision_match.group(1).strip().lower()
            print(decision)

            if decision == "true":
                return True  # Return immediately if the decision is true
            elif decision == "false":
                consecutive_false_count += 1
                if consecutive_false_count >= max_attempt:
                    return False  # Return false after 3 consecutive false results
        else:
            # Handle the case where the decision tag is missing
            raise ValueError("No <decision> tag found in the response.")
    return False


def get_claude_key_issue(request, firebase_image_url, width, height):
    major = []
    minor = []
    potentials = []
    all_key_issues = []
    is_found = False
    resp_count = 1

    # Loop to get key issues up to a certain threshold
    while resp_count <= key_issues_threshhold_count:
        print("Key issue claude running")
        # issues = get_issues_from_claude(request, firebase_image_url)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_issues = executor.submit(get_issues_from_claude, request, firebase_image_url)
            issues = future_issues.result()
        is_found = False

        # Helper function to add issues to the respective lists
        def add_issues(issue_list, issue_type):
            nonlocal is_found, resp_count
            existing_titles = {issue['title'] for issue in all_key_issues}
            for issue in issue_list:
                if issue['title'] not in existing_titles:
                    is_found = True
                    resp_count = 1
                    all_key_issues.append(issue)
                    issue_type.append(issue)

        # Categorize issues based on severity
        current_major = [issue for issue in issues if issue['severity'] == 'major']
        current_minor = [issue for issue in issues if issue['severity'] == 'minor']
        current_potential = [issue for issue in issues if issue['severity'] == 'potential']

        # Add categorized issues to respective lists
        add_issues(current_major, major)
        add_issues(current_minor, minor)
        add_issues(current_potential, potentials)

        if not is_found:
            resp_count += 1

        # resp_count += 1

    key_issues = [issue['title'] for issue in all_key_issues]

    if len(key_issues) > 0:
        key_issues_with_pos_resp = get_claude_key_issues_with_image_position(request, key_issues, width, height)

        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     future_key_issues_with_pos_resp = executor.submit(get_claude_key_issues_with_image_position, request, key_issues, width, height)
        #     key_issues_with_pos_resp = future_key_issues_with_pos_resp.result()

        # Adjust issue IDs for 3D
        for item in key_issues_with_pos_resp:
            if item['issues_id'] == '3d':
                item['issues_id'] = 'three_d'

        # Match the issues with image positions for major, minor, and potential issues
        def update_position_info(issue_list):
            for item in issue_list:
                for issue in key_issues_with_pos_resp:
                    if item['title'] == issue['issues_name']:
                        item['top_gap'] = issue['top_gap']
                        item['left_gap'] = issue['left_gap']
                        item['id'] = issue['issues_id']

        update_position_info(major)
        update_position_info(minor)
        update_position_info(potentials)

        valid_pitfall_labels = {v["label"] for v in get_pitfalls().values()}
        major = filter_valid_issues(major, valid_pitfall_labels)
        minor = filter_valid_issues(minor, valid_pitfall_labels)
        potentials = filter_valid_issues(potentials, valid_pitfall_labels)
        
        key_issues = [issue for issue in key_issues if issue in valid_pitfall_labels]

        return {
            'key_issues': key_issues,
            'major': major,
            'minor': minor,
            'potentials': potentials,
        }
    else:
        return {
            'key_issues': [],
            'major': [],
            'minor': [],
            'potentials': [],
        }


def filter_valid_issues(issue_list, valid_pitfall_labels):
    return [issue for issue in issue_list if issue["title"] in valid_pitfall_labels]

def get_gpt_key_issue(request, firebase_image_url, width, height):
    major = []
    minor = []
    potentials = []
    all_key_issues = []
    is_found = False
    resp_count = 1

    # Loop to get key issues up to a certain threshold
    while resp_count <= key_issues_threshhold_count:
        print("Key issue gpt running")
        # issues = get_issues_from_gpt(request, firebase_image_url)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_issues = executor.submit(get_issues_from_gpt, request, firebase_image_url)
            issues = future_issues.result()
        
        is_found = False

        # Helper function to add issues to the respective lists
        def add_issues(issue_list, issue_type):
            nonlocal is_found, resp_count
            existing_titles = {issue['title'] for issue in all_key_issues}
            for issue in issue_list:
                if issue['title'] not in existing_titles:
                    is_found = True
                    resp_count = 1
                    all_key_issues.append(issue)
                    issue_type.append(issue)

        # Categorize issues based on severity
        current_major = [issue for issue in issues if issue['severity'] == 'major']
        current_minor = [issue for issue in issues if issue['severity'] == 'minor']
        current_potential = [issue for issue in issues if issue['severity'] == 'potential']

        # Add categorized issues to respective lists
        add_issues(current_major, major)
        add_issues(current_minor, minor)
        add_issues(current_potential, potentials)

        if not is_found:
            resp_count += 1
        # resp_count += 1

    # Extract just the titles of the key issues
    key_issues = [issue['title'] for issue in all_key_issues]

    if len(key_issues) > 0:
        key_issues_with_pos_resp = get_gpt_key_issues_with_image_position(request, key_issues, width, height)
        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     future_key_issues_with_pos_resp = executor.submit(get_gpt_key_issues_with_image_position, request, key_issues, width, height)
        #     key_issues_with_pos_resp = future_key_issues_with_pos_resp.result()

        # Adjust issue IDs for 3D
        for item in key_issues_with_pos_resp:
            if item['issues_id'] == '3d':
                item['issues_id'] = 'three_d'

        # Match the issues with image positions for major, minor, and potential issues
        def update_position_info(issue_list):
            for item in issue_list:
                for issue in key_issues_with_pos_resp:
                    if item['title'] == issue['issues_name']:
                        item['top_gap'] = issue['top_gap']
                        item['left_gap'] = issue['left_gap']
                        item['id'] = issue['issues_id']

        update_position_info(major)
        update_position_info(minor)
        update_position_info(potentials)
        
        valid_pitfall_labels = {v["label"] for v in get_pitfalls().values()}
        major = filter_valid_issues(major, valid_pitfall_labels)
        minor = filter_valid_issues(minor, valid_pitfall_labels)
        potentials = filter_valid_issues(potentials, valid_pitfall_labels)
        
        key_issues = [issue for issue in key_issues if issue in valid_pitfall_labels]

        return {
            'key_issues': key_issues,
            'major': major,
            'minor': minor,
            'potentials': potentials,
        }
    else:
        return {
            'key_issues': [],
            'major': [],
            'minor': [],
            'potentials': [],
        }


def get_key_issues(request):
    is_misleading = check_misleading_graph(request)

    if is_misleading:
        firebase_image_url = request.session.get('firebase_image_url', '')
        width = request.POST.get('width', '')
        height = request.POST.get('height', '')

        chart = ChartData.objects.create(
           original_image=firebase_image_url
        )
        save_session(request, CURRENT_CHART_ID, chart.id)
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_claude = executor.submit(get_claude_key_issue, request, firebase_image_url, width, height)
            future_gpt = executor.submit(get_gpt_key_issue, request, firebase_image_url, width, height)

            claude_data = future_claude.result()
            gpt_data = future_gpt.result()

        merged_key_issues = list(set(claude_data['key_issues'] + gpt_data['key_issues']))
        save_session(request, 'key_issues', merged_key_issues)
        issues_data = {
            'key_issues': merged_key_issues,
            'major_claude': claude_data['major'],
            'minor_claude': claude_data['minor'],
            'potentials_claude': claude_data['potentials'],
            'major_gpt': gpt_data['major'],
            'minor_gpt': gpt_data['minor'],
            'potentials_gpt': gpt_data['potentials'],
        }
        chart_id = request.session.get(CURRENT_CHART_ID)
        if chart_id:
            chart = get_object_or_404(ChartData, id=chart_id)
            chart.key_issues = issues_data
            chart.save()
        return JsonResponse(issues_data)
    else:
        firebase_image_url = request.session.get('firebase_image_url', '')
        chart = ChartData.objects.create(
           original_image=firebase_image_url
        )
        save_session(request, CURRENT_CHART_ID, chart.id)
        return JsonResponse({
            'key_issues': [],
            'major': [],
            'minor': [],
            'potentials': [],
        })


def fetch_gpt_image(request):
    key_issues = request.POST.get('key_issues', '').split(',')
    dataset = request.POST.get('dataset', '')
    image_url = request.session.get('firebase_image_url', '')
    response = get_gpt_image(request, dataset, image_url, key_issues)
    chart_id = request.session.get(CURRENT_CHART_ID)
    if chart_id:
        chart = get_object_or_404(ChartData, id=chart_id)
        chart.gpt_solved_list = response['solved_list']
        chart.save()
        gpt_image = GptImage(chart=chart)
        save_base64_image(response['image'], gpt_image.image_file, GPT)
        gpt_image.save()

    return JsonResponse({'image': response['image'], 'solved_list': response['solved_list']})


def fetch_claude_image(request):
    key_issues = request.POST.get('key_issues', '').split(',')
    dataset = request.POST.get('dataset', '')
    image_url = request.session.get('firebase_image_url', '')
    response = get_claude_image(request, dataset, image_url, key_issues)
    chart_id = request.session.get(CURRENT_CHART_ID)
    if chart_id:
        chart = get_object_or_404(ChartData, id=chart_id)
        chart.claude_solved_list = response['solved_list']
        chart.save()
        claude_image = ClaudeImage(chart=chart)
        save_base64_image(response['image'], claude_image.image_file, CLAUDE)
        claude_image.save()
    return JsonResponse({'image': response['image'], 'solved_list': response['solved_list']})

@csrf_exempt
def chat_api(request):
    if request.method == "POST":
        user_message = request.POST.get('message')
        image_url = request.session.get('firebase_image_url', '')
        key_issues = request.session.get('key_issues', '')
        message_type = request.POST.get('messageType', '')
        chart_id = request.session.get(CURRENT_CHART_ID)
        if chart_id:
            chart = get_object_or_404(ChartData, id=chart_id)
            ChatMessage.objects.create(
                chart=chart,
                user="You",
                content=user_message
            )
        if message_type == 'original_claude' or message_type == 'latest_claude':
            response = get_chat_claude_image(request, user_message, message_type, key_issues)
            if chart_id:
                ChatMessage.objects.create(
                    chart=chart,
                    user="MisVisFix",
                    content=response['changes_made']
                )
                claude_image = ClaudeImage(chart=chart)
                save_base64_image(response['image'], claude_image.image_file, CLAUDE)
                claude_image.save()
            return JsonResponse({'image': response['image'], 'changes_made': response['changes_made']})
        elif message_type == 'original_gpt' or message_type == 'latest_gpt':
            response = get_chat_gpt_image(request, user_message, message_type, key_issues)
            if chart_id:
                ChatMessage.objects.create(
                    chart=chart,
                    user="MisVisFix",
                    content=response['changes_made']
                )
                gpt_image = GptImage(chart=chart)
                save_base64_image(response['image'], gpt_image.image_file, GPT)
                gpt_image.save()
            return JsonResponse({'image': response['image'], 'changes_made': response['changes_made']}) 
        elif message_type == 'original_both':
            response = get_chat_combine_image(request, user_message, message_type, key_issues)
            if chart_id:
                ChatMessage.objects.create(
                    chart=chart,
                    user="MisVisFix",
                    content=response['changes_made']
                )
                claude_image = ClaudeImage(chart=chart)
                save_base64_image(response['claude_image'], claude_image.image_file, CLAUDE)
                claude_image.save()
                gpt_image = GptImage(chart=chart)
                save_base64_image(response['gpt_image'], gpt_image.image_file, GPT)
                gpt_image.save()
            return JsonResponse({'claude_image': response['claude_image'], 'gpt_image': response['gpt_image'], 'changes_made': response['changes_made']})
        else:
            image_hash = get_session(request, SESSSION_CURRENT_IMAGE_HASH)
            threa_id = get_hash_data(request, image_hash)
            open_ai_api_key = get_openai_key(request)
            asst_id = get_asst_id(request)
            run_id = ask_question(threa_id, user_message, open_ai_api_key, asst_id)
            if run_id:
                return JsonResponse({'run_id': run_id})
            else:
                return JsonResponse({'error': 'Invalid File Upload Error'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def upload_dataset(request):
    if request.method == 'POST' and request.FILES.get('file'):
        # Save the uploaded file temporarily
        uploaded_file = request.FILES['file']

        file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)

        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Load the Excel file into pandas DataFrame
        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            return JsonResponse({'error': f'Failed to process Excel file: {str(e)}'}, status=400)

        # Create a prompt based on the file's data (generalized for different data sets)
        columns = df.columns.tolist()
        data_sample = df.to_dict()  # Get a sample of the data

        try:
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            response = get_image_for_dataset(request, csv_data)
            chart_id = request.session.get(CURRENT_CHART_ID)

            if chart_id:
                chart = ChartData.objects.filter(id=chart_id).first()
                if chart is not None:
                    if response and response['gpt_image'] and chart_id:
                        gpt_image = GptImage(chart=chart)
                        save_base64_image(response['gpt_image'], gpt_image.image_file, GPT)
                        gpt_image.save()
                    if response and response['claude_image'] and chart_id:
                        claude_image = ClaudeImage(chart=chart)
                        save_base64_image(response['claude_image'], claude_image.image_file, CLAUDE)
                        claude_image.save()
                        
            
            return JsonResponse({
                'gpt_image': response['gpt_image'],
                'claude_image': response['claude_image'],
            })
        except Exception as e:
            return JsonResponse({'error': f'Failed to convert data to CSV: {str(e)}'}, status=500)


def prepare_key_issues_with_details(key_issues):
    issues = key_issues
    pitfalls = get_pitfalls()

    issues_details = []

    for issue in issues:
        # Convert the issue to lowercase and replace spaces with underscores for the key
        key = issue.lower().replace(' ', '_')

        # Check if the key exists in the pitfalls dictionary
        if issue != '3d' and key in pitfalls:
            details = f"{pitfalls[key]['label']}: {pitfalls[key]['description']}"
            issues_details.append(details)
        else:
            three_d_key = 'three_d'
            if three_d_key in pitfalls:
                details = f"{pitfalls[three_d_key]['label']}: {pitfalls[three_d_key]['description']}"
                issues_details.append(details)
    return issues_details


def fetch_get_dataset(request):
    key_issues = request.POST.get('key_issues', '').split(',')
    image_url = request.session.get('firebase_image_url', '')
    dataset = get_dataset(request, Claude_Ai_Model, key_issues, image_url)
    save_session(request, 'dataset', dataset)
    response = HttpResponse(dataset, content_type="text/plain")
    return response

def set_thread_instructions(request):
    image_hash = get_session(request, SESSSION_CURRENT_IMAGE_HASH)
    contents = ImageLearnContent.objects.filter(image_hash=image_hash).order_by('-created_at')
    serializer = ImageLearnContentSerializer(contents, many=True)
    data = serializer.data

    predefined_answers = [answer['content'] for answer in data]
    pitfalls = get_pitfalls()

    prompt = ""
    if len(predefined_answers) > 0:
        prompt = """**Predefined Answer Guidelines for the Chart:**\n\n"""

        for idx, content in enumerate(predefined_answers, start=1):
            prompt += f"{idx}. {content}\n"

    prompt += f"""
        **Instructions:**  
            - When answering questions about the chart, first check if the answer exists in the predefined list.  
            - If the answer is predefined, respond accordingly **without mentioning it as a predefined rule** (assume it as learned knowledge).  
            - If the question is not covered in the predefined answers, analyze the attached image and respond accordingly.
            - Provide answers inside the `<answer></answer>` tag.

            **Issue Detection Guidelines**  
            
            - If the user is trying to **learn, define, understand, or describe** an issue, **first check if their understanding is correct based on the provided chart.** 
            - If their understanding is incorrect, explain why in <answer>.  
            - If their understanding is correct, determine whether it should be considered a new issue.  
            - **Before adding any issue, check if it already match in the predefined list.**  
                - **If it exists in the predefined lists, add it to <existing_issues>.**  
            - **If it does NOT exist in the predefined lists, add it to <new_issues>.**  
            - **If no new issues are detected, return an empty <new_issues> array ([]).**  
                     
            ** Here is the response tag Purposes (what you have to include in the tags)**  

            1. **`<answer>`**:  
            - Contains the **regular response**, **explanation of new/existing issues**, or **clarifications if the user is learning**.  
            - If the user is **learning, defining, or describing** an issue incorrectly, explain why.  
            - If the user correctly identifies an issue, confirm and explain it clearly.

            2. **`<existing_issues>`**:  
            - **Lists issues that already exist in the predefined issues list** and **have been detected in the uploaded chart**.  
            - The issue must be included with a **detailed paragraph** describing when this issue occurs.  
            - If new measurable detection criteria are found, **they should be merged naturally into the existing description** as a continuous explanation.  
            - The description **should remain general and must not contain chart-specific examples** to allow reuse in different contexts.  
            - **An example should be dynamically generated** based on the issue description and detection criteria.  
            - If **no existing issues are detected**, return an empty array (`[]`).
            - **Ensure that the response is always valid JSON with double quotes (`""`) instead of single quotes (`''`).**  

            3. **`<new_issues>`**:  
            - **Lists issues that do not exist in the predefined list** and should be **added as new detections**.
            - If **no new issues are detected**, return an empty array (`[]`).
            - **An example should be dynamically generated** based on the issue description and detection criteria.
            - **Ensure that the response is always valid JSON with double quotes (`""`) instead of single quotes (`''`).**  

            **Predefined Issues List:**  
                {json.dumps(pitfalls, indent=4)}

            
            Response Format (Always Returning `<answer>`, `<existing_issues>`, & `<new_issues>`):

            <answer>
                "Your response should be a regular answer, an explanation of new/existing issues, or a clarification if the user is learning."
            </answer>
            <existing_issues>
            {[
                {
                    "existing_issue_key": {
                        "label": "Existing Issue Label",
                        "description": "A visualization should ensure that [explain the issue]. This issue is detected when the chart exhibits [existing measurable criteria 1], [existing measurable criteria 2], and [existing measurable criteria 3]. Additionally, if [new measurable criteria improving detection 1] or [new measurable criteria improving detection 2] are present, the issue is further reinforced. Other contributing factors include [existing relevant points] and any additional inconsistencies such as [new measurable criteria improving detection 3]. When these conditions are met, the issue is confirmed. **Example:** [Generate an example based on the issue description and detection criteria.]"
                    }
                }
            ]}
            </existing_issues>

            <new_issues>
            {[
                {
                    "new_issue_key": {
                        "label": "New Issue Label",
                        "description": "A visualization should ensure that [explain the issue]. This issue is detected when [list measurable detection criteria]. If [specific condition] occurs, this issue should be flagged. **Example:** [Dynamically generate an example based on the issue description and detection criteria.]"
                    }
                }
            ]}
            </new_issues>

            **Important Formatting Requirements:**
            - Both `<existing_issues>` and `<new_issues>` must always contain a **list (`[]`) of individual issue objects**.
            - Each object must be **separate** inside the array. Do **not** place two keys inside a single object.
            - Each issue object must contain **one key only** and include a nested object with `label` and `description`.

    """

    image_url = request.session.get('firebase_image_url', '')
    open_ai_api_key = get_openai_key(request)
    file = upload_image(image_url, open_ai_api_key)
    if file:
        image_hash = get_session(request, SESSSION_CURRENT_IMAGE_HASH)
        threa_id = get_hash_data(request, image_hash)
        asst_id = get_asst_id(request)
        run_id = set_instructions(threa_id, prompt, file['id'], open_ai_api_key, asst_id)
        if run_id:
            return JsonResponse({'run_id': run_id})
        else:
            return JsonResponse({'error': 'Invalid File Upload Error'}, status=400)

    return JsonResponse({'messages': 'Learn Successfully'})


def check_run_status(request):
    image_hash = get_session(request, SESSSION_CURRENT_IMAGE_HASH)
    threa_id = get_hash_data(request, image_hash)
    run_id = request.GET.get("run_id")
    open_ai_api_key = get_openai_key(request)
    response = check_run_status_with_answer(threa_id, run_id, open_ai_api_key)
    response_json = json.loads(response.content)
    if response_json and response_json.get('status') == 'completed':
        parsed_response = response_json.get('response')
        merged_issues = merge_issues(parsed_response['existing_issues'], parsed_response['new_issues'])
        chart_id = request.session.get(CURRENT_CHART_ID)
        if chart_id:
            if merged_issues and len(merged_issues) > 0:
                chart = ChartData.objects.filter(id=chart_id).first()
                if chart is not None:
                    ChatMessage.objects.create(
                        chart=chart,
                        user="MisVisFix",
                        content=parsed_response['answer'],
                        issues=merged_issues
                    )
            else:
                chart = ChartData.objects.filter(id=chart_id).first()
                if chart is not None:
                    ChatMessage.objects.create(
                        chart=chart,
                        user="MisVisFix",
                        content=parsed_response['answer'],
                        issues=merged_issues
                    )
    return response

def merge_issues(new_issues, existing_issues):
    new_issues = json.loads(new_issues)
    existing_issues = json.loads(existing_issues)
    combined = new_issues + existing_issues
    merged_dict = {}

    for issue in combined:
        key = list(issue.keys())[0]  # Extract the outer key, e.g., 'misrepresentation'
        merged_dict[key] = issue     # Overwrites if key already seen

    merged_array = list(merged_dict.values())
    return merged_array


@api_view(['POST'])
def save_learn_content(request):
    image_hash = get_session(request, SESSSION_CURRENT_IMAGE_HASH)
    content = request.data.get('content', '').strip()  # Extract content from request
    learn_entry = ImageLearnContent.objects.create(image_hash=image_hash, content=content)
    return JsonResponse({"message": "Learn content saved", "data": ImageLearnContentSerializer(learn_entry).data})


@csrf_exempt  # Disable CSRF for testing purposes; use proper CSRF protection in production
def save_messages(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            messages = data.get('messages', [])
            learning_sets_response = get_learn_message(request, messages)
            issues_list_resp = learning_sets_response.choices[0].get('message', {}).get('content', '')
            cleaned_temp = issues_list_resp.strip('```json').strip('```').strip()
            learn_items = json.loads(cleaned_temp)
            print(learn_items)
            
            if len(learn_items['learning_points']) > 0 :
                image_hash = get_session(request, SESSSION_CURRENT_IMAGE_HASH)
                for point in learn_items['learning_points']:
                    learn_content = ImageLearnContent(
                        image_hash=image_hash,
                        content=point,
                    )
                    learn_content.save()
                return JsonResponse({'status': 'success', 'message': 'Learning has been successfully completed.'})
            else:
                return JsonResponse({'status': 'success', 'message': 'There is no learning item found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    

@csrf_exempt
def add_new_issue(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            manager = PitfallManager()
            manager.add_pitfall(data)
            return JsonResponse({"status": "success", "message": "Issue added successfully"}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

def gallery_page(request):
    return render(request, 'gallery.html', {
        'MEDIA_URL': settings.MEDIA_URL,
    })


def gallery_api(request):
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))

    charts = ChartData.objects.all()
    records_total = charts.count()
    charts = charts[start:start + length]

    data = []
    for chart in charts:
        gpt_image = chart.gpt_images.first()
        claude_image = chart.claude_images.first()

        data.append([
            chart.original_image,
            claude_image.image_file.url if claude_image and claude_image.image_file else None,
            gpt_image.image_file.url if gpt_image and gpt_image.image_file else None,
            chart.id
        ])

    return JsonResponse({
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_total,
        'data': data
    })


def view_image(request, index):
    chart = get_object_or_404(ChartData, id=index)

    # Get all GPT image URLs
    gpt_images = [
        img.image_file.url
        for img in chart.gpt_images.all()
        if img.image_file
    ]

    # Get all Claude image URLs
    claude_images = [
        img.image_file.url
        for img in chart.claude_images.all()
        if img.image_file
    ]

    chats = []

    for chat in chart.chats.all().order_by('created_at'):
        chat_entry = {
            'user': chat.user,
            'content': chat.content
        }

        if chat.issues:  # only include if issues are present
            chat_entry['new_issues'] = chat.issues

        chats.append(chat_entry)

    data = {
        'MEDIA_URL': settings.MEDIA_URL,
        'original_image': chart.original_image,
        'key_issues': chart.key_issues,
        'gpt': {
            'images': gpt_images,
            'solved_list': chart.gpt_solved_list
        },
        'claude': {
            'images': claude_images,
            'solved_list': chart.claude_solved_list
        },
        'chats': chats
    }
    return render(request, 'view.html', data)


@csrf_exempt
def analyze_chart_code(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            message_type = body['messageType']
            content = body['content']
            if message_type == 'original_claude':
                image_url = request.session.get('firebase_image_url', '')
                response = get_mislead_status_for_image_user_instructions(content, image_url)
                return response
            elif message_type == 'latest_claude':
                corrected_image_code = get_session(request, 'corrected_claude_image_code')
                response = get_mislead_status_for_code_user_instructions(content, corrected_image_code)
                return response
            elif message_type == 'original_gpt':
                image_url = request.session.get('firebase_image_url', '')
                response = get_mislead_status_for_image_user_instructions(content, image_url)
                return response
            elif message_type == 'latest_gpt':
                corrected_image_code = get_session(request, 'corrected_gpt_image_code')
                response = get_mislead_status_for_code_user_instructions(content, corrected_image_code)
                return response
            else:
                image_url = request.session.get('firebase_image_url', '')
                response = get_mislead_status_for_image_user_instructions(content, image_url)
                return response

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "POST request required."}, status=405)

def how_it_works(request):
    return render(request, 'how_it_works.html', {
        'MEDIA_URL': settings.MEDIA_URL,
    })

@csrf_exempt
def save_user_api_keys_session(request):
    if request.method == "POST":
        data = json.loads(request.body)
        openai_key = data.get("openai_key")
        claude_key = data.get("claude_key")
        asst_id = data.get("asst_id")

        if openai_key:
            openai.api_key = openai_key
            save_session(request, OPEN_AI_KEY, encrypt_value(openai_key))
        if claude_key:
            save_session(request, CLAUDE_KEY, encrypt_value(claude_key))
        if asst_id:
            save_session(request, ASST_ID, encrypt_value(asst_id))

        return JsonResponse({'success': True})

def how_it_setup_key(request):
    return render(request, 'how_to_setup_key.html', {
        'MEDIA_URL': settings.MEDIA_URL,
    })