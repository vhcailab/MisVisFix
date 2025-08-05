from ..image_conversion_helper import get_image_type_from_url, image_url_to_base64
from ..pitfalls import get_pitfalls


def generate_pitfalls_text():
    pitfalls = get_pitfalls()
    pitfalls_text = ""
    for key, value in pitfalls.items():
        pitfalls_text += f"{value['label']}: {value['description']}\n"
    return pitfalls_text


def generate_chart_gpt_prompt(dataset, image_url, key_issues):
    pitfalls_text = generate_pitfalls_text()
    return [
        {
            "role": "system",
            "content": "You are an AI assistant tasked with analyzing and correcting misleading charts. You will be provided with information about key issues in misleading graphs, a specific misleading chart, its identified issues, and a corrected dataset. Your goal is to resolve the issues, generate a new chart, and provide Python code for the corrected chart."
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
                        Examine the misleading chart provided below:
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
                        Identified key issues for this specific chart:
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
                            8. Ensure the generated chart is not misleading.

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

                             3. List which identified key issues have been successfully resolved in the generated chart.
                                <solved_issues>
                                    ["issue_1", "issue_2", "issue_3", ...]
                                </solved_issues>

                        Remember to think through each step carefully and ensure that your solution effectively addresses all the identified issues while accurately representing the data from the corrected dataset. Also, Ensure the code is bug-free, handles all possible errors, and is ready for dynamic execution environments.
                    """
                },
            ]
        }
    ]


def generate_chart_cl_prompt(dataset, image, key_issues):
    pitfalls_text = generate_pitfalls_text()
    return [
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
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": f"image/{get_image_type_from_url(image)}",
                "data": image_url_to_base64(image)
            },
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
                            4. If you need to use 'seaborn' style then use 'seaborn-v0_8'.
                            5. If you encounter any difficulties in interpreting the data from the original chart, prioritize using the corrected dataset provided in CSV format. This dataset contains the accurate information needed for the new chart.
                            6. After creating the initial version of the corrected chart, review it to ensure that all identified issues have been resolved and that the chart accurately represents the data.
                            7. If necessary, modify your Python code to fine-tune the chart's appearance, readability, or any other aspects that could be improved.
                            8. Present your final Python code for the corrected chart within <python_code> tags. Include comments explaining key parts of the code and how it addresses the previously identified issues.
                            9. Provide a brief explanation of how the new chart resolves each of the identified key issues within <explanation> tags.
                            10. Ensure the data is plotted accurately in the chart while adhering to the chart's properties, such as axis scaling, marker placement, line connections, and overall visual clarity.
                            11. Ensure the data is sorted logically based on the relevant x-axis variable (e.g., date, numerical values, or categorical order) before plotting. If the x-axis represents time, sort chronologically; if it's numeric, sort in ascending order; and if it's categorical, use the natural order or specified priority.
                            12. Parse the `Date` column as a time series using `pd.to_datetime` and sort the data chronologically.
                            13. Select the appropriate chart type based on the data and the following criteria. For example: 
                                a) Use **bar charts** for categorical comparisons (e.g., comparing case counts between counties).
                                b) Use **line charts** for chronological trends (e.g., changes in case counts over time).
                                c) Use **stacked bar charts** or **area charts** to show cumulative trends or proportions.
                            14. Ensure the x-axis (Date) is properly formatted for readability using `DateFormatter` and rotated if needed.
                            15. Apply clear labels for the x-axis, y-axis, title, and legend to ensure readability and interpretability.
                            16. Avoid misleading elements, such as uneven intervals, inconsistent scaling, or confusing markers.

                        Error Handling:
                            1. Ensure that all variable names adhere to Python's naming conventions, meaning no special characters like '&' or '%'. 
                            2. Variable names should only contain alphanumeric characters and underscores ('_'). 
                            4. Handle unterminated string literal error
                            5. Handle 'Text' object has no property 'padding'
                            6. Ensure that the code works directly with the provided dataset, which has tagged with <corrected_dataset>. there is no file path. use direct dataset which has provided.
                            7. 'pandas' has no attribute 'StringIO'


                         Your response should follow the format below:

                            1. Output your complete Python code inside <python_code> tags. Ensure the code is properly formatted and indented.
                            <python_code>
                                # Your Python code here...
                            </python_code>

                            2. Provide a brief explanation of how the new chart resolves each of the identified key issues within <explanation> tags.
                            <explanation>
                                - Clearly state how each key issue was resolved.
                                - Highlight improvements in clarity, accuracy, and visual representation.
                            </explanation>

                            3. List which identified key issues have been successfully resolved in the generated chart.
                            <solved_issues>
                                ["Issue_1", "Issue_2", "Issue_3", ...]
                            </solved_issues>

                            Ensure that:
                                - The `<solved_issues>` section provides a **JSON-style array** that can be easily parsed.
                                - If an issue remains unresolved, do not include it in `<solved_issues>`.
                                - The explanation is clear and concise, addressing all changes made.

                        Remember to think through each step carefully and ensure that your solution effectively addresses all the identified issues while accurately representing the data from the corrected dataset. Also, Ensure the code is bug-free, handles all possible errors, and is ready for dynamic execution environments.

                    """
        },
    ]
