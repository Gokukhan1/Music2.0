import random
import requests
import time
import asyncio

from pyrogram import filters
from pyrogram.enums import PollType, ChatAction
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ERAVIBES import app

# Module metadata
__MODULE__ = "Qᴜɪᴢ"
__HELP__ = """
/quiz - Sᴛᴀʀᴛs ᴛʜᴇ ǫᴜɪᴢ ᴍᴏᴅᴇ. Wʜᴇɴ ʏᴏᴜ ʀᴜɴ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ, ɪᴛ ᴡɪʟʟ ᴘʀᴏᴠɪᴅᴇ ʏᴏᴜ ᴡɪᴛʜ ʙᴜᴛᴛᴏɴs ᴛᴏ sᴇʟᴇᴄᴛ ᴛʜᴇ ǫᴜɪᴢ ɪɴᴛᴇʀᴠᴀʟ.

/quiz [on/off] - 
   • **On**: Sᴇʟᴇᴄᴛ ᴛʜᴇ ɪɴᴛᴇʀᴠᴀʟ (30 sᴇᴄᴏɴᴅs, 1 ᴍɪɴᴜᴛᴇ, 5 ᴍɪɴᴜᴛᴇs, 10 ᴍɪɴᴜᴛᴇs).
   • **Off**: Sᴛᴏᴘ ᴛʜᴇ ǫᴜɪᴢ ʟᴏᴏᴘ.
   • Qᴜɪᴢᴢᴇs ᴡɪʟʟ ʙᴇ sᴇɴᴛ ᴀᴛ ʏᴏᴜʀ ᴄʜᴏsᴇɴ ɪɴᴛᴇʀᴠᴀʟ ᴜɴᴛɪʟ ʏᴏᴜ sᴛᴏᴘ ɪᴛ.

• **Intervals:**
   - 30 seconds
   - 1 minute
   - 5 minutes
   - 10 minutes
   • **Stop**: Pʀᴇss ᴛʜᴇ "Sᴛᴏᴘ Qᴜɪᴢ" ʙᴜᴛᴛᴏɴ ᴛᴏ sᴛᴏᴘ ᴛʜᴇ ǫᴜɪᴢ ʟᴏᴏᴘ.
"""

# Dictionary to track user quiz loops and their intervals
quiz_loops = {}

# Function to fetch a quiz question from the API
async def fetch_quiz_question():
    categories = [9, 17, 18, 20, 21, 27]  # Quiz categories
    url = f"https://opentdb.com/api.php?amount=1&category={random.choice(categories)}&type=multiple"
    response = requests.get(url).json()

    question_data = response["results"][0]
    question = question_data["question"]
    correct_answer = question_data["correct_answer"]
    incorrect_answers = question_data["incorrect_answers"]

    all_answers = incorrect_answers + [correct_answer]
    random.shuffle(all_answers)

    cid = all_answers.index(correct_answer)

    return question, all_answers, cid

# Function to send a quiz poll
async def send_quiz_poll(client, message):
    question, all_answers, cid = await fetch_quiz_question()

    await app.send_poll(
        chat_id=message.chat.id,
        question=question,
        options=all_answers,
        is_anonymous=False,
        type=PollType.QUIZ,
        correct_option_id=cid,
    )

# /quiz command to show time interval options
@app.on_message(filters.command(["quiz", "uiz"], prefixes=["/", "!", ".", "Q", "q"]))
async def quiz(client, message):
    user_id = message.from_user.id

    # Creating time interval buttons and stop button
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Every 30 seconds", callback_data="30_sec")],
            [InlineKeyboardButton("Every 1 minute", callback_data="1_min")],
            [InlineKeyboardButton("Every 5 minutes", callback_data="5_min")],
            [InlineKeyboardButton("Every 10 minutes", callback_data="10_min")],
            [InlineKeyboardButton("Stop Quiz", callback_data="stop_quiz")]
        ]
    )

    # Sending only the buttons, no extra text
    await message.reply_text("Select your preferred quiz interval:", reply_markup=keyboard)

# Handling button presses for time intervals
@app.on_callback_query(filters.regex(r"^\d+_sec$|^\d+_min$"))
async def start_quiz_loop(client, callback_query):
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    if user_id in quiz_loops:
        await callback_query.answer("Quiz loop is already running!", show_alert=True)
        return

    # Set interval based on button press
    if callback_query.data == "30_sec":
        interval = 30
        interval_text = "30 seconds"
    elif callback_query.data == "1_min":
        interval = 60
        interval_text = "1 minute"
    elif callback_query.data == "5_min":
        interval = 300
        interval_text = "5 minutes"
    elif callback_query.data == "10_min":
        interval = 600
        interval_text = "10 minutes"

    # Confirm that the quiz loop has started
    await callback_query.answer(f"Quiz loop started! You'll receive a quiz every {interval_text}.", show_alert=True)
    
    quiz_loops[user_id] = True  # Mark loop as running

    # Start the quiz loop based on the chosen interval
    while quiz_loops.get(user_id, False):
        await send_quiz_poll(client, callback_query.message)
        await asyncio.sleep(interval)  # Wait for the selected time interval

# Handling the stop button press
@app.on_callback_query(filters.regex("stop_quiz"))
async def stop_quiz_loop(client, callback_query):
    user_id = callback_query.from_user.id

    if user_id not in quiz_loops:
        await callback_query.answer("No quiz loop is running!", show_alert=True)
    else:
        quiz_loops.pop(user_id)  # Stop the loop
        await callback_query.answer("Quiz loop stopped!", show_alert=True)
