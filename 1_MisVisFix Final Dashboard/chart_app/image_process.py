import json
import os
import re
import httpx
from django.conf import settings
from django.shortcuts import render
import openai
import io
import base64
from django.http import HttpResponse, JsonResponse
import matplotlib
import pandas as pd
import uuid
import anthropic

from ..chart_app.utils.api_key_helper import get_claude_key
from .utils.secrets import decrypt_env_var
from .prompt_helper_claude import get_corrected_image_prompt_cl, get_image_error_correction_cl, \
    get_dataset_chart_generation_prompt_cl, get_dataset_from_the_chart_cl, generate_image_with_cl

from .prompt_helper import generate_chart_prompt_for_claude, \
    get_image_error_correction

matplotlib.use('Agg')

import matplotlib.pyplot as plt
from .model_helper import GPT_4o_Model

temp = 0.2

def corrected_image_process(request, selected_model, key_issues, image_url):
    client = anthropic.Anthropic(api_key=get_claude_key(request))
    response = client.messages.create(
        model=selected_model,
        max_tokens=4096,
        system="You are an AI assistant tasked with generating Python code to fix issues in a data visualization chart. Your goal is to produce robust, error-free code that addresses all identified problems and is ready for immediate execution.",
        temperature=temp,
        messages=[
            {
                "role": "user",
                "content": get_corrected_image_prompt_cl(key_issues, image_url)
            }
        ]
    )
    response_text = response.content[0].text
    try:
        code_match = re.search(r"<code>(.*?)</code>", response_text, re.DOTALL)
        if code_match:
            extracted_code = code_match.group(1).strip()
            print("Extracted Python Code:\n")
            print(extracted_code)
        else:
            raise ValueError("Error: Unable to extract Python code from the response text.")
        namespace = {}
        exec(extracted_code, namespace)
        if 'plt' in namespace:
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png')
            img_buffer.seek(0)

            # Encode the image as Base64
            img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')

            # Close the buffer and the figure
            img_buffer.close()
            plt.close()
            return JsonResponse({'image': img_base64})
        else:
            raise ValueError("Error: No plot was generated in the executed code.")
    except Exception as e:
        print(e)
        response_new = client.messages.create(
            model=selected_model,
            max_tokens=4096,
            system="You are an expert Python code analyst and debugger. Your task is to analyze a piece of Python code that has produced an error, identify the issues, and provide a corrected version of the code that will run without errors. Pay close attention to deprecated methods, missing required arguments, and any practices that may lead to runtime errors.",
            temperature=temp,
            messages=[
                {
                    "role": "user",
                    "content": get_image_error_correction_cl(extracted_code, e)
                }
            ]
        )
        response_text_new = response_new.content[0].text
        try:
            code_match_new = re.search(r"<corrected_code>(.*?)</corrected_code>", response_text_new, re.DOTALL)
            if code_match_new:
                extracted_code_new = code_match_new.group(1).strip()
                print("Extracted Python Code:\n")
                print(extracted_code_new)
            else:
                raise ValueError("Error: Unable to extract Python code from the response text.")
            namespace = {}
            exec(extracted_code_new, namespace)
            if 'plt' in namespace:
                # Save the plot to a BytesIO object
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format='png')
                img_buffer.seek(0)

                # Encode the image as Base64
                img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')

                # Close the buffer and the figure
                img_buffer.close()
                plt.close()
                return JsonResponse({'image': img_base64})
            else:
                raise ValueError("Error: No plot was generated in the executed code.")
        except Exception as e:
            print(e)


def image_process_for_dataset(request, selected_model, columns, data_sample):
    client = anthropic.Anthropic(api_key=get_claude_key(request))
    response = client.messages.create(
        model=selected_model,
        max_tokens=4096,
        system="You are an AI assistant specialized in data analysis and Python code generation for data visualization. Your task is to create Python code that visualizes a given dataset in the most appropriate way using matplotlib and seaborn libraries.",
        temperature=temp,
        messages=[
            {
                "role": "user",
                "content": get_dataset_chart_generation_prompt_cl(columns, data_sample)
            }
        ]
    )
    response_text = response.content[0].text
    try:
        code_match = re.search(r"<code>(.*?)</code>", response_text, re.DOTALL)
        if code_match:
            extracted_code = code_match.group(1).strip()
            print("Extracted Python Code:\n")
            print(extracted_code)
        else:
            raise ValueError("Error: Unable to extract Python code from the response text.")
        namespace = {}
        exec(extracted_code, namespace)
        if 'plt' in namespace:
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png')
            img_buffer.seek(0)

            # Encode the image as Base64
            img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')

            # Close the buffer and the figure
            img_buffer.close()
            plt.close()
            return JsonResponse({'image': img_base64})
        else:
            raise ValueError("Error: No plot was generated in the executed code.")
    except Exception as e:
        print(e)
        response_new = client.messages.create(
            model=selected_model,
            max_tokens=4096,
            system="You are an expert Python code analyst and debugger. Your task is to analyze a piece of Python code that has produced an error, identify the issues, and provide a corrected version of the code that will run without errors. Pay close attention to deprecated methods, missing required arguments, and any practices that may lead to runtime errors.",
            temperature=temp,
            messages=[
                {
                    "role": "user",
                    "content": get_image_error_correction_cl(extracted_code, e)
                }
            ]
        )
        response_text_new = response_new.content[0].text
        try:
            code_match_new = re.search(r"<corrected_code>(.*?)</corrected_code>", response_text_new, re.DOTALL)
            if code_match_new:
                extracted_code_new = code_match_new.group(1).strip()
                print("Extracted Python Code:\n")
                print(extracted_code_new)
            else:
                raise ValueError("Error: Unable to extract Python code from the response text.")
            namespace = {}
            exec(extracted_code_new, namespace)
            if 'plt' in namespace:
                # Save the plot to a BytesIO object
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format='png')
                img_buffer.seek(0)

                # Encode the image as Base64
                img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')

                # Close the buffer and the figure
                img_buffer.close()
                plt.close()
                return JsonResponse({'image': img_base64})
            else:
                raise ValueError("Error: No plot was generated in the executed code.")
        except Exception as e:
            print(e)


def process_to_generate_image(request, selected_model, key_issues, image_url):
    client = anthropic.Anthropic(api_key=get_claude_key(request))
    response = client.messages.create(
        model=selected_model,
        max_tokens=4096,
        system="You are tasked with analyzing a misleading chart and creating a corrected dataset based on the key issues identified.",
        temperature=temp,
        messages=[
            {
                "role": "user",
                "content": get_dataset_from_the_chart_cl(image_url, key_issues)
            }
        ]
    )
    response_text = response.content[0].text
    print(response_text)
    match = re.search(r"<corrected_dataset>(.*?)</corrected_dataset>", response_text, re.DOTALL)
    if match:
        dataset_content = match.group(1).strip()
        dataset = f"""{dataset_content}"""
        claude_image = generate_image_with_claude(request, dataset, selected_model, image_url, key_issues)
        chart_response = openai.ChatCompletion.create(
            model='gpt-4o',
            messages=generate_chart_prompt_for_claude(dataset, image_url, key_issues),
            max_tokens=16384,
            temperature=temp
        )
        generated_text = chart_response['choices'][0]['message']['content'].strip()

        python_code_match = re.search(r"<python_code>(.*?)</python_code>", generated_text, re.DOTALL)

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
            request.session['corrected_image_code'] = generated_code
            # Close the BytesIO object
            img_buffer.close()
            return JsonResponse({'image': img_base64, 'temp_image': claude_image['image']})
            # return JsonResponse({'image': img_base64})
        except Exception as e:
            print(".....GPT ERROR........")
            print(e)
            response_new = openai.ChatCompletion.create(
                model=GPT_4o_Model,
                messages=get_image_error_correction(generated_code, e),
                max_tokens=16384,
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
                request.session['corrected_image'] = img_base64_new
                request.session['corrected_image_code'] = generated_code_new
                # Close the BytesIO object
                img_buffer_new.close()
                return JsonResponse({'image': img_base64_new, 'temp_image': claude_image['image']})
            except Exception as e:
                print(f"Error during corrected code execution: {e}")

    else:
        print("Dataset not found.")


def generate_image_with_claude(request, dataset, selected_model, image_url, key_issues):
    client = anthropic.Anthropic(api_key=get_claude_key(request))
    response = client.messages.create(
        model=selected_model,
        max_tokens=4096,
        system="You are an AI assistant tasked with analyzing and correcting misleading charts. You will be provided with information about key issues in misleading graphs, a specific misleading chart, its identified issues, and a corrected dataset. Your goal is to resolve the issues, generate a new chart, and provide the Python code for the corrected chart.",
        temperature=temp,
        messages=[
            {
                "role": "user",
                "content": generate_image_with_cl(dataset, image_url, key_issues)
            }
        ]
    )

    generated_text = response.content[0].text

    python_code_match = re.search(r"<python_code>(.*?)</python_code>", generated_text, re.DOTALL)

    if python_code_match:
        python_code_content = python_code_match.group(1).strip()

        cleaned_python_code = re.sub(r"^```python|```$", "", python_code_content, flags=re.MULTILINE).strip()

        generated_code = cleaned_python_code
        print(".....Claude Code........")
        print(cleaned_python_code)
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
        request.session['corrected_image_code'] = generated_code
        # Close the BytesIO object
        img_buffer.close()
        return {
            'image': img_base64
        }
    except Exception as e:
        print(".....Claude Error........")
        print(e)

        response_new = openai.ChatCompletion.create(
            model=GPT_4o_Model,
            messages=get_image_error_correction(generated_code, e),
            max_tokens=16384,
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
            request.session['corrected_image'] = img_base64_new
            request.session['corrected_image_code'] = generated_code_new
            # Close the BytesIO object
            img_buffer_new.close()
            return {
                'image': img_base64_new
            }
        except Exception as e:
            print(f"Error during corrected code execution: {e}")
