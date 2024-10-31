from pyrogram import filters
from pyrogram.enums import ChatAction
from TheApi import api

from ERAVIBES import app
from config import BANNED_USERS


@app.on_message(filters.command(["etect", "t"], prefixes=["/", "!", ".", "D", "d"]) & ~BANNED_USERS)
async def chatgpt_chat_lang(bot, message):
    # Agar command ke baad koi text ya reply nahi diya gaya hai
    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply_text("**Provide text after command or reply to a message.**")
        return
    
    # User ke message ka text lena
    user_text = message.reply_to_message.text if message.reply_to_message and message.reply_to_message.text else " ".join(message.command[1:])

    # User input format
    user_input = f"""
    Sentences: {user_text}

    Mujhe yeh batana hai ki yeh kis language mein hai. Bas language ka name aur code, aur ek short chatbot jaisa reply do:
    
    Format:
    Lang : [language name]
    Code : [language code]
    Reply : [response in same language]

    Agar text mein sirf emoji hai to reply bhi wahi emoji mein dena.
    """

    # Code to call OpenAI API or other language detection API could go here
    # ...

    # Example Response (to simulate response handling)
    response_text = "Lang : English\nCode : en\nReply : Okay"  # Replace with actual response

    await message.reply_text(response_text)


@app.on_message(filters.command(["chatgpt", "ai", "ask"]) & ~BANNED_USERS)
async def chatgpt_chat(bot, message):
    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply_text(
            "Example:\n\n`/ai write simple website code using html css, js?`"
        )
        return

    if message.reply_to_message and message.reply_to_message.text:
        user_input = message.reply_to_message.text
    else:
        user_input = " ".join(message.command[1:])

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    results = api.chatgpt(user_input)
    await message.reply_text(results)


__MODULE__ = "CʜᴀᴛGᴘᴛ"
__HELP__ = """
/advice - ɢᴇᴛ ʀᴀɴᴅᴏᴍ ᴀᴅᴠɪᴄᴇ ʙʏ ʙᴏᴛ
/ai [ǫᴜᴇʀʏ] - ᴀsᴋ ʏᴏᴜʀ ǫᴜᴇsᴛɪᴏɴ ᴡɪᴛʜ ᴄʜᴀᴛɢᴘᴛ's ᴀɪ
/gemini [ǫᴜᴇʀʏ] - ᴀsᴋ ʏᴏᴜʀ ǫᴜᴇsᴛɪᴏɴ ᴡɪᴛʜ ɢᴏᴏɢʟᴇ's ɢᴇᴍɪɴɪ ᴀɪ
/bard [ǫᴜᴇʀʏ] -ᴀsᴋ ʏᴏᴜʀ ǫᴜᴇsᴛɪᴏɴ ᴡɪᴛʜ ɢᴏᴏɢʟᴇ's ʙᴀʀᴅ ᴀɪ"""
