from openai import OpenAI
from utils import settings


def ask_chatgpt(question):
    """Function to ask ChatGPT a question and return the response."""
    
    client = OpenAI(
        api_key=settings.config["settings"]["openai"].get("api_key", None)
    )

    response = client.chat.completions.create(
        model="gpt-4o",  # You can also use "gpt-4" if you have access to it
        messages=[
            {
                "role": "system",
                "content": f"""
                    You are a youtube short content creator.
                    Your role is to simply return the text to be said in the short.
                    Remember that the first attraction is imperative, so make the 
                    first sentece of the short appealing to the viewer. The content
                    must cover at least 45 seconds but NO MORE than 1 minute. Text MUST be
                    clean, no emojis. And make it concise the text to be said, we dont want to have
                    a long short.
                """},
            {"role": "user", "content": question},
        ],
        max_tokens=150  
    )
    # Extract the response content
    answer = response.choices[0].message.content
    return answer
