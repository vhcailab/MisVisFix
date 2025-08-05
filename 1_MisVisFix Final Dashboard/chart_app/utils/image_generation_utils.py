import json
import os
import re
import anthropic
import matplotlib
import openai
from django.http import HttpResponse
import io
import base64

from ..utils.api_key_helper import get_claude_key
from ..utils.secrets import decrypt_env_var

from .session_helper import save_session, get_session
from ..model_helper import CLAUDE_TOKEN, GPT_TOKEN, Claude_Ai_Model, GPT_4o_Model
from ..prompt.amended_image_prompt import generate_chart_gpt_prompt, generate_chart_cl_prompt
from ..prompt.image_correction_prompt import image_error_correction_gpt_prompt, image_error_correction_cl_prompt
from ..prompt.retrieve_dataset_prompt import retrieve_dataset_cl_prompt, retrieve_dataset_gpt_prompt

temp = 0.2

matplotlib.use('Agg')

import matplotlib.pyplot as plt


def get_dataset(request, selected_model, key_issues, image_url):
    client = anthropic.Anthropic(api_key=get_claude_key(request))
    if selected_model == Claude_Ai_Model:
        response = client.messages.create(
            model=selected_model,
            max_tokens=CLAUDE_TOKEN,
            system="You are tasked with analyzing a misleading chart and creating a corrected dataset based on the key issues identified.",
            temperature=temp,
            messages=[
                {
                    "role": "user",
                    "content": retrieve_dataset_cl_prompt(image_url, key_issues)
                }
            ]
        )
        response_text = response.content[0].text
        match = re.search(r"<corrected_dataset>(.*?)</corrected_dataset>", response_text, re.DOTALL)
        if match:
            dataset_content = match.group(1).strip()
            dataset = f"""{dataset_content}"""
            print("Claude")
            print(dataset)
            return dataset
        else:
            return None
    else:
        chart_response = openai.ChatCompletion.create(
            model='gpt-4o',
            messages=retrieve_dataset_gpt_prompt(image_url, key_issues),
            max_tokens=GPT_TOKEN,
            temperature=temp
        )
        generated_text = chart_response['choices'][0]['message']['content'].strip()
        match = re.search(r"<corrected_dataset>(.*?)</corrected_dataset>", generated_text, re.DOTALL)
        if match:
            dataset_content = match.group(1).strip()
            dataset = f"""{dataset_content}"""
            print("Gpt")
            print(dataset)
            return dataset
        else:
            return None


def get_gpt_image(request, dataset, image_url, key_issues):
    chart_response = openai.ChatCompletion.create(
        model=GPT_4o_Model,
        messages=generate_chart_gpt_prompt(dataset, image_url, key_issues),
        max_tokens=GPT_TOKEN,
        temperature=temp
    )

    generated_text = chart_response['choices'][0]['message']['content'].strip()
    print(generated_text)
    python_code_match = re.search(r"<python_code>(.*?)</python_code>", generated_text, re.DOTALL)
    solved_issues_match = re.search(r"<solved_issues>\s*(\[[^\]]+\])\s*</solved_issues>", generated_text)
    solved_issues_list = json.loads(solved_issues_match.group(1)) if solved_issues_match else []

    # If no match, fall back to triple backticks (```python ... ```)
    if not python_code_match:
        python_code_match = re.search(r"```python(.*?)```", generated_text, re.DOTALL)

    # Extract and clean Python code
    if python_code_match:
        python_code_content = python_code_match.group(1).strip()
        cleaned_python_code = re.sub(r"^```python|```$", "", python_code_content, flags=re.MULTILINE).strip()
        generated_code = cleaned_python_code
        print("-----GPT Code-----")
        print(generated_code)
    else:
        print("No Python code found.")
        return HttpResponse("Error: Unable to extract Python code from the response.")
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
        save_session(request, 'corrected_gpt_image', img_base64)
        save_session(request, 'corrected_gpt_image_code', generated_code)
        # Close the BytesIO object
        img_buffer.close()
        return {
            'image': img_base64,
            'solved_list': solved_issues_list
        }
    except Exception as e:
        print(".....GPT ERROR........")
        print(e)
        response_new = openai.ChatCompletion.create(
            model=GPT_4o_Model,
            messages=image_error_correction_gpt_prompt(generated_code, e),
            max_tokens=GPT_TOKEN,
            temperature=temp
        )
        generated_text_new = response_new['choices'][0]['message']['content'].strip()
        print(generated_text_new)
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
            save_session(request, 'corrected_gpt_image', img_base64_new)
            save_session(request, 'corrected_gpt_image_code', generated_code_new)
            # Close the BytesIO object
            img_buffer_new.close()
            return {
                'image': img_base64_new,
                'solved_list': solved_issues_list
            }
        except Exception as e:
            print(f"Error during corrected code execution: {e}")


def get_claude_image(request, dataset, image_url, key_issues):
    client = anthropic.Anthropic(api_key=get_claude_key(request))
    response = client.messages.create(
        model=Claude_Ai_Model,
        max_tokens=CLAUDE_TOKEN,
        system="You are an AI assistant tasked with analyzing and correcting misleading charts. You will be provided with information about key issues in misleading graphs, a specific misleading chart, its identified issues, and a corrected dataset. Your goal is to resolve the issues, generate a new chart, and provide the Python code for the corrected chart.",
        temperature=temp,
        messages=[
            {
                "role": "user",
                "content": generate_chart_cl_prompt(dataset, image_url, key_issues)
            }
        ]
    )

    generated_text = response.content[0].text
    print(generated_text)

    python_code_match = re.search(r"<python_code>(.*?)</python_code>", generated_text, re.DOTALL)
    solved_issues_match = re.search(r"<solved_issues>\s*(\[[^\]]+\])\s*</solved_issues>", generated_text)
    solved_issues_list = json.loads(solved_issues_match.group(1)) if solved_issues_match else []

    if python_code_match:
        python_code_content = python_code_match.group(1).strip()

        cleaned_python_code = re.sub(r"^```python|```$", "", python_code_content, flags=re.MULTILINE).strip()

        generated_code = cleaned_python_code
    else:
        return HttpResponse("Error: Unable to extract Python code from the response.")

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
        save_session(request, 'corrected_claude_image', img_base64)
        save_session(request, 'corrected_claude_image_code', generated_code)
        # Close the BytesIO object
        img_buffer.close()
        return {
            'image': img_base64,
            'solved_list': solved_issues_list
        }
    except Exception as e:
        print(".....Claude Error........")
        print(e)

        response_new = openai.ChatCompletion.create(
            model=GPT_4o_Model,
            messages=image_error_correction_gpt_prompt(generated_code, e),
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
            save_session(request, 'corrected_claude_image', img_base64_new)
            save_session(request, 'corrected_claude_image_code', generated_code_new)
            # Close the BytesIO object
            img_buffer_new.close()
            return {
                'image': img_base64_new,
                'solved_list': solved_issues_list
            }
        except Exception as e:
            print(f"Error during corrected code execution: {e}")
