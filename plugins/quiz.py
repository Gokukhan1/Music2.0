import random
import requests
import asyncio
from pyrogram import filters
from pyrogram.enums import PollType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ERAVIBES import app

# Track quiz loops and active polls per user
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

# Function to send a quiz poll with an open_period for countdown
async def send_quiz_poll(client, chat_id, user_id, interval):
    question, all_answers, cid = await fetch_quiz_question()

    if user_id in active_polls:
        try:
            await app.delete_messages(chat_id=chat_id, message_ids=active_polls[user_id])
        except Exception as e:
            print(f"Failed to delete previous poll: {e}")

    poll_message = await app.send_poll(
        chat_id=chat_id,
        question=question,
        options=all_answers,
        is_anonymous=False,
        type=PollType.QUIZ,
        correct_option_id=cid,
        open_period=interval  # Countdown timer in seconds
    )

    if poll_message:
        active_polls[user_id] = poll_message.id

    # Simulating a "CSS-like" timer message
    countdown_message = await client.send_message(
        chat_id=chat_id,
        text=f"🕒 **Quiz starts now!** Poll is active for `{interval}` seconds.\n"
             f"Countdown: `{interval}` seconds remaining...",
    )

    # Update countdown every 5 seconds
    for i in range(interval, 0, -5):
        await asyncio.sleep(5)
        try:
            await countdown_message.edit_text(
                f"🕒 **Quiz is active!** `{i-5}` seconds remaining..."
            )
        except Exception as e:
            print(f"Failed to update timer message: {e}")
    
    # Finally delete the countdown message
    await countdown_message.delete()

# /quiz on command to show time interval options
@app.on_message(filters.command("quiz on"))
async def quiz_on(client, message):
    user_id = message.from_user.id

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("30s", callback_data="30_sec"), InlineKeyboardButton("1min", callback_data="1_min")],
            [InlineKeyboardButton("5min", callback_data="5_min"), InlineKeyboardButton("10min", callback_data="10_min")],
        ]
    )

    # Informational message
    await message.reply_text(
        "ℹ️ **Quiz Bot Instructions**:\n\n"
        "Use the buttons below to select how frequently you want to receive quizzes.\n"
        "- **30s**: Receive a quiz every 30 seconds.\n"
        "- **1min**: Receive a quiz every 1 minute.\n"
        "- **5min**: Receive a quiz every 5 minutes.\n"
        "- **10min**: Receive a quiz every 10 minutes.\n\n"
        "You can stop the quiz anytime using the `/quiz off` command.",
        reply_markup=keyboard
    )

# Handle button presses for time intervals
@app.on_callback_query(filters.regex(r"^\d+_sec$|^\d+_min$"))
async def start_quiz_loop(client, callback_query):
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    if user_id in quiz_loops:
        await callback_query.answer("Quiz loop is already running!", show_alert=True)
        return

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

    await callback_query.message.delete()

    await callback_query.message.reply_text(f"✅ Quiz loop started! You’ll get a new quiz every {interval_text}.")

    quiz_loops[user_id] = True

    while quiz_loops.get(user_id, False):
        await send_quiz_poll(client, chat_id, user_id, interval)
        await asyncio.sleep(interval)

# /quiz off command to stop the quiz loop
@app.on_message(filters.command("quiz off"))
async def stop_quiz(client, message):
    user_id = message.from_user.id

    if user_id not in quiz_loops:
        await message.reply_text("❌ No quiz loop is currently running.")
    else:
        quiz_loops.pop(user_id)
        await message.reply_text("⛔ Quiz loop stopped.")

        if user_id in active_polls:
            try:
                await app.delete_messages(chat_id=message.chat.id, message_ids=active_polls[user_id])
                active_polls.pop(user_id)
            except Exception as e:
                print(f"Failed to delete active poll: {e}")
