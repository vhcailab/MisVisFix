from ..image_conversion_helper import get_image_type_from_url, image_url_to_base64
from ..pitfalls import get_pitfalls


def generate_pitfalls_text():
    pitfalls = get_pitfalls()
    pitfalls_text = ""
    for key, value in pitfalls.items():
        pitfalls_text += f"{value['label']}: {value['description']}\n"
    return pitfalls_text


def misleading_decision_cl_prompt(image):
    pitfalls_text = generate_pitfalls_text()
    example_image = "https://firebasestorage.googleapis.com/v0/b/chartinsight-3f620.appspot.com/o/imagesimg-10.jpeg?alt=media&token=0b39a841-ada1-4a69-9bcf-b658dbc30446"
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
            "text": "Carefully examine the provided chart to determine if any of the mentioned pitfalls exist. Focus on identifying issues that could mislead viewers or significantly hinder the interpretation of the data."
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
                Your response must strictly follow this format:

                <analysis>
                   [Evaluate the chart based solely on the provided pitfalls. Identify flaws that could mislead viewers or compromise the clarity, accuracy, or integrity of the visualization.]
                </analysis>
                
                <decision>
                    [true if the chart contains major issues OR multiple minor issues that could lead to misinterpretation]  
                    [false if there are no major issues AND only minor isolated issues that do not compromise the chart's integrity or message.]
                </decision>
                
                <decision_details>
                    [Clearly explain why the chart is or is not misleading based strictly on the identified pitfalls. Justify how the issues impact the chart's interpretability, accuracy, or trustworthiness.]
                </decision_details>
            """
        },
        {
            "type": "text",
            "text": f""" 
                Guidelines for Assessment:
                - Base your analysis strictly on the provided pitfalls. Avoid considering factors outside this checklist.
                - Focus on whether the chart's issues lead to misinterpretation, ambiguity, or a loss of trustworthiness.
                - A decision of "true" should be made if the issues meaningfully compromise the chart's ability to communicate accurate and clear data.
                - A decision of "false" should only be made if the issues are minor and do not significantly affect the chart's interpretability.
            """
        },
        {
            "type": "text",
            "text": f"""
                <example>
                    Here is an example of a misleading chart and its corresponding analysis:
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
            "text": f"""
                     The response is:
                     <analysis> 
                        The provided graph has the following issues:
                            Misrepresentation: The bar lengths for Trump (45%) and Clinton (43%) do not accurately reflect their numerical difference. The visual difference between the bars is exaggerated, misleading the viewer into thinking Trump's lead is more significant than it actually is.
                            Violating Color Convention: Red and blue are commonly associated with Republican and Democratic parties in the United States, which is consistent here. However, the use of these colors alongside a significant size discrepancy may amplify the bias.
                            Misleading Annotation: The visual emphasis of Trump's bar, combined with the prominent placement of his image and gesture, creates a bias in interpretation, potentially overshadowing the actual data.
                            Inappropriate Use of Bar Chart: Bar charts are intended to represent proportional differences clearly. The graph fails this purpose due to the disproportionate scaling of the bars.
                            Misleading Value Labels: While the percentage values are labeled, the mismatch between the numerical data and the visual representation causes confusion, misleading viewers regarding the true proportions.
                            Distractive Elements: The inclusion of a large image of Trump giving a thumbs-up further distracts from the data itself and introduces a bias in favor of Trump.
                    </analysis>
                    <decision>
                        true 
                    </decision>
                    <decision_details> 
                        The graph is misleading because the bar chart's visual representation does not accurately reflect the numerical data, exaggerating the difference between Trump and Clinton's percentages. Additionally, the design choices, including disproportionate bar scaling, prominent imagery, and distractive elements, introduce bias and fail to adhere to neutral data visualization principles. 
                    </decision_details>
                </example>
            """
        }
    ]


def misleading_decision_gpt_prompt(image):
    pitfalls_text = generate_pitfalls_text()
    example_image = "https://firebasestorage.googleapis.com/v0/b/chartinsight-3f620.appspot.com/o/imagesimg-10.jpeg?alt=media&token=0b39a841-ada1-4a69-9bcf-b658dbc30446"
    return [
        {
            "role": "system",
            "content": "You are an AI tasked with analyzing graphs to determine if they are misleading. You will be provided with an image of a graph, and your job is to decide whether the graph is misleading or not."
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
                    "text": "Carefully examine the provided chart to determine if any of the mentioned pitfalls exist. Focus on identifying issues that could mislead viewers or significantly hinder the interpretation of the data."
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
                        [Evaluate the chart based solely on the provided pitfalls. Identify flaws that could mislead viewers or compromise the clarity, accuracy, or integrity of the visualization.]
                        </analysis>
                        
                        <decision>
                            [true if the chart contains major issues OR multiple minor issues that could lead to misinterpretation]  
                            [false if there are no major issues AND only minor isolated issues that do not compromise the chart's integrity or message.]
                        </decision>
                        
                        <decision_details>
                            [Clearly explain why the chart is or is not misleading based strictly on the identified pitfalls. Justify how the issues impact the chart's interpretability, accuracy, or trustworthiness.]
                        </decision_details>
                    """
                },
                {
                    "type": "text",
                    "text": f""" 
                    Guidelines for Assessment:
                        - Base your analysis strictly on the provided pitfalls. Avoid considering factors outside this checklist.
                        - Focus on whether the chart's issues lead to misinterpretation, ambiguity, or a loss of trustworthiness.
                        - A decision of "true" should be made if the issues meaningfully compromise the chart's ability to communicate accurate and clear data.
                        - A decision of "false" should only be made if the issues are minor and do not significantly affect the chart's interpretability.
                    """
                },
                {
                    "type": "text",
                    "text": f"""
                        Here is an example of a misleading chart and its corresponding analysis:
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
                    "text": f"""
                        The example image response is:
                                <analysis> 
                                    The provided graph has the following issues:
                                        Misrepresentation: The bar lengths for Trump (45%) and Clinton (43%) do not accurately reflect their numerical difference. The visual difference between the bars is exaggerated, misleading the viewer into thinking Trump's lead is more significant than it actually is.
                                        Violating Color Convention: Red and blue are commonly associated with Republican and Democratic parties in the United States, which is consistent here. However, the use of these colors alongside a significant size discrepancy may amplify the bias.
                                        Misleading Annotation: The visual emphasis of Trump's bar, combined with the prominent placement of his image and gesture, creates a bias in interpretation, potentially overshadowing the actual data.
                                        Inappropriate Use of Bar Chart: Bar charts are intended to represent proportional differences clearly. The graph fails this purpose due to the disproportionate scaling of the bars.
                                        Misleading Value Labels: While the percentage values are labeled, the mismatch between the numerical data and the visual representation causes confusion, misleading viewers regarding the true proportions.
                                        Distractive Elements: The inclusion of a large image of Trump giving a thumbs-up further distracts from the data itself and introduces a bias in favor of Trump.
                                </analysis>
                                <decision>
                                    true 
                                </decision>
                                <decision_details> 
                                    The graph is misleading because the bar chart's visual representation does not accurately reflect the numerical data, exaggerating the difference between Trump and Clinton's percentages. Additionally, the design choices, including disproportionate bar scaling, prominent imagery, and distractive elements, introduce bias and fail to adhere to neutral data visualization principles. 
                                </decision_details>
                        """
                }
            ],
        }
    ]
