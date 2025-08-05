from django.http import JsonResponse
import openai
import re

from ..prompt.misleading_decision_user_instructions_prompt import  misleading_decision_user_message_code_gpt_prompt, misleading_decision_user_message_image_gpt_prompt
from ..model_helper import GPT_4o_Model

temp = 0.2

def get_mislead_status_for_image_user_instructions(user_messgae, image):
    response = openai.ChatCompletion.create(
        messages=misleading_decision_user_message_image_gpt_prompt(image, user_messgae),
        model=GPT_4o_Model,
        temperature=temp
    )
    return parse_mislead_response(response['choices'][0]['message']['content'])


def get_mislead_status_for_code_user_instructions(user_messgae, code):
    response = openai.ChatCompletion.create(
        messages=misleading_decision_user_message_code_gpt_prompt(code, user_messgae),
        model=GPT_4o_Model,
        temperature=temp
    )
    return parse_mislead_response(response['choices'][0]['message']['content'])

def parse_mislead_response(response_text):
    # Extract <decision>
    decision_match = re.search(r"<decision>\s*(true|false)\s*</decision>", response_text, re.IGNORECASE)
    decision = decision_match.group(1).strip().lower() == 'true' if decision_match else False

    # Extract <reason> as plain text
    reason_match = re.search(r"<reason>(.*?)</reason>", response_text, re.DOTALL | re.IGNORECASE)
    reason = reason_match.group(1).strip() if reason_match else ""
    print(decision)
    print(reason)
    return JsonResponse({
        "decision": decision,
        "reason": reason
    })