def learn_message_gpt_prompt(chat_histories):
    return [
        {
            "role": "system",
            "content": "You are an AI assistant responsible for extracting learning points from chat histories related to chart data. These learning points should be based on user messages and indicate improved understanding, corrected facts, insights, or new knowledge. Return only a valid JSON object containing learning points without any additional text or explanations."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Analyze the following chat history and extract relevant learning points related to chart data."
                },
                {
                    "type": "text",
                    "text": f"""
                        {chat_histories}
                    """
                },
                {
                    "type": "text",
                    "text": "Focus only on messages from the 'user' source to determine learning points. Consider messages where the user is learning, defining, understanding, or clarifying chart-related information."
                },
                {
                    "type": "text",
                    "text": "Extract only the learning points without any introductory phrases like 'The user learned that' or 'The user clarified that'. The output should be a list of direct insights or facts."
                },
                {
                    "type": "text",
                    "text": "Return the learning points in the following JSON format:"
                },
                {
                    "type": "text",
                    "text": """
                    {
                        "learning_points": [
                            "learning point 1",
                            "learning point 2",
                            ...
                        ]
                    }
                    """
                },
                {
                    "type": "text",
                    "text": "If no learning points are identified, return an empty array:"
                },
                {
                    "type": "text",
                    "text": """
                    {
                        "learning_points": []
                    }
                    """
                },
                {
                    "type": "text",
                    "text": "Ensure your response strictly follows the JSON format with no extra text or explanation."
                }
            ]
        }
    ]
