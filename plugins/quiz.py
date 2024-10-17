import random
import requests
import time
import asyncio

from pyrogram import filters
from pyrogram.enums import PollType, ChatAction
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ERAVIBES import app

# Dictionary to track if a user has activated the quiz loop
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

# /quiz command to show the on/off options
@app.on_message(filters.command(["quiz", "uiz"], prefixes=["/", "!", ".", "Q", "q"]))
async def quiz(client, message):
    user_id = message.from_user.id

    # Creating on/off buttons
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Sᴛᴀʀᴛ Qᴜɪᴢ", callback_data="start_quiz")],
            [InlineKeyboardButton("Sᴛᴏᴘ Qᴜɪᴢ", callback_data="stop_quiz")],
        ]
    )

    # Sending the message with buttons
    await message.reply_text(
        "Sᴛᴀʀᴛ ᴏʀ sᴛᴏᴘ ǫᴜɪᴢᴢᴇs. \n\n"
        "• **On**: The bot will send a quiz every 10 minutes.\n"
        "• **Off**: The bot will stop sending quizzes.",
        reply_markup=keyboard
    )

# Handling the button presses (callbacks)
@app.on_callback_query(filters.regex("start_quiz"))
async def start_quiz_loop(client, callback_query):
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    if user_id in quiz_loops:
        await callback_query.answer("Quiz loop is already running!", show_alert=True)
    else:
        quiz_loops[user_id] = True  # Mark the loop as running
        await callback_query.answer("Quiz loop started!", show_alert=True)

        # Start the quiz loop with a 10-minute delay
        while quiz_loops.get(user_id, False):
            await send_quiz_poll(client, callback_query.message)
            await asyncio.sleep(600)  # 10 minutes (600 seconds)

@app.on_callback_query(filters.regex("stop_quiz"))
async def stop_quiz_loop(client, callback_query):
    user_id = callback_query.from_user.id

    if user_id not in quiz_loops:
        await callback_query.answer("No quiz loop is running!", show_alert=True)
    else:
        quiz_loops.pop(user_id)  # Stop the loop
        await callback_query.answer("Quiz loop stopped!", show_alert=True)




__MODULE__ = "Qᴜɪᴢ"
__HELP__ = " /quiz - ᴛᴏ ɢᴇᴛ ᴀɴ ʀᴀɴᴅᴏᴍ ǫᴜɪᴢ"
