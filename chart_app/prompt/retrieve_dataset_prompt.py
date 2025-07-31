from ..image_conversion_helper import get_image_type_from_url, image_url_to_base64


def retrieve_dataset_cl_prompt(image, key_issues):
    return [
        {
            "type": "text",
            "text": "Follow these instructions to analyze the chart and create a corrected dataset: "
        },
        {
            "type": "text",
            "text": "First, Please analyze the following image: "
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
                        Key issues identified with this chart: 
                        <key_issues>
                        {', '.join(key_issues)}.
                        </key_issues>    
                    """
        },
        {
            "type": "text",
            "text": f"""
                    Analyze both image & key issues.
                """
        },
        {
            "type": "text",
            "text": f"""
                    1. Data Extraction Rules:
                        - Extract data ONLY from the correct/accurate chart if multiple versions are shown
                        - Follow any specific instructions or notes provided in the image
                        - Include ALL data points visible in the visualization
                        - Maintain the exact same time periods/intervals as shown
                        - Use the same units and scales as indicated in the original
                        - 

                    2. Output Format Requirements:
                        - Provide data in CSV format with clear column headers
                        - Include ONLY columns/metrics that are explicitly shown in the visualization
                        - Use consistent decimal places and number formatting throughout
                        - Separate values with commas and rows with newlines

                    3. Context Preservation:
                        - Include the title and subtitle exactly as shown
                        - Preserve any axis labels and units
                        - Note any relevant legends or keys
                        - Include any critical footnotes or data source information

                    4. Data Validation:
                        - Confirm all required data points are included


                    Please provide the dataset in this format:
                    column1,column2,column3
                    value1,value2,value3
                """
        },
        {
            "type": "text",
            "text": f"""   
                    2. Output Format:
                       <corrected_dataset>
                           [Complete with corrected dataset in structured format]
                       </corrected_dataset>
                    3. Explanation:
                       <explanation>
                           Explain how the corrected dataset addresses each key issue identified
                       </explanation>

                """
        },
        {
            "type": "text",
            "text": f"""
                    Important: Generate the complete dataset without any placeholders or "continued" markers.
                """
        },
    ]


def retrieve_dataset_gpt_prompt(image, key_issues):
    return [
        {
            "role": "system",
            "content": "You are a data analyst tasked with extracting accurate datasets from visualizations and correcting any identified issues to provide a complete and accurate CSV output."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Follow these instructions to analyze the chart and create a corrected dataset:"
                },
                {
                    "type": "text",
                    "text": "First, analyze the following image:"
                },
                {
                    "type": "image_url",
                    "image_url": {"url": image}
                },
                {
                    "type": "text",
                    "text": "Key issues identified with this chart:"
                },
                {
                    "type": "text",
                    "text": f"""
                        {', '.join(key_issues)}
                    """
                },
                {
                    "type": "text",
                    "text": "Analyze the image and the issues to create a corrected dataset."
                },
                {
                    "type": "text",
                    "text": "Data Extraction Rules:\n- Extract data ONLY from the correct/accurate chart if multiple versions are shown\n- Follow any specific instructions or notes provided in the image\n- Include ALL data points visible in the visualization\n- Maintain the exact same time periods/intervals as shown\n- Use the same units and scales as indicated in the original"
                },
                {
                    "type": "text",
                    "text": "Output Format Requirements:\n- Provide data in CSV format with clear column headers\n- Include ONLY columns/metrics that are explicitly shown in the visualization\n- Use consistent decimal places and number formatting throughout\n- Separate values with commas and rows with newlines"
                },
                {
                    "type": "text",
                    "text": "Context Preservation:\n- Include the title and subtitle exactly as shown\n- Preserve any axis labels and units\n- Note any relevant legends or keys\n- Include any critical footnotes or data source information"
                },
                {
                    "type": "text",
                    "text": "Data Validation:\n- Confirm all required data points are included"
                },
                {
                    "type": "text",
                    "text": "Please provide the dataset in this format:\ncolumn1,column2,column3\nvalue1,value2,value3"
                },
                {
                    "type": "text",
                    "text": "Output Format:\n<corrected_dataset>\n[Complete dataset in structured CSV format]\n</corrected_dataset>\nExplanation:\n<explanation>\nExplain how the corrected dataset addresses each key issue identified.\n</explanation>"
                },
                {
                    "type": "text",
                    "text": "Important: Generate the complete dataset without any placeholders or \"continued\" markers. Please strictly follow the output format."
                }
            ]
        }
    ]
