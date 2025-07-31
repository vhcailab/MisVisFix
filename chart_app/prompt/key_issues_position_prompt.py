from ..image_conversion_helper import get_image_type_from_url, image_url_to_base64


def key_issues_position_cl_prompt(image, key_issues, actual_box_width, actual_box_height):
    example_image = "https://firebasestorage.googleapis.com/v0/b/chartinsight-3f620.appspot.com/o/imageschart-1.png?alt=media&token=bdd660b0-b59b-4828-8fd5-56aa4a4fca8e"
    return [
        {
            "type": "text",
            "text": f"Here is the URL of the chart image: "
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
            "text": f"The key issues associated with this chart are: "
        },
        {
            "type": "text",
            "text": f"""
                <key_issues>
                    {', '.join(key_issues)}.
                </key_issues>
            """
        },
        {
            "type": "text",
            "text": f"""
                Your goal is to return a list of objects, each representing a key issue, with the following properties:
                    - issues_id: The issue name in lowercase with underscores as separators
                    - issues_name: The original issue name
                    - top_gap: The vertical distance from the top of the image to the issue label
                    - left_gap: The horizontal distance from the left of the image to the issue label
            """
        },
        {
            "type": "text",
            "text": f"""
                When positioning the issues on the chart:
                    1. Ensure that each issue is placed in a logical position that clearly highlights the problem area.
                    2. Make sure all issue names are legible and do not exceed the image boundaries.
                    3. If an issue name might extend outside the image boundaries, adjust its position to keep it visible within the image.
                """
        },
        {
            "type": "text",
            "text": f"""
                    Important constraints:
                        - The maximum width of the image container is {int(actual_box_width)} pixels.
                        - The maximum height of the image container is {int(actual_box_height)} pixels.
                        - Ensure that no top_gap value exceeds the maximum height and no left_gap value exceeds the maximum width.
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
                    Here is an example of how to identify the issues position.
            """
        },
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": f"image/{get_image_type_from_url(example_image)}",
                "data": image_url_to_base64(example_image)
            },
        },
        {
            "type": "text",
            "text": "Here are the key issues of the example chart: Truncated Axis, Inappropriate Axis Range, Misleading Title, Missing Units, Misrepresentation."
        },
        {
            "type": "text",
            "text": f"""
                        {[
                {
                    "issues_id": "truncated_axis",
                    "issues_name": "Truncated Axis",
                    "top_gap": 50,
                    "left_gap": 10,
                    "explanation": "Positioned at the top left of the axis section to clearly highlight the truncation issue."
                },
                {
                    "issues_id": "inappropriate_axis_range",
                    "issues_name": "Inappropriate Axis Range",
                    "top_gap": 100,
                    "left_gap": 10,
                    "explanation": "Placed below 'Truncated Axis' to show that the range starts inappropriately close to the values."
                },
                {
                    "issues_id": "misleading_title",
                    "issues_name": "Misleading Title",
                    "top_gap": 10,
                    "left_gap": 200,
                    "explanation": "Aligned near the title area to draw attention to its misleading nature."
                },
                {
                    "issues_id": "missing_units",
                    "issues_name": "Missing Units",
                    "top_gap": 150,
                    "left_gap": 10,
                    "explanation": "Added at the bottom-left of the axis section to indicate missing unit labels."
                },
                {
                    "issues_id": "misrepresentation",
                    "issues_name": "Misrepresentation",
                    "top_gap": 200,
                    "left_gap": 10,
                    "explanation": "Located near the middle of the bar chart to emphasize misrepresentation in data scaling."
                }
            ]}
                    """
        },
        {
            "type": "text",
            "text": "Think through the placement of each issue step-by-step, considering its relevance to specific areas of the chart and ensuring optimal visibility."
        },
        {
            "type": "text",
            "text": "Provide your final output as a list of objects in the format described above, without any additional text or explanations."
        },
    ]


def key_issues_position_gpt_prompt(image, key_issues, actual_box_width, actual_box_height):
    example_image = "https://firebasestorage.googleapis.com/v0/b/chartinsight-3f620.appspot.com/o/imageschart-1.png?alt=media&token=bdd660b0-b59b-4828-8fd5-56aa4a4fca8e"
    return [
        {
            "role": "system",
            "content": "You are an expert in chart analysis. Your task is to accurately plot key issues on a misleading chart image and provide a list of objects with specific properties for each issue."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Here is the URL of the chart image: "
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
                    "text": f"The key issues associated with this chart are: "
                },
                {
                    "type": "text",
                    "text": f"""
                        <key_issues>
                            {', '.join(key_issues)}.
                        </key_issues>
                    """
                },
                {
                    "type": "text",
                    "text": f"""
                        Your goal is to return a list of objects, each representing a key issue, with the following properties:
                            - issues_id: The issue name in lowercase with underscores as separators
                            - issues_name: The original issue name
                            - top_gap: The vertical distance from the top of the image to the issue label
                            - left_gap: The horizontal distance from the left of the image to the issue label
                    """
                },
                {
                    "type": "text",
                    "text": f"""
                        When positioning the issues on the chart:
                            1. Ensure that each issue is placed in a logical position that clearly highlights the problem area.
                            2. Make sure all issue names are legible and do not exceed the image boundaries.
                            3. If an issue name might extend outside the image boundaries, adjust its position to keep it visible within the image.
                        """
                },
                {
                    "type": "text",
                    "text": f"""
                            Important constraints:
                                - The maximum width of the image container is {int(actual_box_width)} pixels.
                                - The maximum height of the image container is {int(actual_box_height)} pixels.
                                - Ensure that no top_gap value exceeds the maximum height and no left_gap value exceeds the maximum width.
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
                            Here is an example of how to identify the issues position.
                    """
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "detail": "high",
                        "url": example_image
                    }
                },
                {
                    "type": "text",
                    "text": "Here are the key issues of the example chart: Truncated Axis, Inappropriate Axis Range, Misleading Title, Missing Units, Misrepresentation."
                },
                {
                    "type": "text",
                    "text": """
                        [
                            {
                                "issues_id": "truncated_axis",
                                "issues_name": "Truncated Axis",
                                "top_gap": 50,
                                "left_gap": 10,
                                "explanation": "Positioned at the top left of the axis section to clearly highlight the truncation issue."
                            },
                            {
                                "issues_id": "inappropriate_axis_range",
                                "issues_name": "Inappropriate Axis Range",
                                "top_gap": 100,
                                "left_gap": 10,
                                "explanation": "Placed below 'Truncated Axis' to show that the range starts inappropriately close to the values."
                            },
                            {
                                "issues_id": "misleading_title",
                                "issues_name": "Misleading Title",
                                "top_gap": 10,
                                "left_gap": 200,
                                "explanation": "Aligned near the title area to draw attention to its misleading nature."
                            },
                            {
                                "issues_id": "missing_units",
                                "issues_name": "Missing Units",
                                "top_gap": 150,
                                "left_gap": 10,
                                "explanation": "Added at the bottom-left of the axis section to indicate missing unit labels."
                            },
                            {
                                "issues_id": "misrepresentation",
                                "issues_name": "Misrepresentation",
                                "top_gap": 200,
                                "left_gap": 10,
                                "explanation": "Located near the middle of the bar chart to emphasize misrepresentation in data scaling."
                            }
                        ]
                        """
                },
                {
                    "type": "text",
                    "text": "Think through the placement of each issue step-by-step, considering its relevance to specific areas of the chart and ensuring optimal visibility."
                },
                {
                    "type": "text",
                    "text": "Provide your final output as a list of objects in the format described above, without any additional text or explanations."
                },
            ]
        }
    ]
