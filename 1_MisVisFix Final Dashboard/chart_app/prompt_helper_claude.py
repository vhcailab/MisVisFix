from .pitfalls import get_pitfalls
import base64
from .image_conversion_helper import image_url_to_base64, get_image_type_from_url
import httpx


def generate_pitfalls_text():
    pitfalls = get_pitfalls()
    pitfalls_text = ""
    for key, value in pitfalls.items():
        pitfalls_text += f"{value['label']}: {value['description']}\n"
    return pitfalls_text


def get_key_issues_cl_prompt(image):
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
            "text": f"""
                    Classify the pitfalls into the following categories:
                        1. Major Pitfalls - Issues that severely undermine the integrity and trustworthiness of the data representation, such as misrepresenting the underlying data or using visualizations in inappropriate ways.
                        2. Minor Pitfalls - Problems that reduce the chart's clarity, usability or accessibility, but don't necessarily invalidate the data itself.
                        3. Potential or Inconclusive Pitfalls - Issues that may introduce bias or misleading impressions, but require more context to determine their severity.
                """
        },
        {
            "type": "text",
            "text": "Here is the chart image for you to analyze: "
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
                    1. Carefully examine all elements of the chart, including axes, labels, colors, data representation, and overall design.
                    2. Compare each element to the pitfalls in the checklist.
                    3. For each identified pitfall, determine its category (Major, Minor, or Potential) based on its impact on the chart's integrity and effectiveness.
                    4. Provide a detailed explanation for each pitfall, specifying why it belongs to that category and how it affects the chart's interpretation.
            """
        },
        {
            "type": "text",
            "text": "Present your analysis in the following format: "
        },
        {
            "type": "text",
            "text": f"""
                <analysis>
                    The chart contains the following pitfalls:
                    1. **Pitfall Name (Category)**
                       - Detailed explanation of why this pitfall is present and how it affects the chart
                    2. **Pitfall Name (Category)**
                       - Detailed explanation of why this pitfall is present and how it affects the chart
                    (Continue for all identified pitfalls)
                </analysis>

                After your detailed analysis, provide a JSON-formatted summary of the pitfalls in each category. Use the exact label names from the pitfalls list (e.g., 'Misrepresentation', 'Missing Axis', etc.). Use the following format:

                <output>
                    ```{{
                        "major": [
                            "Pitfall 1",
                            "Pitfall 2"
                          ],
                          "minor": [
                            "Pitfall 3"
                          ],
                          "potentials": [
                            "Pitfall 4",
                            "Pitfall 5"
                          ]
                    }}```
                </output>
            """
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
            "text": "Here is the analysis and output of the example image: "
        },
        {
            "type": "text",
            "text": f"""
                    Analysis: The chart contains the following pitfalls:
                    1. **Misrepresentation (Major)**
                            - The bar representing Trump (45%) is disproportionately taller than the bar for Clinton (43%).
                            - This exaggerates the visual difference in percentages (2%) and misleads viewers about the data.
                            - This is a **major pitfall** because it fundamentally distorts the data representation.
                    2. **Missing Axis (Minor)**
                            - The chart lacks axis labels or tick marks to provide a reference for bar heights.
                            - Without a scale, viewers cannot verify if the bars are accurately proportional to their values.
                            - This is a **minor pitfall** because it affects clarity but does not directly misrepresent the data.
                    3. **Distractive Value Labels (Minor)**
                            - The prominent image of Trump giving a thumbs-up distracts from the data and introduces emotional bias.
                            - This is a **minor pitfall** because it affects neutrality but does not alter the data itself.       
                    
                    <output>
                        ```{{"major": ["Misrepresentation"], "minor": ["Missing Axis", "Distractive Value Labels"], "potentials": []}}```
                    </output>
                    
                </example>
            """
        },
        {
            "type": "text",
            "text": "Remember to think step-by-step and consider all aspects of the chart before providing your final analysis and output."
        },
    ]


def get_key_issues_position_with_cl(image, key_issues, actual_box_width, actual_box_height):
    print("Actual Width: " + str(int(actual_box_width)))
    print("Actual Height: " + str(int(actual_box_height)))
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


def get_issue_details_prompt_cl(key_issues, image):
    pitfalls_text = generate_pitfalls_text()
    example_image = "https://firebasestorage.googleapis.com/v0/b/chartinsight-3f620.appspot.com/o/imagesimg-10.jpeg?alt=media&token=0b39a841-ada1-4a69-9bcf-b658dbc30446"
    return [
        {
            "type": "text",
            "text": "Here is the image URL you need to analyze: "
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
                You have identified the following key issues in the provided chart:
                <identified_issues>
                    {', '.join(key_issues)}.
                </identified_issues>
            """
        },
        {
            "type": "text",
            "text": f"""
                   Your task is to analyze this image and provide a detailed explanation of each identified issue in proper HTML format. Focus on why each issue could be misleading or incorrect. Use the following structure for each issue:
            """
        },
        {
            "type": "text",
            "text": f"""
                <br/><b>[issue number]. [issue name]:</b><br/>
                <b>- Definition:</b> [Definition of the issue]<br/>
                <b>- Issue:</b> [Description of the issue with examples]<br/>
                <b>- Why it's misleading:</b> [Explanation of why this issue is misleading or incorrect]<br/>
            """
        },
        {
            "type": "text",
            "text": f"""
                For each identified issue:
                    1. Provide a clear definition of the issue based on data visualization best practices.
                    2. Describe how this issue manifests in the given chart, providing specific examples from the image.
                    3. Explain why this issue is misleading or incorrect, focusing on how it could lead to misinterpretation of the data.
            """
        },
        {
            "type": "text",
            "text": "Ensure your response is in valid HTML and adheres strictly to this format. Do not include additional text or HTML block formatting."
        },
        {
            "type": "text",
            "text": "Think through each issue step-by-step, considering its impact on data interpretation and viewer understanding. Provide a comprehensive analysis for each identified issue, maintaining a clear and professional tone throughout your explanation."
        },
        {
            "type": "text",
            "text": "Begin your analysis now, starting with the first identified issue and proceeding through all listed issues in order."
        },
        {
            "type": "text",
            "text": f"""
                    <example>
                        Here is an example.
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
                        <br/><b>1. Missing Axis:</b><br/>
                        <br/><b>- Definition:</b> An axis is a scale used to represent the numerical values in a data visualization. Missing an axis can make it difficult to understand the actual data being presented.<br/>
                        <br/><b>- Issue:</b> In this chart, there are no visible numerical scales or axes. The percentages for Trump and Clinton are presented without any reference to the total or the scale used.<br/>
                        <br/><b>- Why it's misleading:</b> Without clear axes, the viewer cannot determine the full context of the data. The percentages appear to be arbitrary and could be interpreted as representing different metrics, such as vote share, favorability, or some other measure. This lack of context makes it difficult to draw accurate conclusions from the information provided.<br/>
                        
                        <br/><b>2. Misrepresentation:</b><br/>
                        <br/><b>- Definition:</b> Misrepresentation occurs when data is presented in a way that distorts or exaggerates the actual information, leading to an inaccurate interpretation.<br/>
                        <br/><b>- Issue:</b> The chart represents the percentages for Trump and Clinton in a way that appears to imply a significant lead for Trump, even though the difference between the two is only 2 percentage points.<br/>
                        <br/><b>- Why it's misleading:</b> By emphasizing the Trump percentage with a larger, bolder font and a prominent "45%" label, while downplaying the Clinton percentage, the chart creates a visual impression of a larger gap between the two candidates. This misrepresentation of the data can lead the viewer to conclude that Trump has a much stronger lead than the actual 2-point difference suggests.<br/>
                        
                        <br/><b>3. Distractive Value Labels:</b><br/>
                        <br/><b>- Definition:</b> Value labels are numeric or textual annotations used to provide specific data points within a visualization. Distractive value labels are those that draw unnecessary attention or clutter the chart, making it harder to interpret the overall information.<br/>
                        <br/><b>- Issue:</b> In this chart, the large "45%" and "43%" labels for Trump and Clinton, respectively, are distracting and dominate the visual presentation.<br/>
                        <br/><b>- Why it's misleading:</b> The oversized value labels draw the viewer's attention away from the overall context and proportions of the data. This can lead to a focus on the specific percentages rather than the relationship between the two candidates, potentially skewing the interpretation of the data.<br/>
                        
                        <br/><b>4. Missing Units:</b><br/>
                        <br/><b>- Definition:</b> Units are the measurement or scale used to represent the data in a visualization. Missing units can make it difficult to understand the true meaning and scale of the data.<br/>
                        <br/><b>- Issue:</b> The chart does not indicate the units or scale for the percentages presented. It is unclear whether these are vote shares, favorability ratings, or some other metric.<br/>
                        <br/><b>- Why it's misleading:</b> Without clearly defined units, the viewer cannot accurately interpret the significance of the percentages. The lack of units makes it impossible to compare the data to other relevant information or to draw meaningful conclusions about the underlying data.<br/>
                        
                        <br/><b>5. Missing Title:</b><br/>
                        <br/><b>- Definition:</b> A title is a concise, descriptive label that explains the overall purpose and context of a data visualization.<br/>
                        <br/><b>- Issue:</b> The chart does not have a title, leaving the viewer without any clear indication of what the data represents or the purpose of the visualization.<br/>
                        <br/><b>- Why it's misleading:</b> Without a title, the viewer is left to make their own assumptions about the data and its context. This can lead to misinterpretations or draw attention to irrelevant details, rather than focusing on the intended message or analysis.<br/>
                        
                        <br/><b>6. Violating Color Convention:</b><br/>
                        <br/><b>- Definition:</b> Color conventions in data visualization refer to the established practice of using specific colors to represent certain political affiliations or entities.<br/>
                        <br/><b>- Issue:</b> In this chart, the colors used for the Trump and Clinton percentages do not follow the typical color conventions for political parties in the United States. Trump's percentage is presented in red, while Clinton's is in blue.<br/>
                        <br/><b>- Why it's misleading:</b> Viewers are accustomed to seeing the Democratic Party represented by blue and the Republican Party represented by red. By reversing these colors, the chart creates a visual inconsistency that can be confusing and misleading, potentially causing the viewer to misinterpret the data or the political affiliations of the candidates.<br/>
                        
                        <br/><b>7. Hidden Uncertainty:</b><br/>
                        <br/><b>- Definition:</b> Uncertainty refers to the degree of confidence or reliability associated with the data being presented. Hiding this uncertainty can lead to overstating the significance or accuracy of the information.<br/>
                        <br/><b>- Issue:</b> The chart does not provide any indication of the uncertainty or margin of error associated with the percentages shown for Trump and Clinton.<br/>
                        <br/><b>- Why it's misleading:</b> Without information about the uncertainty or statistical significance of the data, the viewer may interpret the percentages as precise and definitive, when in reality, there may be a level of error or variability that should be taken into consideration. This lack of transparency can lead to an overconfident interpretation of the data and potentially incorrect conclusions.<br/>
                    </example
                """
        },
    ]


def get_issue_improvements_prompt_cl(key_issues, image):
    pitfalls_text = generate_pitfalls_text()
    example_image = "https://firebasestorage.googleapis.com/v0/b/chartinsight-3f620.appspot.com/o/imagesimg-10.jpeg?alt=media&token=0b39a841-ada1-4a69-9bcf-b658dbc30446"
    return [
        {
            "type": "text",
            "text": "Here is the chart image you need to analyze: "
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
                            You have identified the following key issues in the provided chart:
                            <identified_issues>
                                {', '.join(key_issues)}.
                            </identified_issues>
                        """
        },
        {
            "type": "text",
            "text": f"""
                    Analyze the provided image and suggest specific improvements to help avoid or correct each identified issue. Use the following structure for each issue:
                """
        },
        {
            "type": "text",
            "text": f"""
                    <br/><b>[issue number]. [issue name]:</b><br/>
                    <b>- Suggested Improvement:</b> [Suggestions on how to improve or avoid this issue]<br/><br/>
                """
        },

        {
            "type": "text",
            "text": """
                    Ensure your response adheres to the following guidelines:
                        1. Use valid HTML formatting.
                        2. Follow the specified output format strictly.
                        3. Do not include unnecessary additional text.
                        4. Do not use ```html block formatting.
                """
        },
        {
            "type": "text",
            "text": """
                    Think through each issue step-by-step, considering:
                        1. The nature of the issue and how it manifests in the chart.
                        2. Potential solutions that could address the problem.
                        3. How these solutions would improve the chart's accuracy and clarity.
                """
        },
        {
            "type": "text",
            "text": f"""
                        <example>
                            Here is an example.
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
                        <br/><b>1. Missing Axis:</b><br/>
                        <br/><b>- Definition:</b> An axis is a numerical scale used to represent the data values in a data visualization. The absence of clear axes can make it difficult to interpret the actual data being presented.<br/>
                        <br/><b>- Issue:</b> In this chart, there are no visible numerical scales or axes. The percentages for Trump and Clinton are presented without any reference to the total or the scale used.<br/>
                        <br/><b>- Why it's misleading:</b> Without clear axes, the viewer cannot determine the full context of the data. The percentages appear to be arbitrary and could be interpreted as representing different metrics, such as vote share, favorability, or some other measure. This lack of context makes it challenging to draw accurate conclusions from the information provided.<br/>
                        <br/><b>- Suggested Improvement:</b> Add clear numerical axes to the chart, either along the x-axis (for the percentages) or as a separate y-axis. This will provide the necessary context and scale for interpreting the data accurately.<br/>
                        
                        <br/><b>2. Misrepresentation:</b><br/>
                        <br/><b>- Definition:</b> Misrepresentation occurs when data is presented in a way that distorts or exaggerates the actual information, leading to an inaccurate interpretation.<br/>
                        <br/><b>- Issue:</b> The chart represents the percentages for Trump and Clinton in a way that appears to imply a significant lead for Trump, even though the difference between the two is only 2 percentage points.<br/>
                        <br/><b>- Why it's misleading:</b> By emphasizing the Trump percentage with a larger, bolder font and a prominent "45%" label, while downplaying the Clinton percentage, the chart creates a visual impression of a larger gap between the two candidates. This misrepresentation of the data can lead the viewer to conclude that Trump has a much stronger lead than the actual 2-point difference suggests.<br/>
                        <br/><b>- Suggested Improvement:</b> Present the percentages for Trump and Clinton in a more balanced and proportional manner, without exaggerating the difference between the two. This could involve using a bar chart or other visualization style that focuses on the relative relationship between the data points rather than emphasizing a specific candidate.<br/>
                        
                        <br/><b>3. Distractive Value Labels:</b><br/>
                        <br/><b>- Definition:</b> Value labels are numeric or textual annotations used to provide specific data points within a visualization. Distractive value labels are those that draw unnecessary attention or clutter the chart, making it harder to interpret the overall information.<br/>
                        <br/><b>- Issue:</b> In this chart, the large "45%" and "43%" labels for Trump and Clinton, respectively, are distracting and dominate the visual presentation.<br/>
                        <br/><b>- Why it's misleading:</b> The oversized value labels draw the viewer's attention away from the overall context and proportions of the data. This can lead to a focus on the specific percentages rather than the relationship between the two candidates, potentially skewing the interpretation of the data.<br/>
                        <br/><b>- Suggested Improvement:</b> Reduce the size and prominence of the individual percentage labels, and instead integrate them more seamlessly into the chart design. The emphasis should be on the overall comparison rather than the specific numeric values.<br/>
                        
                        <br/><b>4. Missing Units:</b><br/>
                        <br/><b>- Definition:</b> Units are the measurement or scale used to represent the data in a visualization. Missing units can make it difficult to understand the true meaning and scale of the data.<br/>
                        <br/><b>- Issue:</b> The chart does not indicate the units or scale for the percentages presented. It is unclear whether these are vote shares, favorability ratings, or some other metric.<br/>
                        <br/><b>- Why it's misleading:</b> Without clearly defined units, the viewer cannot accurately interpret the significance of the percentages. The lack of units makes it impossible to compare the data to other relevant information or to draw meaningful conclusions about the underlying data.<br/>
                        <br/><b>- Suggested Improvement:</b> Clearly indicate the units or scale being used for the percentages, such as "Percentage of Voters" or "Approval Rating." This will help the viewer understand the context and meaning of the data.<br/>
                        
                        <br/><b>5. Missing Title:</b><br/>
                        <br/><b>- Definition:</b> A title is a concise, descriptive label that explains the overall purpose and context of a data visualization.<br/>
                        <br/><b>- Issue:</b> The chart does not have a title, leaving the viewer without any clear indication of what the data represents or the purpose of the visualization.<br/>
                        <br/><b>- Why it's misleading:</b> Without a title, the viewer is left to make their own assumptions about the data and its context. This can lead to misinterpretations or draw attention to irrelevant details, rather than focusing on the intended message or analysis.<br/>
                        <br/><b>- Suggested Improvement:</b> Add a concise, descriptive title to the chart that clearly explains the purpose and content of the data being presented. This will provide the necessary context for the viewer to interpret the information accurately.<br/>
                        
                        <br/><b>6. Violating Color Convention:</b><br/>
                        <br/><b>- Definition:</b> Color conventions in data visualization refer to the established practice of using specific colors to represent certain political affiliations or entities.<br/>
                        <br/><b>- Issue:</b> In this chart, the colors used for the Trump and Clinton percentages do not follow the typical color conventions for political parties in the United States. Trump's percentage is presented in red, while Clinton's is in blue.<br/>
                        <br/><b>- Why it's misleading:</b> Viewers are accustomed to seeing the Democratic Party represented by blue and the Republican Party represented by red. By reversing these colors, the chart creates a visual inconsistency that can be confusing and misleading, potentially causing the viewer to misinterpret the data or the political affiliations of the candidates.<br/>
                        <br/><b>- Suggested Improvement:</b> Use the standard color conventions for political affiliations in the United States, with the Democratic Party represented by blue and the Republican Party represented by red. This will align with the viewer's expectations and avoid any confusion or misinterpretation.<br/>
                        
                        <br/><b>7. Hidden Uncertainty:</b><br/>
                        <br/><b>- Definition:</b> Uncertainty refers to the degree of confidence or reliability associated with the data being presented. Hiding this uncertainty can lead to overstating the significance or accuracy of the information.<br/>
                        <br/><b>- Issue:</b> The chart does not provide any indication of the uncertainty or margin of error associated with the percentages shown for Trump and Clinton.<br/>
                        <br/><b>- Why it's misleading:</b> Without information about the uncertainty or statistical significance of the data, the viewer may interpret the percentages as precise and definitive, when in reality, there may be a level of error or variability that should be taken into consideration. This lack of transparency can lead to an overconfident interpretation of the data and potentially incorrect conclusions.<br/>
                        <br/><b>- Suggested Improvement:</b> Provide information about the margin of error, confidence intervals, or other statistical measures that indicate the level of uncertainty associated with the percentages. This will help the viewer understand the limitations and reliability of the data, and make more informed interpretations.<br/>
                    </example>
                """
        },
    ]


def get_corrected_image_prompt_cl(key_issues, image):
    example_image = "https://firebasestorage.googleapis.com/v0/b/chartinsight-3f620.appspot.com/o/imagesimg-10.jpeg?alt=media&token=0b39a841-ada1-4a69-9bcf-b658dbc30446"
    return [
        {
            "type": "text",
            "text": "Follow these instructions carefully: "
        },
        {
            "type": "text",
            "text": "1. Analyze the following image URL:"
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
                    2. Address the following key issues identified in the chart:
                    <issues>
                        {', '.join(key_issues)}.
                    </issues>
                """
        },
        {
            "type": "text",
            "text": f"""
                3. Generate Python code using matplotlib that resolves all of the identified issues. Ensure your code is bug-free, handles all possible errors, and is ready for dynamic execution environments.
            """
        },
        {
            "type": "text",
            "text": f"""
                4. Use the following predefined aliases in your code:
                   - 'plt' for matplotlib.pyplot
                   - 'np' for numpy
                   - 'pd' for pandas
                   - 'mdates' for matplotlib.dates
                   - 'ticker' for matplotlib.ticker
                   - 'DateFormatter' for matplotlib.dates.DateFormatter
                   - 'MonthLocator' for matplotlib.dates.MonthLocator
                   - 'YearLocator' for matplotlib.dates.YearLocator
                   - 'DayLocator' for matplotlib.dates.DayLocator
                   - 'sns' for seaborn
                 Ensure that 'YearLocator', 'MonthLocator', 'DayLocator', and 'DateFormatter' are referenced from 'mdates' (not 'ticker'), and 'MaxNLocator' is referenced from 'ticker'.
            """
        },
        {
            "type": "text",
            "text": f"""
                5. Implement robust error handling:
                   - Check that all data arrays are of the same length
                   - Provide fallbacks for missing datasets or deprecated functions
                   - Handle multi-axes plots and ensure legends are created for all relevant elements
                   - if you need to use 'seaborn' style then use 'seaborn-v0_8'.
                   - Handle unterminated string literal error
                   - Please don't use geopandas dataset.
                   - Handle cannot import name 'ThousandFormatter' from 'matplotlib.ticker'
                   - Address potential issues like missing data, incorrect data types, mismatched array lengths, improper axis scaling, etc.
                   - operands could not be broadcast together with shapes
                Ensure the code is bug-free, handles all possible errors, and is ready for dynamic execution environments.
            """
        },
        {
            "type": "text",
            "text": f"""
                6. Do not rely on external data sources. If required data is unavailable, use dummy data that accurately reflects the expected format and structure.
            """
        },
        {
            "type": "text",
            "text": f"""
                    7. Ensure all variable names adhere to Python naming conventions (alphanumeric characters and underscores only).
                """
        },
        {
            "type": "text",
            "text": f"""
                8. Structure your code for clarity and readability:
                   - Use meaningful variable names
                   - Add comments to explain complex operations
                   - Organize code into logical sections (e.g., data preparation, plotting, formatting)
            """
        },
        {
            "type": "text",
            "text": f"""
                   9. Provide your complete Python code solution within <code> tags. Ensure the code is fully functional and ready for immediate execution.
            """
        },
        {
            "type": "text",
            "text": f"""
                10. After the code, provide a brief explanation of how your solution addresses each of the identified issues within <explanation> tags.
            """
        },
        {
            "type": "text",
            "text": f"""
                Remember, your goal is to produce a visualization that is accurate, clearly labeled, and free of any misleading elements while addressing all the identified issues. 
            """
        },
        {
            "type": "text",
            "text": f"""
                        <example>
                            Here is an example.
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
                        <code>
                            import numpy as np
                            import matplotlib.pyplot as plt
                            from matplotlib.ticker import MaxNLocator

                            # Set style for better visualization
                            plt.style.use('seaborn-v0_8')

                            # Sample data with confidence intervals (95% CI typically ±3-4% for polls)
                            candidates = ['Trump', 'Clinton']
                            poll_values = np.array([45, 43])
                            confidence_interval = 3.5  # Standard 95% CI for most polls
                            error_margins = np.array([confidence_interval] * len(candidates))

                            # Create figure and axis with adjusted size
                            fig, ax = plt.subplots(figsize=(12, 6))

                            # Create horizontal bar chart
                            y_pos = np.arange(len(candidates))
                            bars = ax.barh(y_pos, poll_values, 
                                        height=0.6,
                                        color=['#FF4040', '#4080FF'])

                            # Add error bars
                            ax.errorbar(poll_values, y_pos, 
                                        xerr=error_margins,
                                        fmt='none',
                                        color='black',
                                        capsize=5,
                                        capthick=1.5,
                                        elinewidth=1.5)

                            # Customize the plot
                            ax.set_title('Colorado Presidential Poll Results\nOctober 2016', 
                                        pad=20, fontsize=14, fontweight='bold')
                            ax.set_xlabel('Support (%)', fontsize=12)
                            ax.set_ylabel('Candidates', fontsize=12)

                            # Set axis limits to prevent misleading scale
                            ax.set_xlim(0, 100)

                            # Add value labels on the bars
                            for i, bar in enumerate(bars):
                                width = bar.get_width()
                                ax.text(width + 2, bar.get_y() + bar.get_height()/2,
                                        f'{{poll_values[i]}}% ± {{error_margins[i]}}%',
                                        va='center')

                            # Customize y-axis
                            ax.set_yticks(y_pos)
                            ax.set_yticklabels(candidates)

                            # Add source and methodology note
                            plt.figtext(0.05, 0.02,
                                        'Source: Reuters/Ipsos Poll\n'
                                        'Sample size: ~1000 likely voters\n'
                                        'Margin of error: ±3.5% at 95% confidence level',
                                        fontsize=8)

                            # Adjust layout with specific margins
                            plt.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.15)

                            plt.show()
                        </code>
                        <explanation>
                            The code addresses each identified issue:

                                1. Missing Axis: Added proper x-axis (Support %) and y-axis (Candidates) labels.

                                2. Misrepresentation: 
                                - Used horizontal bars for better readability
                                - Set x-axis scale to 0-100% to prevent visual distortion
                                - Maintained proper proportions between values

                                3. Distractive Value Labels:
                                - Placed value labels outside the bars
                                - Included error margins in the labels
                                - Used consistent formatting

                                4. Missing Units:
                                - Added % symbol to all values
                                - Clearly labeled axis units

                                5. Missing Title:
                                - Added clear title with date
                                - Included subtitle for context

                                6. Dubious Data:
                                - Added source attribution
                                - Included sample size information
                                - Added methodology notes

                                7. Hidden Uncertainty:
                                - Displayed error margins (±3.5%)
                                - Added error bars to show confidence intervals
                                - Included explanation of confidence level

                                Additional improvements:
                                - Used appropriate colors for party identification
                                - Implemented clean, professional design
                                - Added proper spacing and layout
                                - Included comprehensive documentation
                        </explanation>
                    </example>
                """
        },
    ]


def get_image_error_correction_cl(generated_code, error_message):
    return [
        {
            "type": "text",
            "text": "Here is the Python code that caused an error:"
        },
        {
            "type": "text",
            "text": f"""
                <generated_code>
                    {generated_code}
                </generated_code>
            """
        },
        {
            "type": "text",
            "text": "The error message received was:"
        },
        {
            "type": "text",
            "text": f"""
                <error_message>
                    {error_message}
                </error_message>
            """
        },
        {
            "type": "text",
            "text": f"""
                    Analyze the provided code carefully. Look for the following types of issues:
                        1. Syntax errors
                        2. Missing required arguments in function calls
                        3. Incorrect data handling
                        4. Use of invalid or deprecated functions
                        5. Dependencies on external files or resources
            """
        },
        {
            "type": "text",
            "text": f"""
                When correcting the code:
                    1. Ensure all required arguments for functions are included
                    2. Replace deprecated methods with current best practices
                    3. Modify the code to generate data internally if it depends on external files
                    4. Provide alternative approaches to avoid dependencies that can't be resolved
                    5. Make sure the corrected code will run without any errors
            """
        },
        {
            "type": "text",
            "text": f"""
                Present your analysis and corrected code in the following format:
                
                <analysis>
                    Provide a brief explanation of the issues found in the original code and the changes made to correct them.
                </analysis>
                
                <corrected_code>
                    Insert the corrected Python code here. Ensure it's properly formatted and indented.
                </corrected_code>

            """
        },
        {
            "type": "text",
            "text": f"""
                   Remember:
                    - Please don't use geopandas dataset.
                    - Ensure functions like plt.annotate() include all required arguments
                    - Avoid any methods requiring external files
                    - Generate data internally or provide alternative approaches when necessary
                    - The goal is to produce code that will run without any errors
                    - if you need to use 'seaborn' style then use 'seaborn-v0_8'.
                    - Handle unterminated string literal error
                    - Handle cannot import name 'ThousandFormatter' from 'matplotlib.ticker'
                    
                    Provide your complete analysis and corrected code without any additional commentary. Also, Ensure the code is bug-free, handles all possible errors, and is ready for dynamic execution environments.
                """
        }
    ]


def generate_resolved_issues_prompt_cl(key_issues, main_image, corrected_image):
    return [
        {
            "type": "text",
            "text": "Here are the key issues that were identified in the original chart:"
        },
        {
            "type": "text",
            "text": f"""
                    You have identified the following key issues in the provided chart:
                    <identified_issues>
                        {', '.join(key_issues)}.
                    </identified_issues>
                """
        },
        {
            "type": "text",
            "text": "Please follow these steps: "
        },
        {
            "type": "text",
            "text": f"""
                    1. Carefully examine the original chart:
                    <main_image>
                """
        },
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": f"image/{get_image_type_from_url(main_image)}",
                "data": image_url_to_base64(main_image)
            },
        },
        {
            "type": "text",
            "text": f"""
                    </main_image>
                    2. Now, examine the corrected chart:
                    <corrected_image>
                """
        },
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": f"image/{get_image_type_from_url(corrected_image)}",
                "data": image_url_to_base64(corrected_image)
            },
        },
        {
            "type": "text",
            "text": f"""
                    </corrected_image>
                """
        },
        {
            "type": "text",
            "text": "3. Compare the two charts, focusing on the previously identified issues. Look for changes that address these specific problems."
        },
        {
            "type": "text",
            "text": "4. Determine which of the identified issues have been resolved in the corrected chart. An issue is considered resolved if the correction adequately addresses the problem and significantly improves the chart's accuracy, clarity, or effectiveness."
        },
        {
            "type": "text",
            "text": f"""
                    5. For each resolved issue, think about why it has been resolved. Consider:
                        - What specific changes were made?
                        - How do these changes address the original problem?
                        - How does the correction improve the chart's overall effectiveness or accuracy?
                """
        },
        {
            "type": "text",
            "text": f"""
                    6. Prepare your response in the following format:
                        <resolved_issues>
                        List the resolved issues, separated by commas
                        </resolved_issues>

                        <explanation>
                        Provide a detailed explanation for why each listed issue is considered resolved. Discuss the specific changes made and how they improve the chart.
                        </explanation>
                """
        },
        {
            "type": "text",
            "text": "Remember to be thorough in your analysis and clear in your explanations. Focus only on the issues that were originally identified and have been genuinely resolved in the corrected chart."
        }
    ]


def get_dataset_chart_generation_prompt_cl(columns, data_sample):
    return [
        {
            "type": "text",
            "text": "Follow these instructions carefully:"
        },
        {
            "type": "text",
            "text": f"""
                        1. Dataset Information:
                            The dataset contains the following columns:
                            <columns>
                                {columns}
                            </columns>

                            Here is the data:
                            <data_sample>
                                {data_sample}
                            </data_sample>
                    """
        },
        {
            "type": "text",
            "text": f"""
                        2. Data Analysis and Chart Selection:
                            Analyze the provided data sample and column names. Consider the data types, relationships between variables, and the number of dimensions. Based on this analysis, determine the most appropriate chart type (e.g., bar chart, line chart, scatter plot, pie chart) to represent the data effectively.
                    """
        },
        {
            "type": "text",
            "text": f"""
                            3. Python Code Generation: Generate Python code using matplotlib and seaborn to visualize the data. Adhere to the following guidelines:
                                a) Use the predefined aliases: 'plt' for matplotlib.pyplot, 'np' for numpy, 'pd' for pandas, 'sns' for seaborn, 'mdates' for matplotlib.dates, and 'ticker' for matplotlib.ticker.
                                b) Import 'DateFormatter', 'MonthLocator', 'YearLocator', and 'DayLocator' from 'mdates', and 'MaxNLocator' from 'ticker'.
                                c) Follow Python naming conventions: use only alphanumeric characters and underscores for variable names.
                                d) Ensure the code has no syntax errors and can execute without manual intervention.
                    """
        },
        {
            "type": "text",
            "text": f"""
                            4. Data Handling and Visualization Requirements:
                                a) Include all columns and data points from the dataset in the chart.
                                b) Handle missing or incomplete data by using appropriate techniques such as interpolation, backfilling, or explicit marking on the chart.
                                c) Ensure flexibility to handle various data types and structures.
                                d) Generate single-axis or multi-axis plots as appropriate for the data.
                                e) Automatically check and resolve any mismatches in array or data column lengths.
                                f) Clearly label the chart, including axes, title, and legend if applicable.
                    """
        },
        {
            "type": "text",
            "text": f"""
                            5. Error Handling and Data Integrity:
                                a) Implement checks for potential issues such as missing data, incorrect data types, or inconsistent lengths.
                                b) Resolve any detected problems automatically or provide appropriate warnings while continuing to generate the graph.
                                c) Ensure that the final graph is complete, accurate, and includes all relevant data points.
                                d) Clearly indicate any missing or incorrect data points without omitting valid data.
                                e) 'seaborn' is not a valid package style, path of style file, URL of style file, or library style name (library styles are listed in `style.available`)
                                f) Handle unterminated string literal error
                                g) Handle cannot import name 'ThousandFormatter' from 'matplotlib.ticker'
                                h) Casting to unit-less dtype 'datetime64' is not supported. Pass e.g. 'datetime64[ns]' instead.
                    """
        },

        {
            "type": "text",
            "text": f"""
                        6. Output Format:
                            Provide your response in the following format:

                            <analysis>
                                [Your analysis of the dataset and justification for the chosen chart type]
                            </analysis>

                            <code>
                                [Your generated Python code for data visualization]
                            </code>
                    """
        },
        {
            "type": "text",
            "text": "Remember to think through each step carefully to ensure that your generated code meets all the specified requirements and produces an accurate, comprehensive visualization of the provided data."
        },
        {
            "type": "text",
            "text": f"""
                         <example>
                            Here is an example.

                            A dataset contains the following columns: ['Candidate', 'Percentage'].
                            Here is a sample of the data: {{'Candidate': {{0: 'Trump', 1: 'Clinton', 2: 'Tarun', 3: 'Jannat'}}, 'Percentage': {{0: 0.2, 1: 0.2, 2: 0.22, 3: 0.38}}}}.

                            <analysis>
                                Based on the dataset, the most appropriate chart is a **bar chart**.
                                ### Why This Chart is Appropriate:

                                1. **Handles Categorical Data:**
                                    - The 'Candidate' column is categorical, making a bar chart the most appropriate choice for comparing individual values across categories.
                                    - A bar chart effectively represents the proportion of votes for each candidate.

                                2. **Ensures All Data is Represented:**
                                    - Each candidate and their corresponding percentage is displayed as a separate bar.
                                    - No data is omitted, ensuring full representation of the dataset.

                                3. **Avoids Common Pitfalls:**
                                    - Pie charts are not used here because they are only suitable for part-to-whole relationships, and this data does not sum to 100%.
                                    - Line charts are avoided as they are more suited to continuous data over a time series, which is not applicable here.

                                4. **Handles Missing Data Dynamically:**
                                    - Any missing values in the 'Percentage' column can be filled with defaults (e.g., 0) or interpolated.
                                    - Warnings for missing categories can be provided, ensuring that any issues are clearly indicated.

                                5. **Clarity and Accessibility:**
                                    - Bars are labeled with exact percentages, reducing ambiguity and enhancing interpretability.
                                    - The 'viridis' color palette ensures accessibility for color-blind viewers.

                                6. **Alternative Chart Consideration:**
                                    - A scatter plot was considered but deemed inappropriate because scatter plots are designed to show relationships between two numerical variables, which is not applicable here.
                                    - A stacked bar chart could have been used but would unnecessarily complicate the visualization.

                                7. **Final Outcome:**
                                    - The bar chart ensures a clean, clear, and proportional representation of the data, highlighting differences between candidates effectively.

                            </analysis>

                            <code>
                                import matplotlib.pyplot as plt
                                import pandas as pd
                                import numpy as np
                                import seaborn as sns

                                [rest of the code]
                            </code>
                    """
        }
    ]


def get_dataset_from_the_chart_cl(image, key_issues):
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


def generate_image_with_cl(dataset, image, key_issues):
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
                        
                        Error Handling:
                            1. Ensure that all variable names adhere to Python's naming conventions, meaning no special characters like '&' or '%'. 
                            2. Variable names should only contain alphanumeric characters and underscores ('_'). 
                            4. Handle unterminated string literal error
                            5. Handle 'Text' object has no property 'padding'
                            6. Ensure that the code works directly with the provided dataset, which has tagged with <corrected_dataset>. there is no file path. use direct dataset which has provided.
                            7. 'pandas' has no attribute 'StringIO'
                        
                        Remember to think through each step carefully and ensure that your solution effectively addresses all the identified issues while accurately representing the data from the corrected dataset. Also, Ensure the code is bug-free, handles all possible errors, and is ready for dynamic execution environments.
                                 
                    """
        },
    ]
