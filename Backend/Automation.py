# Import required libraries
from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

# Load environment variables from the .env file
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Define CSS classes for parsing specific elements in HTML content
classes = [
    "ZcWbF",
    "hgKElc",
    "LTKOO SY7ric",
    "ZOLcW",
    "gsrt vk_bk FzvWSb YwPhnf",
    "pclqee",
    "tw-Data-text tw-text-small tw-ta",
    "iZ6rdc",
    "OSurRd",
    "LkOO0 vLzy6d",
    "webanswers-webanswers_table_webanswers-table",
    "dDoNo ikb4Bb gsrt",
    "sXLaOe",
    "LWkfKe",
    "VQF4g",
    "qv3Wpe",
    "kno-rdesc",
    "SPZz6b",
]

# Define user-agent for making web requests
useragent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/100.0.4896.75 Safari/537.36"
)

# Initialize the Groq client
client = Groq(api_key=GroqAPIKey)

# List to store chatbot messages
messages = []

# System message to provide context to the chatbot
SystemChatBot = {
    "role": "system",
    "content": f"Hello, I am {os.environ.get('Username')}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc.",
}


def GoogleSearch(Topic):
    search(Topic)
    return True


def Content(Topic):
    def OpenNotepad(File):
        default_text_editor = "notepad.exe"
        subprocess.Popen([default_text_editor, File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})

        # Fixed Groq API call using the correct method
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[SystemChatBot] + messages,
            max_tokens=2048,
            temperature=0.8,
            top_p=1,
            stream=True,
        )

        Answer = ""
        for chunk in completion:
            if hasattr(chunk.choices[0], "delta") and chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("<\s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic = Topic.replace("Content ", "")
    ContentByAI = ContentWriterAI(Topic)

    with open(
        rf"Data/{Topic.lower().replace(' ', '_')}.txt", "w", encoding="utf-8"
    ) as file:
        file.write(ContentByAI)

    OpenNotepad(rf"Data/{Topic.lower().replace(' ', '_')}.txt")
    return True


def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True


def PlayYoutube(query):
    playonyt(query)
    return True


def OpenApp(app, sess=requests.Session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:

        def extract_Links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, "html.parser")
            links = soup.find_all("a", {"jsname": "UwCKNb"})
            return [link.get("href") for link in links]

        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers)

            if response.status_code == 200:
                return response.text
            return None

        html = search_google(app)
        if html:
            links = extract_Links(html)
            if links:
                webopen(links[0])
        return True


def CloseApp(app):
    if "chrome" in app.lower():
        return True
    close(app, match_closest=True, output=True, throw_error=True)
    return True


def System(command):
    if command == "mute":
        keyboard.press_and_release("volume mute")
    elif command == "unmute":
        keyboard.press_and_release("volume mute")
    elif command == "volume up":
        keyboard.press_and_release("volume up")
    elif command == "volume down":
        keyboard.press_and_release("volume down")
    return True


async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        if command.startswith("open "):
            if not any(skip in command for skip in ["open it", "open file"]):
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)

        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)

        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
            funcs.append(fun)

        elif command.startswith("content "):
            fun = asyncio.to_thread(Content, command)
            funcs.append(fun)

        elif command.startswith("google search "):
            fun = asyncio.to_thread(
                GoogleSearch, command.removeprefix("google search ")
            )
            funcs.append(fun)

        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(
                YouTubeSearch, command.removeprefix("youtube search ")
            )
            funcs.append(fun)

        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)

        else:
            print(f"No Function Found for: {command}")

    if funcs:
        results = await asyncio.gather(*funcs)
        for result in results:
            if isinstance(result, str):
                yield result
            else:
                yield result


async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True


if __name__ == "__main__":
    asyncio.run(
        Automation(
            [
                "open facebook",
                "open instagram",
                "open telegram",
                "play afsanay",
                "content song for me",
            ]
        )
    )
