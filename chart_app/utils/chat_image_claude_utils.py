import os
import re
import anthropic
import matplotlib
import openai
from django.http import HttpResponse, JsonResponse
import io
import base64

from ..utils.api_key_helper import get_claude_key
from ..utils.secrets import decrypt_env_var
from .session_helper import save_session, get_session
from ..model_helper import CLAUDE_TOKEN, GPT_TOKEN, Claude_Ai_Model, GPT_4o_Model
from ..prompt.claude_chat_image_prompt import chat_original_image_cl_prompt, chat_latest_image_cl_prompt
from ..prompt_helper import get_image_error_correction

temp = 0.2

matplotlib.use('Agg')

import matplotlib.pyplot as plt


def get_chat_claude_image(request, question, message_type, key_issues):
    client = anthropic.Anthropic(api_key=get_claude_key(request))
    corrected_image_code = get_session(request, 'corrected_claude_image_code')
    original_image_url = request.session.get('firebase_image_url', '')
    dataset = request.session.get('dataset', '')
    changes_made = ''
    if message_type == 'original_claude':
        response = client.messages.create(
            model=Claude_Ai_Model,
            max_tokens=CLAUDE_TOKEN,
            system="You are an AI assistant tasked with analyzing misleading charts and creating corrected versions based on user queries. Your goal is to address the issues in the original chart and provide a solution that accurately represents the data.",
            temperature=temp,
            messages=[
                {
                    "role": "user",
                    "content": chat_original_image_cl_prompt(question, original_image_url, dataset, key_issues)
                }
            ]
        )
        generated_text = response.content[0].text
        python_code_match = re.search(r"<python_code>(.*?)</python_code>", generated_text, re.DOTALL)
        if python_code_match:
            python_code_content = python_code_match.group(1).strip()
            cleaned_python_code = re.sub(r"^```python|```$", "", python_code_content, flags=re.MULTILINE).strip()
            generated_code = cleaned_python_code
        else:
            return HttpResponse("Error: Unable to extract Python code from the response.")
        
        changes_made_match = re.search(r"<changes_made>(.*?)</changes_made>", generated_text, re.DOTALL)
        if changes_made_match:
            changes_made = changes_made_match.group(1).strip()
        else:
            print("No <changes_made> section found.")
    else:
        response = client.messages.create(
            model=Claude_Ai_Model,
            max_tokens=CLAUDE_TOKEN,
            system="You are an expert in analyzing and modifying Python code. Your task is to modify a given Python code according to a specific request while adhering to certain guidelines and best practices. Follow these instructions carefully:",
            temperature=temp,
            messages=[
                {
                    "role": "user",
                    "content": chat_latest_image_cl_prompt(question, corrected_image_code)
                }
            ]
        )
        generated_text = response.content[0].text
        changes_made_match = re.search(r"<changes_made>(.*?)</changes_made>", generated_text, re.DOTALL)
        if changes_made_match:
            changes_made = changes_made_match.group(1).strip()
        else:
            print("No <changes_made> section found.")
        python_code_match = re.search(r"<modified_code>(.*?)</modified_code>", generated_text, re.DOTALL)
        if python_code_match:
            python_code_content = python_code_match.group(1).strip()
            cleaned_python_code = re.sub(r"^```python|```$", "", python_code_content, flags=re.MULTILINE).strip()
            generated_code = cleaned_python_code
        else:
            return HttpResponse("Error: Unable to extract Python code from the response.")

    # Extract the generated code

    # Print the generated code for debugging
    # print("Generated Python Code:\n")
    # print(generated_code)

    # Dynamic import necessary libraries
    namespace = {}

    try:
        # Execute the code in the provided namespace
        exec(generated_code, namespace)

        # Save the plot to a BytesIO object
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)

        # Encode the image as Base64
        img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
        save_session(request, 'corrected_claude_image_code', generated_code)
        # Close the BytesIO object
        img_buffer.close()
        return {
            'image': img_base64,
            'changes_made': changes_made
        }
    except Exception as e:
        response_new = openai.ChatCompletion.create(
            model=GPT_4o_Model,
            messages=get_image_error_correction(generated_code, e),
            max_tokens=GPT_TOKEN,
            temperature=temp
        )
        generated_text_new = response_new['choices'][0]['message']['content'].strip()

        # Use a regular expression to extract the Python code block
        code_match_new = re.search(r"```python(.*?)```", generated_text_new, re.DOTALL)
        if code_match_new:
            generated_code_new = code_match_new.group(1).strip()
        else:
            print("Error: Unable to extract Python code new from the response.")
            # print(generated_text_new)
            return HttpResponse("Error: Unable to extract Python code from the response.")

        # Print the generated code for debugging
        # print("Generated New Python Code:\n")
        # print(generated_code_new)

        # Dynamic import necessary libraries
        namespace_new = {}
        try:
            exec(generated_code_new, namespace_new)
            # Save the plot to a BytesIO object
            img_buffer_new = io.BytesIO()
            plt.savefig(img_buffer_new, format='png')
            img_buffer_new.seek(0)

            # Encode the image as Base64
            img_base64_new = base64.b64encode(img_buffer_new.read()).decode('utf-8')
            save_session(request, 'corrected_claude_image_code', generated_code_new)
            # Close the BytesIO object
            img_buffer_new.close()
            return {
                'image': img_base64_new,
                'changes_made': changes_made
            }
        except Exception as e:
            print(f"Error during corrected code execution: {e}")
            return JsonResponse({'error': "Something went wrong with the corrected code as well."}, status=400)
