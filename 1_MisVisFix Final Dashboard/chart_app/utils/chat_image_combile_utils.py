import json
import os
import re
import anthropic
import matplotlib
import openai
from django.http import HttpResponse, JsonResponse
import io
import base64

from ..utils.secrets import decrypt_env_var

from .chat_image_claude_utils import get_chat_claude_image
from .chat_image_gpt_utils import get_chat_gpt_image

temp = 0.2

matplotlib.use('Agg')

import matplotlib.pyplot as plt


def get_chat_combine_image(request, question, message_type, key_issues):
    claude_image_response = get_chat_claude_image(request, question, 'original_claude', key_issues)
    gpt_image_response = get_chat_gpt_image(request, question, 'original_gpt', key_issues)

    # claude_response_json = json.loads(claude_image_response.content)
    # gpt_response_json = json.loads(gpt_image_response.content)

    claude_image = ''
    gpt_image = ''
    if claude_image_response and claude_image_response['image']:
        claude_image = claude_image_response['image']

    if gpt_image_response and gpt_image_response['image']:
        gpt_image = gpt_image_response['image']

    changes_made = ''
    if claude_image_response['changes_made']:
        changes_made += 'Claude Changes: \n' + claude_image_response['changes_made'] + "\n\n"

    if gpt_image_response['changes_made']:
        changes_made += 'Gpt Changes: \n' + gpt_image_response['changes_made'] + "\n"

    return {
        'claude_image': claude_image, 
        'gpt_image': gpt_image,
        'changes_made': changes_made
    }
