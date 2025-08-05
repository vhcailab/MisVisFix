from ..pitfalls import get_pitfalls
from ..image_conversion_helper import image_url_to_base64, get_image_type_from_url


def generate_pitfalls_text():
    pitfalls = get_pitfalls()
    pitfalls_text = ""
    for key, value in pitfalls.items():
        pitfalls_text += f"{value['label']}: {value['description']}\n"
    return pitfalls_text


def key_issues_cl_prompt(image):
    pitfalls_text = generate_pitfalls_text()
    example_image_data = "https://firebasestorage.googleapis.com/v0/b/chartinsight-3f620.appspot.com/o/imagesimg-10.jpeg?alt=media&token=0b39a841-ada1-4a69-9bcf-b658dbc30446"
    return [
        {
            "type": "text",
            "text": "First, review the following checklist of common pitfalls in data visualization: "
        },
        {
            "type": "text",
            "text": f"""
                <pitfalls_checklist>
                    {pitfalls_text}
                </pitfalls_checklist>
            """
        },
        {
            "type": "text",
            "text": "Now, you will analyze the provided chart image and identify which pitfalls it falls into. Please carefully consider all listed pitfalls and ensure to include every possible pitfall explicitly present in the chart."
        },
        {
            "type": "text",
            "text": "Carefully examine the provided chart to determine if any of the mentioned pitfalls exist. Focus on identifying issues that could mislead viewers or significantly hinder the interpretation of the data. Please note that you don't need to analysis any issues that are not present in the provided pitfalls."
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
            "text": """
                To analyze the chart:
                    1. Examine all elements of the chart, including axes, labels, colors, data representation, and overall design.
                    2. Compare each element to the pitfalls in the checklist.
                    3. For each identified pitfall, determine its severity category:
                        - Major: Issues that severely undermine the integrity and trustworthiness of the data representation.
                        - Minor: Problems that reduce the chart's clarity, usability, or accessibility, but don't necessarily invalidate the data itself.
                        - Potential: Issues that may introduce bias or misleading impressions, but require more context to determine their severity.
                    4. Provide a detailed explanation for each pitfall, specifying why it belongs to that category and how it affects the chart's interpretation.
                    5. Suggest improvements for each identified issue.
            """
        },
        {
            "type": "text",
            "text": "Present your analysis in the following JSON format: "
        },
        {
            "type": "text",
            "text": f"""
                ```json
                {[
                {
                    "id": "1",
                    "title": "Issue 1",
                    "severity": "major",
                    "details": "Details about issue 1.",
                    "improvement": "Suggestions for improving issue 1."
                },
                {
                    "id": "2",
                    "title": "Issue 2",
                    "severity": "minor",
                    "details": "Details about issue 2.",
                    "improvement": "Suggestions for improving issue 2."
                },
                {
                    "id": "3",
                    "title": "Issue 3",
                    "severity": "potential",
                    "details": "Details about issue 3.",
                    "improvement": "Suggestions for improving issue 3."
                }
            ]}
                ```
            """
        },
        {
            "type": "text",
            "text": f"""Ensure that the response is always valid JSON with double quotes (") instead of single quotes (')."""
        },
        {
            "type": "text",
            "text": f"""
                <example>
                   Here is an example:
                """
        },
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": f"image/{get_image_type_from_url(example_image_data)}",
                "data": image_url_to_base64(example_image_data)
            },
        },
        {
            "type": "text",
            "text": "Here is the output of the example image: "
        },
        {
            "type": "text",
            "text": f"""
                    ```json
                        {[
                {
                    "id": "1",
                    "title": "Truncated Axis",
                    "severity": "major",
                    "details": "The bar chart does not start the vertical axis at zero, exaggerating the difference between 45% and 43%. This visually distorts the comparison and misrepresents the actual gap.",
                    "improvement": "Adjust the axis to start at zero to accurately represent the percentage values and ensure proportionality in the bar lengths."
                },
                {
                    "id": "2",
                    "title": "Misrepresentation",
                    "severity": "major",
                    "details": "The difference between the two percentages (45% vs. 43%) is relatively small but is visually amplified by the design of the bars and the lack of a clear baseline.",
                    "improvement": "Ensure that the length of the bars directly corresponds to the percentage values without artificial amplification."
                },
                {
                    "id": "3",
                    "title": "Violating Color Convention",
                    "severity": "minor",
                    "details": "The use of red for one candidate and blue for the other follows a U.S. political convention but might not be meaningful without clarification in the context of the visualization.",
                    "improvement": "Provide a clear legend or annotation explaining the choice of colors to avoid confusion."
                },
                {
                    "id": "4",
                    "title": "Misleading Title",
                    "severity": "potential",
                    "details": "The title does not clearly state that this is polling data and may give the impression that these are final results or definitive outcomes.",
                    "improvement": "Modify the title to indicate that the chart represents polling results and specify the context, such as the date or methodology of the poll."
                },
                {
                    "id": "5",
                    "title": "Distractive Value Labels",
                    "severity": "minor",
                    "details": "The large text size of the percentage labels (45% and 43%) draws disproportionate attention and may bias viewers toward focusing on the numbers without context.",
                    "improvement": "Reduce the size of the percentage labels or include additional explanatory context to balance the visual impact."
                },
            ]}
                    ```    
                </example>
            """
        },
        {
            "type": "text",
            "text": "Remember to think step-by-step and consider all aspects of the chart before providing your final analysis. Ensure that each identified issue corresponds to a specific pitfall from the provided checklist."
        },
        {
            "type": "text",
            "text": "Your response should be a valid JSON array containing objects for each identified issue, or an empty array if no issues are found. Do not include any additional text or explanations outside of the JSON structure."
        },
    ]


def key_issues_gpt_prompt(image):
    pitfalls_text = generate_pitfalls_text()
    example_image_data = "https://firebasestorage.googleapis.com/v0/b/chartinsight-3f620.appspot.com/o/imagesimg-10.jpeg?alt=media&token=0b39a841-ada1-4a69-9bcf-b658dbc30446"
    return [
        {
            "role": "system",
            "content": "You are an AI assistant tasked with analyzing data visualization charts for potential pitfalls and issues. You will be provided with a checklist of common pitfalls in data visualization and an image of a chart to analyze. Your goal is to identify any issues present in the chart and provide a detailed analysis."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "First, review the following checklist of common pitfalls in data visualization: "
                },
                {
                    "type": "text",
                    "text": f"""
                            {pitfalls_text}
                    """
                },
                {
                    "type": "text",
                    "text": "Now, you will analyze the provided chart image and identify which pitfalls it falls into. Please carefully consider all listed pitfalls and ensure to include every possible pitfall explicitly present in the chart."
                },
                {
                    "type": "text",
                    "text": "Carefully examine the provided chart to determine if any of the mentioned pitfalls exist. Focus on identifying issues that could mislead viewers or significantly hinder the interpretation of the data. Please note that you don't need to analysis any issues that are not present in the provided pitfalls."
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
                    "text": """
                        To analyze the chart:
                            1. Examine all elements of the chart, including axes, labels, colors, data representation, and overall design.
                            2. Compare each element to the pitfalls in the checklist.
                            3. For each identified pitfall, determine its severity category:
                                - Major: Issues that severely undermine the integrity and trustworthiness of the data representation, such as misrepresenting the underlying data or using visualizations in inappropriate ways.
                                - Minor: Problems that reduce the chart's clarity, usability or accessibility, but don't necessarily invalidate the data itself.
                                - Potential: Issues that may introduce bias or misleading impressions, but require more context to determine their severity.
                            4. Provide a detailed explanation for each pitfall, specifying why it belongs to that category and how it affects the chart's interpretation.
                            5. Suggest improvements for each identified issue.
                    """
                },
                {
                    "type": "text",
                    "text": "Present your analysis in the following JSON format: "
                },
                {
                    "type": "text",
                    "text": """
                        [
                            {
                                "id": "1",
                                "title": "Issue 1",
                                "severity": "major",
                                "details": "Details about issue 1.",
                                "improvement": "Suggestions for improving issue 1."
                            },
                            {
                                "id": "2",
                                "title": "Issue 2",
                                "severity": "minor",
                                "details": "Details about issue 2.",
                                "improvement": "Suggestions for improving issue 2."
                            },
                            {
                                "id": "3",
                                "title": "Issue 3",
                                "severity": "potential",
                                "details": "Details about issue 3.",
                                "improvement": "Suggestions for improving issue 3."
                            }
                        ]
                    """
                },
                {
                    "type": "text",
                    "text": f"""Ensure that the response is always valid JSON with double quotes (") instead of single quotes (')."""
                },
                {
                    "type": "text",
                    "text": f"""
                        Here is an example:
                        """
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "detail": "high",
                        "url": example_image_data
                    }
                },
                {
                    "type": "text",
                    "text": "Here is the output of the example image: "
                },
                {
                    "type": "text",
                    "text": """
                                [
                                    {
                                        "id": "1",
                                        "title": "Truncated Axis",
                                        "severity": "major",
                                        "details": "The bar chart does not start the vertical axis at zero, exaggerating the difference between 45% and 43%. This visually distorts the comparison and misrepresents the actual gap.",
                                        "improvement": "Adjust the axis to start at zero to accurately represent the percentage values and ensure proportionality in the bar lengths."
                                    },
                                    {
                                        "id": "2",
                                        "title": "Misrepresentation",
                                        "severity": "major",
                                        "details": "The difference between the two percentages (45% vs. 43%) is relatively small but is visually amplified by the design of the bars and the lack of a clear baseline.",
                                        "improvement": "Ensure that the length of the bars directly corresponds to the percentage values without artificial amplification."
                                    },
                                    {
                                        "id": "3",
                                        "title": "Violating Color Convention",
                                        "severity": "minor",
                                        "details": "The use of red for one candidate and blue for the other follows a U.S. political convention but might not be meaningful without clarification in the context of the visualization.",
                                        "improvement": "Provide a clear legend or annotation explaining the choice of colors to avoid confusion."
                                    },
                                    {
                                        "id": "4",
                                        "title": "Misleading Title",
                                        "severity": "potential",
                                        "details": "The title does not clearly state that this is polling data and may give the impression that these are final results or definitive outcomes.",
                                        "improvement": "Modify the title to indicate that the chart represents polling results and specify the context, such as the date or methodology of the poll."
                                    },
                                    {
                                        "id": "5",
                                        "title": "Distractive Value Labels",
                                        "severity": "minor",
                                        "details": "The large text size of the percentage labels (45% and 43%) draws disproportionate attention and may bias viewers toward focusing on the numbers without context.",
                                        "improvement": "Reduce the size of the percentage labels or include additional explanatory context to balance the visual impact."
                                    },
                                ]
                    """
                },
                {
                    "type": "text",
                    "text": "Remember to think step-by-step and consider all aspects of the chart before providing your final analysis. Ensure that each identified issue corresponds to a specific pitfall from the provided checklist."
                },
                {
                    "type": "text",
                    "text": "Your response should be a valid JSON array containing objects for each identified issue, or an empty array if no issues are found. Do not include any additional text or explanations outside of the JSON structure."
                },
            ]
        }
    ]
