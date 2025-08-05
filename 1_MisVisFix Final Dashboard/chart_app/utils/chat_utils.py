import os
import anthropic
import matplotlib
import openai
from django.http import JsonResponse

from ..utils.api_key_helper import get_claude_key
from ..utils.secrets import decrypt_env_var

from ..model_helper import Claude_Ai, GPT_4o_Model, Claude_Ai_Model
from ..prompt.text_chat_prompt import text_chat_gpt_prompt, text_chat_cl_prompt

temp = 0.2

matplotlib.use('Agg')


def get_chat_text_data(request, question, image):
    client = anthropic.Anthropic(api_key=get_claude_key(request))
    model = Claude_Ai_Model
    if model == Claude_Ai:
        response = client.messages.create(
            model=Claude_Ai_Model,
            max_tokens=4096,
            system="You are an expert in chart analysis. You will be provided with a chart image and a question about the chart. Your task is to analyze the image carefully and answer the question based on the information.",
            temperature=temp,
            messages=[
                {
                    "role": "user",
                    "content": text_chat_cl_prompt(question, image)
                }
            ]
        )
        response_text = response.content[0].text
        return JsonResponse({'message': response_text})
    else:
        response = openai.ChatCompletion.create(
            model=GPT_4o_Model,
            messages=text_chat_gpt_prompt(question, image),
            max_tokens=16384,
            temperature=temp
        )
        return JsonResponse({'message': response['choices'][0]['message']['content'].strip()})
