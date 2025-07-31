from ..pitfalls import get_pitfalls


def generate_pitfalls_text():
    pitfalls = get_pitfalls()
    pitfalls_text = ""
    for key, value in pitfalls.items():
        pitfalls_text += f"{value['label']}: {value['description']}\n"
    return pitfalls_text


def misleading_decision_user_message_image_gpt_prompt(image, user_message):
    pitfalls_text = generate_pitfalls_text()
    example_image = "https://firebasestorage.googleapis.com/v0/b/chartinsight-3f620.appspot.com/o/download%20(4).png?alt=media&token=0105042c-e1f7-4a43-898a-b848dccc067e"
    return [
    {
        "role": "system",
        "content": "You are an AI tasked with analyzing graphs to determine if they are misleading. You will be provided with an image of a graph, a user instruction, and a checklist of visualization pitfalls. Your job is to decide whether the result of applying the user's request to the chart would be misleading or not."
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "First, review the following checklist of common pitfalls in data visualization:"
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
                "text": "Then examine the provided chart image and assess the following user instruction:"
            },
            {
                "type": "text",
                "text": f"""<user_message>
                    {user_message}
                </user_message>"""
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
                    
                    <decision>
                        true|false
                    </decision>
                    
                    <reason>
                        <b>[pitfall 1]</b>: [explanation of how the pitfall applies if the user instruction is applied to the chart]
                        <b>[pitfall 2]</b>: [explanation...]
                        ...
                    </reason>
                """
            },
            {
                "type": "text",
                "text": f"""
                    Guidelines:
                        - Use only the pitfalls provided in your reasoning.
                        - Mark <decision>true</decision> only if the user's instruction would likely make the chart misleading based on one or more of the pitfalls.
                        - Mark <decision>false</decision> if the change would not introduce misleading elements.
                        - Include at least one matching pitfall explanation in <reason> if <decision>true</decision>.
                """
            },
            {
                "type": "text",
                "text": f"""
                    **Here is an example:**
                """
            },
            {
                "type": "text",
                "text": f"""User instruction: Change color blue to red"""
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
                        **Response:**
                        The expected output is:
                            <decision>true</decision>
                            <reason>
                                <b>Violating Color Convention</b>: Changing the Clinton bar from blue to red disrupts consistency in color assignment across the chart. Each color currently represents a distinct group. Reusing red introduces ambiguity, reducing clarity.

                                <b>Misrepresentation</b>: Visually encoding two different categories with the same color may unintentionally suggest they represent the same or similar data. This risks misleading the viewer, especially in comparative bar charts.

                                <b>Ineffective Color Scheme</b>: Using the same color (red) for two separate bars reduces the ability to distinguish between them, which hinders accurate comparison and data interpretation.
                            </reason>
                """
            }
        ]
    }
]


def misleading_decision_user_message_code_gpt_prompt(code, user_message):
    pitfalls_text = generate_pitfalls_text()
    example_image = "https://firebasestorage.googleapis.com/v0/b/chartinsight-3f620.appspot.com/o/download%20(4).png?alt=media&token=0105042c-e1f7-4a43-898a-b848dccc067e"
    return [
    {
        "role": "system",
        "content": "You are an expert in data visualization and graphical integrity. You are tasked with evaluating whether a user's requested modification to a chart (represented by Python code) could result in a misleading visualization. Your analysis must be grounded strictly in a provided list of visualization pitfalls."
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": f"""
                    You will be provided with three inputs:
                        1. A Python code block that generates a chart.
                        2. A user instruction for modifying that chart.
                        3. A list of visualization pitfalls.
                                
                    Your job is to assess whether applying the user instruction to the chart code could result in a misleading visualization, based on the pitfall list."""
            },
            {
                "type": "text",
                "text": f"""
                    Here is the chart code:
                        <chart_code>
                            {code}
                        </chart_code>
                """
            },
            {
                "type": "text",
                "text": f"""
                    Here is the user instruction:
                        <user_message>
                            {user_message}
                        </user_message>
                """
            },
            {
                "type": "text",
                "text": f"""
                    Here is the pitfall list you must use for your analysis:
                        <pitfalls>
                            {pitfalls_text}
                        </pitfalls>
                """
            },
            {
                "type": "text",
                "text": f"""
                    Your response must strictly follow this format:
                    
                    <decision>
                        true|false
                    </decision>
                    
                    <reason>
                        <b>[pitfall 1]</b>: [explanation of how the pitfall applies if the user instruction is applied to the chart]
                        <b>[pitfall 2]</b>: [explanation...]
                        ...
                    </reason>
                """
            },
            {
                "type": "text",
                "text": f"""
                    Guidelines:
                        - Use only the pitfalls provided in your reasoning.
                        - Mark <decision>true</decision> only if the user's instruction would likely make the chart misleading based on one or more of the pitfalls.
                        - Mark <decision>false</decision> if the change would not introduce misleading elements.
                        - Include at least one matching pitfall explanation in <reason> if <decision>true</decision>.
                """
            },
            {
                "type": "text",
                "text": f"""
                    **Here is an example:**
                """
            },
            {
                "type": "text",
                "text": f"""
                    User instruction:
                        <user_message>
                            Change the color blue to red
                        </user_message>
                """
            },
            {
                "type": "text",
                "text": "Python chart code:\n<chart_code>\nimport pandas as pd\nimport matplotlib.pyplot as plt\nimport numpy as np\nimport seaborn as sns\n\nplt.style.use('seaborn-v0_8')\n\ndata = pd.DataFrame([\n    ['Trump', 45, 3.5],\n    ['Clinton', 43, 3.5],\n    ['Undecided/Other', 12, 3.5]\n], columns=['Candidate', 'Support_Percentage', 'Margin_of_Error'])\n\nfig, ax = plt.subplots(figsize=(10, 6))\n\nbars = ax.bar(data['Candidate'], data['Support_Percentage'], \n              color=['#E91D0E', '#0015BC', '#808080'])\n\nax.errorbar(data['Candidate'], data['Support_Percentage'],\n            yerr=data['Margin_of_Error'], fmt='none', color='black',\n            capsize=5)\n\nax.set_ylim(0, 100)\nax.set_ylabel('Support Percentage (%)')\nax.set_title('2016 Colorado Presidential Poll Results\\nwith Margin of Error (±3.5%)',\n             pad=20)\n\nfor bar in bars:\n    height = bar.get_height()\n    ax.text(bar.get_x() + bar.get_width()/2., height,\n            f'{height}%',\n            ha='center', va='bottom')\n\nplt.figtext(0.02, 0.02, 'Source: Reuters/Ipsos Poll', \n            fontsize=8, alpha=0.7)\n\nplt.tight_layout()\nplt.show()\n</chart_code>"
            },            
            {
                "type": "text",
                "text": f"""
                    Expected output:
                        <decision>
                            true
                        </decision>
                        
                        <reason>
                            <b>Violating Color Convention</b>: Changing the Clinton bar from blue to red disrupts consistency in color assignment across the chart. Each color currently represents a distinct group. Reusing red introduces ambiguity, reducing clarity.

                            <b>Misrepresentation</b>: Visually encoding two different categories with the same color may unintentionally suggest they represent the same or similar data. This risks misleading the viewer, especially in comparative bar charts.

                            <b>Ineffective Color Scheme</b>: Using the same color (red) for two separate bars reduces the ability to distinguish between them, which hinders accurate comparison and data interpretation.
                        </reason>
                """
            }
        ]
    }
]
