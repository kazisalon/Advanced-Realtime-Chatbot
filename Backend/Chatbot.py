from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load variables from the .env file.
env_vars = dotenv_values(".env")

# Get user credentials like username, Assistant name, and API key.
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq client using the provided API key.
client = Groq(api_key=GroqAPIKey)  # Fixed: Removed extra parentheses

# Initialize an empty list to store chat messages.
messages = []

# System message that provides context to be of chatbot about its role and behavior.
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

# Define system chatbot settings.
SystemChatBot = [
    {"role": "system", "content": System}
]  # Fixed: Corrected variable name case

try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)  # Load existing messages from the chat log.
except FileNotFoundError:
    # If the chat log doesn't exist, create an empty JSON file to store chat logs.
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)


# Function to get real-time date and time information.
def RealtimeInformation():
    current_date_time = datetime.datetime.now()  # Get the current date and time.
    day = current_date_time.strftime("%A")  # Day of the week.
    date = current_date_time.strftime("%d")  # Day of the month.
    month = current_date_time.strftime("%B")  # Month name.
    year = current_date_time.strftime("%Y")  # Year.
    hour = current_date_time.strftime("%H")  # Hour in 24-hour format.
    minute = current_date_time.strftime("%M")  # Minute.
    second = current_date_time.strftime("%S")  # Second.

    # Format the information into a string
    data = f"Current date and time information if needed by\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Hour: {hour}\nMinute: {minute}\nSecond: {second}"
    return data


def AnswerModifier(Answer):
    lines = Answer.split("\n")  # Split the response into lines.
    non_empty_lines = [line for line in lines if line.strip()]  # Remove empty lines.
    modified_answer = "\n".join(
        non_empty_lines
    )  # Join the cleaned lines back together.
    return modified_answer


# Main chatbot function to handle user queries.
def ChatBot(Query):
    """This function sends the user's query to the chatbot and returns the AI's response."""

    try:
        # Load the existing chat log from the JSON file.
        with open(r"Data\ChatLog.json", "r") as f:  # Fixed: Corrected path separator
            messages = load(f)

        # Append the user's query to the messages list.
        messages.append({"role": "user", "content": f"{Query}"})

        # Make a request to the Groq API for a response.
        completion = client.chat.completions.create(
            model="llama-70b-8192",  # Specify the AI model to use.
            messages=SystemChatBot
            + [{"role": "system", "content": RealtimeInformation()}]
            + messages,  # Include context
            max_tokens=1024,  # Limit the maximum tokens in the response.
            temperature=0.7,  # Adjust response randomness (higher means more random).
            top_p=1,  # Use nucleus sampling to control diversity.
            stream=True,  # Enable streaming response.
            stop=None,  # Allow the model to determine when to stop.
        )

        # Initialize an empty string to store the AI's response.
        Answer = ""

        # Process the stream/response chunks.
        for chunk in completion:
            if chunk.choices[
                0
            ].delta.content:  # Check if there's content in the current chunk.
                Answer = chunk.choices[0].delta.content

        Answer = Answer.replace(
            "</s>", ""
        )  # Clean up any unwanted tokens from the response.

        # Append the completed chat to the chat file.
        messages.append({"role": "assistant", "content": Answer})

        # Save the updated chat log to the JSON file.
        with open(r"Data\ChatLog.json", "w") as f:  # Fixed: Corrected path separator
            dump(messages, f, indent=4)

        # Return the formatted Answer
        return AnswerModifier(Answer=Answer)

    except Exception as e:
        print(f"Error: {e}")
        # Handle error by updating the exception and resetting the chat log
        with open(r"Data\ChatLog.json", "w") as f:  # Fixed: Corrected path separator
            dump([], f, indent=4)
        return ChatBot(Query)  # Retry the query after resetting the log.


# Main program entry point
if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")  # Prompt the user for a question
        print(ChatBot(user_input))
