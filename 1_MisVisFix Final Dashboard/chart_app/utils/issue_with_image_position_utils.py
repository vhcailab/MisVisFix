import json
import os
import time

from ..utils.api_key_helper import get_claude_key
from ..prompt.key_issues_position_prompt import key_issues_position_cl_prompt, key_issues_position_gpt_prompt
from ..utils.secrets import decrypt_env_var
from ..model_helper import CLAUDE_TOKEN, GPT_TOKEN, Claude_Ai_Model, GPT_4o_Model
import anthropic
import openai

temp = 0.2

MAX_RETRIES = 5
RETRY_DELAY = 3  # seconds

def get_claude_key_issues_with_image_position(request, key_issues, width, height):
    client = anthropic.Anthropic(api_key=get_claude_key(request))
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            actual_box_width = int(((int(width) - 20) / 3))
            actual_box_height = int(((int(height) - 50) * .5) - 40)

            print("Actual Box Claude Width: " + str(actual_box_width))
            print("Actual Box Claude Height: " + str(actual_box_height))

            image_url = request.session.get('firebase_image_url', '')
            response = client.messages.create(
                model=Claude_Ai_Model,
                max_tokens=CLAUDE_TOKEN,
                system="You are an expert in chart analysis. Your task is to accurately plot key issues on a misleading chart image and provide a list of objects with specific properties for each issue.",
                temperature=temp,
                messages=[
                    {
                        "role": "user",
                        "content": key_issues_position_cl_prompt(image_url, key_issues, actual_box_width, actual_box_height)
                    }
                ]
            )
            issues_list_pos = response.content[0].text
            print(issues_list_pos)
            cleaned_temp = issues_list_pos.strip('```json').strip('```').strip()
            issues_list = json.loads(cleaned_temp)
            return issues_list
        except Exception as e:
            print(f"Claude Attempt {attempt + 1} failed: {e}")
            attempt += 1
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                print(e)
                raise RuntimeError("All retry attempts failed.") from e

    

def get_gpt_key_issues_with_image_position(request, key_issues, width, height):
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            actual_box_width = int(((int(width) - 20) / 3))
            actual_box_height = int(((int(height) - 50) * .5) - 40)

            print("Actual Box GPT Width: " + str(actual_box_width))
            print("Actual Box GPT Height: " + str(actual_box_height))

            image_url = request.session.get('firebase_image_url', '')
            response_list = openai.ChatCompletion.create(
                messages=key_issues_position_gpt_prompt(image_url, key_issues, actual_box_width, actual_box_height),
                model=GPT_4o_Model,
                max_tokens=GPT_TOKEN,
                temperature=temp
            )
            issues_list_pos = response_list['choices'][0]['message']['content'].strip()
            cleaned_temp = issues_list_pos.strip('```json').strip('```').strip()
            issues_list = json.loads(cleaned_temp)

            return issues_list
        except Exception as e:
            print(e)
            print(f"Claude Attempt {attempt + 1} failed: {e}")
            attempt += 1
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                raise RuntimeError("All retry attempts failed.") from e
