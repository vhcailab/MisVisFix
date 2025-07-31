from ..image_conversion_helper import get_image_type_from_url, image_url_to_base64
from ..pitfalls import get_pitfalls


def generate_pitfalls_text():
    pitfalls = get_pitfalls()
    pitfalls_text = ""
    for key, value in pitfalls.items():
        pitfalls_text += f"{value['label']}: {value['description']}\n"
    return pitfalls_text


def dataset_image_gpt_prompt(image, dataset, key_issues):
    pitfalls_text = generate_pitfalls_text()
    return [
        {
            "role": "system",
            "content": "You are an AI assistant tasked with analyzing misleading charts and generating Python code to create corrected versions based on provided datasets and key issues. Your goal is to ensure that the new chart accurately represents the data and resolves all identified issues."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"""
                            First, review the list of all possible key issues for misleading graphs: {pitfalls_text}
                        """
                },
                {
                    "type": "text",
                    "text": "Review the identified key issues for the misleading chart:"
                },
                {
                    "type": "text",
                    "text": f"{', '.join(key_issues)}"
                },
                {
                    "type": "text",
                    "text": "Examine the provided misleading chart:"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "detail": "high",
                        "url": image
                    }
                },
                {
                    "type": "text",
                    "text": "Here is the corrected dataset in CSV format:"
                },
                {
                    "type": "text",
                    "text": f"{dataset}"
                },
                {
                    "type": "text",
                    "text": "Generate Python code that creates a corrected chart using the provided dataset and resolves all the identified key issues. Follow these steps:"
                },
                {
                    "type": "text",
                    "text": """
                    1. Analyze the key issues to identify how they affect the accuracy and interpretation of the original chart.
                    2. Use the corrected dataset to create an accurate representation of the data.
                    3. Write Python code to generate the corrected chart. Ensure the code adheres to the following guidelines:
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
                        
                        Remember to think through each step carefully and ensure that your solution effectively addresses all the identified issues and the user's query while accurately representing the data from the corrected dataset. Also, ensure the code is bug-free, handles all possible errors, and is ready for dynamic execution environments.
                    """
                },
            ]
        }
    ]


def dataset_image_cl_prompt(image, dataset, key_issues):
    pitfalls_text = generate_pitfalls_text()
    return [
        {
            "type": "text",
            "text": f"""
                First, review the list of all possible key issues for misleading graphs: {pitfalls_text}
            """
        },
        {
            "type": "text",
            "text": "Review the identified key issues for the misleading chart:"
        },
        {
            "type": "text",
            "text": f"{', '.join(key_issues)}"
        },
        {
            "type": "text",
            "text": "Examine the provided misleading chart:"
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
            "text": "Here is the corrected dataset in CSV format:"
        },
        {
            "type": "text",
            "text": f"{dataset}"
        },
        {
            "type": "text",
            "text": "Generate Python code that creates a corrected chart using the provided dataset and resolves all the identified key issues. Follow these steps:"
        },
        {
            "type": "text",
            "text": """
                    1. Analyze the key issues to identify how they affect the accuracy and interpretation of the original chart.
                    2. Use the corrected dataset to create an accurate representation of the data.
                    3. Write Python code to generate the corrected chart. Ensure the code adheres to the following guidelines:
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

                        Remember to think through each step carefully and ensure that your solution effectively addresses all the identified issues and the user's query while accurately representing the data from the corrected dataset. Also, ensure the code is bug-free, handles all possible errors, and is ready for dynamic execution environments.
                    """
        },
    ]
