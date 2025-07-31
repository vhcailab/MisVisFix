from ..image_conversion_helper import get_image_type_from_url, image_url_to_base64
from ..pitfalls import get_pitfalls
from ..core_pitfalls_list import get_core_pitfalls

def generate_pitfalls_text():
    pitfalls = get_pitfalls()
    pitfalls_text = ""
    for key, value in pitfalls.items():
        pitfalls_text += f"{value['label']}: {value['description']}\n"
    return pitfalls_text

def generate_core_pitfalls_text():
    pitfalls = get_core_pitfalls()
    pitfalls_text = ""
    for key, value in pitfalls.items():
        pitfalls_text += f"{value['label']}: {value['description']}\n"
    return pitfalls_text


def misleading_decision_cl_prompt(image):
    pitfalls_text = generate_pitfalls_text()
    core_pitfall_text = generate_core_pitfalls_text()
    example_image = "https://firebasestorage.googleapis.com/v0/b/chartinsight-3f620.appspot.com/o/imagesimg-10.jpeg?alt=media&token=0b39a841-ada1-4a69-9bcf-b658dbc30446"
    return [
    {
        "type": "text",
        "text": "Review this separate checklist of **core pitfalls** that determine whether a chart is misleading:"
    },
    {
        "type": "text",
        "text": f"""
            <core_pitfalls_checklist> 
                {core_pitfall_text} 
            </core_pitfalls_checklist> 
        """
    },
    {
        "type": "text",
        "text": "Examine the provided chart against **all pitfalls** but determine if it is **misleading** only based on the **core pitfalls**."
    },
    {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": f"image/{get_image_type_from_url(image)}",
            "data": image_url_to_base64(image)
        }
    },
    {
        "type": "text",
        "text": f""" 
            Your response must strictly follow this format:

            <analysis>
                [Evaluate the chart based on **all pitfalls** and list any issues found. Clearly specify if they are **core** pitfalls or minor issues.]
            </analysis>
            
            <decision>
                [true if the chart contains **one or more core pitfalls**]  
                [false if the chart has **no core pitfalls**, even if minor issues exist.]
            </decision>
            
            <decision_details>
                [Clearly explain why the chart is or is not misleading based on **core pitfalls**. Minor issues should be noted but should NOT influence the misleading decision.]
            </decision_details>
        """
    },
    {
        "type": "text",
        "text": f""" 
            **Guidelines for Assessment:**
            - **Check all possible pitfalls** but **only core pitfalls determine if a chart is misleading**.
            - **If there are core pitfalls, return `true` (misleading chart).**
            - **If there are no core pitfalls, return `false`**, even if minor issues exist.
            - **Do not flag minor design flaws** like font size, legend position, or color choices unless they **directly distort data interpretation**.
            - If a corrected version is uploaded and **none of the core issues remain**, return `false`.
        """
    },
    {
        "type": "text",
        "text": f"""
            **Example of a misleading chart and correct evaluation:**
        """
    },
    {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": f"image/{get_image_type_from_url(example_image)}",
            "data": image_url_to_base64(example_image)
        }
    },
    {
        "type": "text",
        "text": f"""
                **Response:**
                <analysis> 
                    The provided graph has the following **issues**:
                    - **Misrepresentation (Core Pitfall)**: The bar lengths are not proportional to the numerical data, making the difference between values seem larger than it is.
                    - **Truncated Axis (Core Pitfall)**: The y-axis does not start at zero, exaggerating the visual difference between 45% and 43%.
                    - **Misleading Visual Emphasis (Core Pitfall)**: The inclusion of Trump's image giving a thumbs-up gesture adds a positive connotation unrelated to the data.
                </analysis>

                <decision>
                    true 
                </decision>

                <decision_details> 
                    The chart is misleading because the **core pitfalls** (misrepresentation, truncated axis, and misleading visual emphasis) significantly distort the actual data relationships. While minor issues like the color scheme exist, they do not heavily contribute to the misleading nature of the chart. The design exaggerates the visual gap between the two percentages and introduces bias through the use of imagery.
                </decision_details>
        """
    }
]

def misleading_decision_gpt_prompt(image):
    return [
    {
        "role": "system",
        "content": "You are an AI tasked with analyzing graphs to determine if they are misleading. You will be provided with an image of a graph, and your job is to decide whether the graph is misleading or not based strictly on core pitfalls."
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Review this separate checklist of **pitfalls** that determine whether a chart is misleading:"
            },
            {
                "type": "text",
                "text": f"""
                    <pitfalls_checklist> 
                        {get_core_pitfalls()} 
                    </pitfalls_checklist> 
                """
            },
            {
                "type": "text",
                "text": "Examine the provided chart against **all pitfalls** but determine if it is **misleading** only based on the **pitfalls**."
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
                "text": f""" 
                    Your response must strictly follow this format:

                    <analysis>
                        [Evaluate the chart based on **all pitfalls** and list any issues found. Clearly specify if they are pitfalls or minor issues.]
                    </analysis>
                    
                    <decision>
                        [true if the chart contains **one or more pitfalls**]  
                        [false if the chart has **no pitfalls**, even if minor issues exist.]
                    </decision>
                    
                    <decision_details>
                        [Clearly explain why the chart is or is not misleading based on **pitfalls**. Minor issues should be noted but should NOT influence the misleading decision.]
                    </decision_details>
                """
            },
            {
                "type": "text",
                "text": f""" 
                    **Guidelines for Assessment:**
                    - **Analyze the image carefully and closely the axis starting point**.
                    - **Check all possible pitfalls** but **only pitfalls determine if a chart is misleading**.
                    - **If there are pitfalls present based on rules, return `true` (misleading chart).**
                    - **If there are no pitfalls, return `false`**, even if minor issues exist.
                    - **Do not flag minor design flaws** like font size, legend position, or color choices unless they **directly distort data interpretation**.
                    - If a corrected version is uploaded and **none of the core issues remain**, return `false`.
                """
            },
        ]
    }
]
