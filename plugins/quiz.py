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
active_polls = {}

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
async def send_quiz_poll(client, chat_id, user_id):
    question, all_answers, cid = await fetch_quiz_question()

    poll_message = await app.send_poll(
        chat_id=chat_id,
        question=question,
        options=all_answers,
        is_anonymous=False,
        type=PollType.QUIZ,
        correct_option_id=cid,
    )

    if user_id in active_polls:
        # Delete the previous poll before adding the new one
        try:
            await app.delete_messages(chat_id, active_polls[user_id])
        except Exception as e:
            print(f"Error deleting message: {e}")

    active_polls[user_id] = poll_message.id

# /quiz command to show help if used incorrectly or start/stop
@app.on_message(filters.command("quiz"))
async def quiz_help(client, message):
    command = message.text.strip().lower()

    if command == "/quiz":
        # If the user just typed /quiz without "on" or "off", send an explanation
        await message.reply_text(
            "You can control the quiz feature using the following commands:\n\n"
            "• /quiz on — Start the quiz and select a time interval for automatic quizzes.\n"
            "• /quiz off — Stop the ongoing quiz loop.\n\n"
            "After selecting **/quiz on**, you'll see buttons that allow you to choose how often the quiz should appear "
            "(e.g., every 30 seconds, 1 minute, etc.). When the quiz is running, it will automatically send you questions "
            "at the interval you selected. Use `/quiz off` anytime to stop receiving quizzes.\n\n"
            "Please choose the appropriate option."
        )
    elif command == "/quiz on":
        # Call the function to show the buttons and start the quiz
        await quiz_on(client, message)
    elif command == "/quiz off":
        # Call the function to stop the quiz
        await stop_quiz(client, message)

# Function to start the quiz loop
async def quiz_on(client, message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Creating time interval buttons in a 4x2 grid
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("30 Seconds", callback_data="30_sec"),
             InlineKeyboardButton("1 Minute", callback_data="1_min")],
            [InlineKeyboardButton("5 Minutes", callback_data="5_min"),
             InlineKeyboardButton("10 Minutes", callback_data="10_min")],
            [InlineKeyboardButton("15 Minutes", callback_data="15_min"),
             InlineKeyboardButton("30 Minutes", callback_data="30_min")],
            [InlineKeyboardButton("45 Minutes", callback_data="45_min"),
             InlineKeyboardButton("1 Hour", callback_data="1_hour")]
        ]
    )

    # Sending the message with buttons
    await message.reply_text(
        "Choose how often you want the quiz to appear:\n\n"
        "• 30 Seconds\n"
        "• 1 Minute\n"
        "• 5 Minutes\n"
        "• 10 Minutes\n"
        "• 15 Minutes\n"
        "• 30 Minutes\n"
        "• 45 Minutes\n"
        "• 1 Hour",
        reply_markup=keyboard
    )

# Handling the button presses (callbacks)
@app.on_callback_query(filters.regex(r"(30_sec|1_min|5_min|10_min|15_min|30_min|45_min|1_hour)"))
async def start_quiz_loop(client, callback_query):
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    if user_id in quiz_loops:
        await callback_query.answer("Quiz loop is already running!", show_alert=True)
    else:
        # Set the interval based on the button clicked
        interval = 30 if callback_query.data == "30_sec" else \
                   60 if callback_query.data == "1_min" else \
                   300 if callback_query.data == "5_min" else \
                   600 if callback_query.data == "10_min" else \
                   900 if callback_query.data == "15_min" else \
                   1800 if callback_query.data == "30_min" else \
                   2700 if callback_query.data == "45_min" else 3600  # 1 hour

        quiz_loops[user_id] = True  # Mark the loop as running

        # Send a notification confirming the quiz loop has started
        await callback_query.answer(f"Quiz loop started! New quiz every {interval // 60} minute(s).", show_alert=True)
        await callback_query.message.reply_text(f"Quiz loop started! You will receive a new quiz every {interval // 60} minute(s).")

        while quiz_loops.get(user_id, False):
            await send_quiz_poll(client, chat_id, user_id)
            await asyncio.sleep(interval)

# Function to stop the quiz loop
@app.on_message(filters.command("quiz off"))
async def stop_quiz(client, message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if user_id not in quiz_loops:
        await message.reply_text("No quiz loop is currently running.")
    else:
        quiz_loops.pop(user_id)  # Stop the loop
        await message.reply_text("Quiz loop stopped.")
