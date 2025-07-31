from ..image_conversion_helper import get_image_type_from_url, image_url_to_base64


def text_chat_gpt_prompt(question, image_url):
    return [
        {
            "role": "system",
            "content": "You are an expert in chart analysis. You will be provided with a chart image and a question about the chart. Your task is to analyze the image carefully and answer the question based on the information."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "First, examine the chart image provided at this URL: "
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
                    "text": "Analyze the chart thoroughly, paying attention to all elements such as title, axes, labels, data points, trends, and any other visual information presented."
                },
                {
                    "type": "text",
                    "text": f"Now, consider the following question about the chart: {question}"
                },
                {
                    "type": "text",
                    "text": f"""
                    To answer the question:
                        1. Carefully interpret the relevant data from the chart.
                        2. Consider any trends, patterns, or specific data points that are pertinent to the question.
                        3. Formulate a clear and concise answer based on your analysis.
                    """
                },
            ]
        }
    ]


def text_chat_cl_prompt(question, image):
    return [
        {
            "type": "text",
            "text": "First, examine the chart image provided at this URL: "
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
            "text": "Analyze the chart thoroughly, paying attention to all elements such as title, axes, labels, data points, trends, and any other visual information presented."
        },
        {
            "type": "text",
            "text": f"""
                Now, consider the following question about the chart:
                <question>
                    {question}
                </question>
            """
        },
        {
            "type": "text",
            "text": f"""
                To answer the question:
                    1. Carefully interpret the relevant data from the chart.
                    2. Consider any trends, patterns, or specific data points that are pertinent to the question.
                    3. Formulate a clear and concise answer based on your analysis.
            """
        },
    ]
