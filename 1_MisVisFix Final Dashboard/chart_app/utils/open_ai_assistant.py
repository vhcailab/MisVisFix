import ast
import json
import os
from django.http import JsonResponse
import requests

from ..utils.secrets import decrypt_env_var

def create_thread(api_key):
    response = requests.post(
        "https://api.openai.com/v1/threads",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "OpenAI-Beta": "assistants=v2"},
        json={}
    )
    thread_id = response.json().get("id")
    return thread_id


def upload_image(image_url, api_key):
    response = requests.get(image_url)
    if response.status_code == 200:
        file_content = response.content
        file_name = os.path.basename(image_url.split("?")[0])  
        print(file_name)
        files = {"file": (file_name, file_content)}
        data = {"purpose": "assistants"}
        upload_response = requests.post(
            "https://api.openai.com/v1/files",
            headers={"Authorization": f"Bearer {api_key}", "OpenAI-Beta": "assistants=v2"},
            files=files,
            data=data
        )
        return upload_response.json()
    else:
        print("Error downloading file:", response.status_code)
        return None
    

def ask_question(thread_id, question, api_key, asst_id, file_id = None):
    if file_id:
        response = requests.post(
            f"https://api.openai.com/v1/threads/{thread_id}/messages",
            headers={"Authorization": f"Bearer {api_key}", "OpenAI-Beta": "assistants=v2"},
            json={
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text":f"""
                            {question}

                            Note: Please follow instructions carefully
                        """
                    },
                    {
                        "type": "image_file", 
                        "image_file": {
                            "file_id": file_id, 
                            "detail": "high"
                        }
                    }
                ],
            }
        )
    else:
        response = requests.post(
            f"https://api.openai.com/v1/threads/{thread_id}/messages",
            headers={"Authorization": f"Bearer {api_key}", "OpenAI-Beta": "assistants=v2"},
            json={
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text":question
                    },
                ],
            }
        )

    if response.status_code != 200:
        print("Error sending message:", response.json())  # Debugging
        return None  # Stop execution if message fails
    run_response = requests.post(
        f"https://api.openai.com/v1/threads/{thread_id}/runs",
        headers={"Authorization": f"Bearer {api_key}", "OpenAI-Beta": "assistants=v2"},
        json={"assistant_id": asst_id}
    )
    run_id = run_response.json().get("id")
    return run_id


def check_run_status_with_answer(thread_id, run_id, api_key):
    response = requests.get(
        f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}",
        headers={"Authorization": f"Bearer {api_key}", "OpenAI-Beta": "assistants=v2"},
    )

    if response.status_code != 200:
        return JsonResponse({"status": "error", "message": "Failed to fetch run status."})

    status = response.json().get("status")

    if status == "completed":
        # ✅ Fetch the assistant's response
        messages_response = requests.get(
            f"https://api.openai.com/v1/threads/{thread_id}/messages",
            headers={"Authorization": f"Bearer {api_key}", "OpenAI-Beta": "assistants=v2"},
        )

        if messages_response.status_code != 200:
            return JsonResponse({"status": "error", "message": "Failed to fetch messages."})

        messages = messages_response.json().get("data", [])
        assistant_reply = messages[0]["content"] if messages else "No response found."

        answers = process_answer(assistant_reply)

        return JsonResponse({"status": "completed", "response": answers})

    elif status in ["failed", "cancelled"]:
        return JsonResponse({"status": "failed", "response": "Error processing request."})

    return JsonResponse({"status": "in_progress"})  


def set_instructions(thread_id, question, file_id, api_key, asst_id):
    response = requests.post(
            f"https://api.openai.com/v1/threads/{thread_id}/messages",
            headers={"Authorization": f"Bearer {api_key}", "OpenAI-Beta": "assistants=v2"},
            json={
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text":question
                    },
                    {
                        "type": "image_file", 
                        "image_file": {
                            "file_id": file_id, 
                            "detail": "high"
                        }
                    }
                ],
            }
        )
    if response.status_code != 200:
        print("Error sending message:", response.json())  # Debugging
        return None  # Stop execution if message fails
    run_response = requests.post(
        f"https://api.openai.com/v1/threads/{thread_id}/runs",
        headers={"Authorization": f"Bearer {api_key}", "OpenAI-Beta": "assistants=v2"},
        json={"assistant_id": asst_id}
    )
    run_id = run_response.json().get("id")
    return run_id

def process_answer(text):
    # text_data = text[0]['text']['value']
    text_data = ''

    for item in text:
        if item.get('type') == 'text' and 'value' in item.get('text', {}):
            text_data = item['text']['value']
            break
        
    print(text_data)
    
    # Extract answer
    answer_start = text_data.find('<answer>') + len('<answer>')
    answer_end = text_data.find('</answer>')
    answer = text_data[answer_start:answer_end].strip()

    # Extract existing issues
    existing_issues = []
    existing_start = text_data.find('<existing_issues>') + len('<existing_issues>')
    existing_end = text_data.find('</existing_issues>')
    if existing_start != -1 and existing_end != -1:
        existing_issues_text = text_data[existing_start:existing_end].strip()
        existing_issues = ast.literal_eval(existing_issues_text) if existing_issues_text else []
    
    # Extract new issues
    new_issues = []
    new_start = text_data.find('<new_issues>') + len('<new_issues>')
    new_end = text_data.find('</new_issues>')
    if new_start != -1 and new_end != -1:
        new_issues_text = text_data[new_start:new_end].strip()
        new_issues = ast.literal_eval(new_issues_text) if new_issues_text else []

    return {
        "answer": answer,  # Ensure answer is a valid string
        "existing_issues": json.dumps(existing_issues),  # Convert to JSON string
        "new_issues": json.dumps(new_issues) 
    }