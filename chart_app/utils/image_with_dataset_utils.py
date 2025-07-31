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
from ..model_helper import CLAUDE_TOKEN, GPT_TOKEN, Claude_Ai, Claude_Ai_Model, GPT_4o, GPT_4o_Model
from ..prompt.dataset_image_prompt import dataset_image_gpt_prompt, dataset_image_cl_prompt
from ..prompt_helper import get_image_error_correction
from ..utils.session_helper import save_session

temp = 0.2

matplotlib.use('Agg')

import matplotlib.pyplot as plt


def get_image_for_dataset(request, dataset):
    original_image_url = request.session.get('firebase_image_url', '')
    key_issues = request.session.get('key_issues', '')
    client = anthropic.Anthropic(api_key=get_claude_key(request))

    response = client.messages.create(
            model=Claude_Ai_Model,
            max_tokens=CLAUDE_TOKEN,
            system="You are an AI assistant tasked with analyzing misleading charts and generating Python code to create corrected versions based on provided datasets and key issues. Your goal is to ensure that the new chart accurately represents the data and resolves all identified issues.",
            temperature=temp,
            messages=[
                {
                    "role": "user",
                    "content": dataset_image_cl_prompt(original_image_url, dataset, key_issues)
                }
            ]
        )
    generated_text = response.content[0].text
    claude_image = None
    python_code_match = re.search(r"<python_code>(.*?)</python_code>", generated_text, re.DOTALL)
    if python_code_match:
        python_code_content = python_code_match.group(1).strip()
        cleaned_python_code = re.sub(r"^```python|```$", "", python_code_content, flags=re.MULTILINE).strip()
        generated_code = cleaned_python_code
        claude_image = get_image(request, generated_code, Claude_Ai)
        
    response = openai.ChatCompletion.create(
        model=GPT_4o_Model,
        messages=dataset_image_gpt_prompt(original_image_url, dataset, key_issues),
        max_tokens=GPT_TOKEN,
        temperature=temp
    )
    generated_text = response['choices'][0]['message']['content'].strip()
    gpt_image = None
    python_code_match = re.search(r"<python_code>(.*?)</python_code>", generated_text, re.DOTALL)
    if python_code_match:
        python_code_content = python_code_match.group(1).strip()
        cleaned_python_code = re.sub(r"^```python|```$", "", python_code_content, flags=re.MULTILINE).strip()
        generated_code = cleaned_python_code
        gpt_image = get_image(request, generated_code, GPT_4o)

    return {
        'gpt_image': gpt_image['image'] if gpt_image else None,
        'claude_image': claude_image['image'] if claude_image else None
    }


def get_image(request, generated_code, model):
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

        if model == Claude_Ai:
            save_session(request, 'corrected_claude_image_code', generated_code)
        else:
            save_session(request, 'corrected_gpt_image_code', generated_code)
        # Close the BytesIO object
        img_buffer.close()
        return {
            'image': img_base64, 
            'model': model
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
            print(generated_text_new)
            return HttpResponse("Error: Unable to extract Python code from the response.")

        # Print the generated code for debugging
        print("Generated New Python Code:\n")
        print(generated_code_new)

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
            if model == Claude_Ai:
                save_session(request, 'corrected_claude_image_code', generated_code_new)
            else:
                save_session(request, 'corrected_gpt_image_code', generated_code_new)
            # Close the BytesIO object
            img_buffer_new.close()
            return {
                'image': img_base64_new, 
                'model': model
            }
        except Exception as e:
            print(f"Error during corrected code execution: {e}")
            return {
                'error': "Something went wrong with the corrected code as well."
            }
