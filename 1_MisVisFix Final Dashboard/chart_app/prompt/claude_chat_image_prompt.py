from ..image_conversion_helper import get_image_type_from_url, image_url_to_base64
from ..pitfalls import get_pitfalls


def generate_pitfalls_text():
    pitfalls = get_pitfalls()
    pitfalls_text = ""
    for key, value in pitfalls.items():
        pitfalls_text += f"{value['label']}: {value['description']}\n"
    return pitfalls_text


def chat_latest_image_cl_prompt(question, python_code):
    return [
        {
            "type": "text",
            "text": f"""
            1. You will be provided with Python code in the following format:
                <python_code>
                    {python_code}
                </python_code>
            """
        },
        {
            "type": "text",
            "text": f"""
            2. You will also receive a modification request:
                <modification_request>
                    {question}
                </modification_request>
            """
        },
        {
            "type": "text",
            "text": f"""
            3. You must strictly use the following predefined aliases in the generated code:
               - 'plt' for matplotlib.pyplot
               - 'np' for numpy
               - 'pd' for pandas
               - 'mdates' for matplotlib.dates
               - 'ticker' for matplotlib.ticker
               - 'sns' for seaborn
            
            Ensure that 'YearLocator', 'MonthLocator', 'DayLocator', and 'DateFormatter' are referenced from 'mdates' (not 'ticker'), and 'MaxNLocator' is referenced from 'ticker'. Any other necessary components from these libraries must be referenced using their respective aliases.

            """
        },
        {
            "type": "text",
            "text": f"""
            4. Adhere to the following guidelines:
               - Ensure all variable names follow Python's naming conventions (alphanumeric characters and underscores only, no special characters like '&' or '%').
               - Make sure the generated code has no syntax errors and runs correctly.
            """
        },
        {
            "type": "text",
            "text": f"""
                5. The code should be flexible and able to handle different chart types (e.g., line charts, bar charts, scatter plots, pie charts). When working with legends, labels, or similar elements that return multiple values, ensure the code properly unpacks and concatenates these values without causing 'too many values to unpack' errors. The code should dynamically handle multi-axes plots (such as dual y-axes) and ensure legends are created for all relevant elements.
                6. Implement checks to ensure all arrays (e.g., data columns) have the same length to avoid issues like 'All arrays must be of the same length'. If a mismatch is detected, the code should either automatically fix it (e.g., by trimming the data) or raise a clear and informative error message.            
                7. The code should be capable of handling various types of issues, including but not limited to missing data, incorrect data types, mismatched array lengths, improper axis scaling, and any other problems that might arise during execution. If an issue is detected, the code should either automatically correct it or provide a fallback approach (e.g., skipping problematic data points or using default values) to ensure the graph is generated without errors.
                8. In all cases, ensure that the final plot is accurate, clearly labeled, and free of any misleading elements. If data is missing or inconsistent, provide a warning and continue generating the chart without throwing an error.
                9. Make sure not to change anything other than the specified modification.
                10. Your response should contain only the modified Python code block, without any explanations or additional text. Enclose the entire code block within <modified_code> tags.
                11. After the modified code, include a summary of what was changed compared to the original code, enclosed within <changes_made> tags. Be concise and specific (e.g., variable renamed, plot type changed, error handling added, axis formatting corrected, etc.).
            """
        },
        {
            "type": "text",
            "text": "Begin your modification process now, and provide the modified code as instructed."
        }
    ]


def chat_original_image_cl_prompt(question, image, dataset, key_issues):
    pitfalls_text = generate_pitfalls_text()

    return [
        # {
        #     "type": "text",
        #     "text": f"""
        #         First, review the list of all possible key issues for misleading graphs: 
        #             <all_key_issues>
        #                 {pitfalls_text}
        #             </all_key_issues>
        #     """
        # },
        {
            "type": "text",
            "text": "Examine the misleading chart provided: "
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
                Consider the identified key issues for this specific chart:
                <identified_key_issues>
                    f"{', '.join(key_issues)}."
                </identified_key_issues>
            """
        },
        {
            "type": "text",
            "text": f"""
                    You have been provided with the dataset of the uploaded chart in CSV format:
                    <corrected_dataset>
                        {dataset}
                    </corrected_dataset>
            """
        },
        {
            "type": "text",
            "text": f"""
                The user has submitted the following query regarding changes to the original image:
                <user_query>
                    {question}
                </user_query>
        """
        },
        {
            "type": "text",
            "text": f"""
                To complete this task, follow these steps:
                
                1. Analyze the user's query and how it relates to the identified key issues and the corrected dataset.
                2. Determine the appropriate changes needed to address both the user's query and the identified issues.
                3. Unless user query is related to change the data, please use the provided data set.
                4. Write Python code to create the corrected chart that addresses the user's query and resolves the identified issues. Follow these guidelines:
                   a) Use the predefined aliases: 'plt' for matplotlib.pyplot, 'np' for numpy, 'pd' for pandas, 'sns' for seaborn, 'mdates' for matplotlib.dates, and 'ticker' for matplotlib.ticker.
                   b) Import 'DateFormatter', 'MonthLocator', 'YearLocator', and 'DayLocator' from 'mdates', and 'MaxNLocator' from 'ticker'.
                   c) Follow Python naming conventions: use only alphanumeric characters and underscores for variable names.
                   d) Ensure the code has no syntax errors and can execute without manual intervention.
                   e) If you need to use 'seaborn' style, use 'seaborn-v0_8'.
                   f) Prioritize using the corrected dataset provided in CSV format.
                   g) Parse the `Date` column as a time series using `pd.to_datetime` and sort the data chronologically.
                   h) Select the appropriate chart type based on the data and the user's query.
                   i) Ensure the x-axis (Date) is properly formatted for readability using `DateFormatter` and rotated if needed.
                   j) Apply clear labels for the x-axis, y-axis, title, and legend to ensure readability and interpretability.
                   k) Avoid misleading elements, such as uneven intervals, inconsistent scaling, or confusing markers.

            """
        },
        {
            "type": "text",
            "text": f"""
                4. After creating the initial version of the corrected chart, review it to ensure that all identified issues have been resolved, the user's query has been addressed, and the chart accurately represents the data.
                5. If necessary, modify your Python code to fine-tune the chart's appearance, readability, or any other aspects that could be improved.
                
                Present your response in the following format:
                
                1. Provide a brief analysis of the user's query and how it relates to the identified issues within <query_analysis> tags.
                2. Present your final Python code for the corrected chart within <python_code> tags. Include comments explaining key parts of the code and how it addresses the previously identified issues and the user's query.
                3. Provide a brief explanation of how the new chart resolves each of the identified key issues and addresses the user's query within <explanation> tags.
                4. Provide a concise summary of the modifications made to the original chart — such as chart type changes, axis corrections, formatting updates, or removed misleading elements — within <changes_made> tags.

                Remember to think through each step carefully and ensure that your solution effectively addresses all the identified issues and the user's query while accurately representing the data from the corrected dataset. Also, ensure the code is bug-free, handles all possible errors, and is ready for dynamic execution environments.
            """
        },
    ]
