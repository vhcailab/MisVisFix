from .pitfalls import get_pitfalls


def generate_pitfalls_text():
    pitfalls = get_pitfalls()
    pitfalls_text = ""
    for key, value in pitfalls.items():
        pitfalls_text += f"{value['label']}: {value['description']}\n"
    return pitfalls_text


def generate_issue_text(key_issues):
    return "\n".join(key_issues)


def get_image_error_correction(generated_code, error_message):
    return [
        {
            "role": "system",
            "content": (
                # "You are an expert in Python code analysis and correction. Your goal is to identify any issues in the provided Python code, "
                # "and return a corrected version of the code that will run without errors."
                "You are an expert in Python code analysis and correction. Your goal is to identify any issues in the provided Python code, "
                "and return a corrected version of the code that will run without errors. Ensure that deprecated methods and practices "
                "are not used, and suggest alternative methods where necessary. Ensure that all required arguments for functions are included."
            )
        },
        {
            "role": "user",
            "content": (
                f"Here is the Python code that caused an error:\n\n"
                f"```python\n{generated_code}\n```\n\n"
                f"The error message received was:\n\n"
                f"```{error_message}```\n\n"
                # "Please execute the code and if is there any errors fix all of those errors."
                # "As geopandas.dataset has been deprecated. Don't use gpd.read_file."
                # "Please analyze the code, identify any issues (such as incorrect data lengths, invalid functions, etc.), "
                # "and provide a corrected version of the code that runs without errors. Modify the code as needed."
                "Please analyze the provided code, identify any errors (such as missing required arguments for functions, incorrect data handling, "
                "invalid functions, or deprecated methods), and return a corrected version. Ensure that functions like `plt annotate()` include all required arguments, "
                "and that the code does not rely on deprecated functions like `gpd.read_file()` or any method requiring external files. Modify the code to generate data internally or provide an alternative approach to avoid such dependencies. "
                "Ensure that the corrected code runs without any errors."
            )
        }
    ]


def generate_chart_prompt_for_claude(dataset, image_url, key_issues):
    pitfalls_text = generate_pitfalls_text()
    return [
        {
            "role": "system",
            "content": "You are an AI assistant tasked with analyzing and correcting misleading charts. You will be provided with information about key issues in misleading graphs, a specific misleading chart, its identified issues, and a corrected dataset. Your goal is to resolve the issues, generate a new chart, and provide the Python code for the corrected chart."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"""
                        First, review the list of all possible key issues for misleading graphs: 
                            <all_key_issues>
                                {pitfalls_text}
                            </all_key_issues>
                    """
                },
                {
                    "type": "text",
                    "text": f"""
                        Now, examine the misleading chart provided:
                        <misleading_chart>
                    """
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "detail": "high",
                        "url": image_url
                    }
                },
                {
                    "type": "text",
                    "text": f"""
                        </misleading_chart>
                    """
                },
                {
                    "type": "text",
                    "text": f"""
                        Consider the identified key issues for this specific chart:
                        <identified_key_issues>
                            f"{', '.join(key_issues)}."
                        </identified_key_issues>
                    """
                },
                {
                    "type": "text",
                    "text": f"""
                        You have been provided with a corrected dataset in CSV format:
                        <corrected_dataset>
                            {dataset}
                        </corrected_dataset>
                    """
                },
                {
                    "type": "text",
                    "text": f"""
                        To complete this task, follow these steps:
                            1. Analyze the identified key issues and think about how to resolve each one. Consider how these issues affect the chart's accuracy and clarity.
                            2. Using the corrected dataset, generate a new chart that addresses all the identified issues. Think about the most appropriate chart type, scaling, labeling, and other visual elements that will accurately represent the data.
                            3. Write Python code to create the corrected chart.
                                a) Use the predefined aliases: 'plt' for matplotlib.pyplot, 'np' for numpy, 'pd' for pandas, 'sns' for seaborn, 'mdates' for matplotlib.dates, and 'ticker' for matplotlib.ticker.
                                b) Import 'DateFormatter', 'MonthLocator', 'YearLocator', and 'DayLocator' from 'mdates', and 'MaxNLocator' from 'ticker'.
                                c) Follow Python naming conventions: use only alphanumeric characters and underscores for variable names.
                                d) Ensure the code has no syntax errors and can execute without manual intervention.
                            4. If you encounter any difficulties in interpreting the data from the original chart, prioritize using the corrected dataset provided in CSV format. This dataset contains the accurate information needed for the new chart.
                            5. After creating the initial version of the corrected chart, review it to ensure that all identified issues have been resolved and that the chart accurately represents the data.
                            6. If necessary, modify your Python code to fine-tune the chart's appearance, readability, or any other aspects that could be improved.
                            7. When using the corrected dataset, apply the corrected color codes provided in the reference image.
                            8. Ensure the data is plotted accurately in the chart while adhering to the chart's properties, such as axis scaling, marker placement, line connections, and overall visual clarity.
                            9. Ensure the data is sorted logically based on the relevant x-axis variable (e.g., date, numerical values, or categorical order) before plotting. If the x-axis represents time, sort chronologically; if it's numeric, sort in ascending order; and if it's categorical, use the natural order or specified priority.
                        
                        Error Handling:
                            1. Ensure that all variable names adhere to Python's naming conventions, meaning no special characters like '&' or '%'. 
                            2. Variable names should only contain alphanumeric characters and underscores ('_'). 
                            3. Handle module 'pandas.compat' has no attribute 'StringIO'
                            4. Handle unterminated string literal error
                            5. Handle 'Text' object has no property 'padding'
                            7. Handle 'pandas' has no attribute 'StringIO'
                        
                        You must follow the output format:
                            1. Output your complete Python code inside <python_code> tags. Ensure the code is properly formatted and indented.
                                <python_code>
                                    # Your Python code here...
                                </python_code>
                            2. Provide a brief explanation of how the new chart resolves each of the identified key issues within <explanation> tags.
                            <explanation>
                                - Clearly state how each key issue was resolved.
                                - Highlight improvements in clarity, accuracy, and visual representation.
                            </explanation>

                        Remember to think through each step carefully and ensure that your solution effectively addresses all the identified issues while accurately representing the data from the corrected dataset. Also, Ensure the code is bug-free, handles all possible errors, and is ready for dynamic execution environments.

                                 
                    """
                },
            ]
        }
    ]
