def image_error_correction_gpt_prompt(generated_code, error_message):
    return [
        {
            "role": "system",
            "content": (
                "You are an expert in Python code analysis and correction. Your goal is to identify any issues in the provided Python code, "
                "and return a corrected version of the code that will run without errors. Ensure that deprecated methods and practices "
                "are not used, and suggest alternative methods where necessary. Ensure that all required arguments for functions are included."
            )
        },
        {
            "role": "user",
            "content": (
                f"Here is the Python code that caused an error:\n\n"
                f"```python\n{generated_code}\n```\n\n"
                f"The error message received was:\n\n"
                f"```{error_message}```\n\n"
                "Please analyze the provided code, identify any errors (such as missing required arguments for functions, incorrect data handling, "
                "invalid functions, or deprecated methods), and return a corrected version. Ensure that functions like `plt annotate()` include all required arguments, "
                "and that the code does not rely on deprecated functions like `gpd.read_file()` or any method requiring external files. Modify the code to generate data internally or provide an alternative approach to avoid such dependencies. "
                "Ensure that the corrected code runs without any errors."
            )
        }
    ]


def image_error_correction_cl_prompt(generated_code, error_message):
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
