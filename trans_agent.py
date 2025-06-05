
import os
from dotenv import load_dotenv
import google.generativeai as genai
import chainlit as cl
import json

# Load environment variables from .env file
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is missing in .env file")

# Configure Gemini API
genai.configure(api_key=gemini_api_key)

# Chat start handler
@cl.on_chat_start
async def start():
    cl.user_session.set("chat_history", [])
    await cl.Message(
        content="**WELCOME to the Translator Agent By Samina Saad!**\n\nPlease tell me **what you want to translate** and **into which language**."
    ).send()

# Message handler
@cl.on_message
async def on_message(message: cl.Message):
    msg = cl.Message(content="🔄 Translating... Please wait!")
    await msg.send()

    history = cl.user_session.get("chat_history") or []
    history.append({"role": "user", "content": message.content})

    try:
        # Call Google Gemini API for translation
        response = genai.GenerativeModel('gemini-1.5-flash').generate_content(message.content)
        
        response_content = response.text
        msg.content = response_content
        await msg.update()

        # Save assistant's reply to history
        history.append({"role": "assistant", "content": response_content})
        cl.user_session.set("chat_history", history)

    except Exception as e:
        msg.content = f"❌ Error: {str(e)}"
        await msg.update()

# Chat end handler
@cl.on_chat_end
async def on_chat_end():
    history = cl.user_session.get("chat_history") or []
    with open("translation_chat_history.json", "w", encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    print("✅ Chat history saved.")
