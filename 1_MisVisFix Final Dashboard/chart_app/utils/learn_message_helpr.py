import os
import anthropic
import matplotlib
import openai
from django.http import JsonResponse

from ..utils.secrets import decrypt_env_var

from ..prompt.learn_message_prompt import learn_message_gpt_prompt
from ..model_helper import GPT_4o_Model

temp = 0.2

matplotlib.use('Agg')


def get_learn_message(request, chat_histories):
    response = openai.ChatCompletion.create(
        model=GPT_4o_Model,
        messages=learn_message_gpt_prompt(chat_histories),
        max_tokens=16384,
        temperature=temp
    )
    return response
