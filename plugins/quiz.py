import random
import requests
import asyncio

from pyrogram import filters
from pyrogram.enums import PollType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ERAVIBES import app

# Track quiz loops and active polls per user
quiz_loops = {}
active_polls = {}  # To track active poll messages for each user

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

# Function to send a quiz poll and delete the previous one if it exists
async def send_quiz_poll(client, chat_id, user_id):
    # Fetch quiz question
    question, all_answers, cid = await fetch_quiz_question()

    # Delete the previous active poll if it exists
    if user_id in active_polls:
        try:
            await app.delete_messages(chat_id=chat_id, message_ids=active_polls[user_id])
        except Exception as e:
            print(f"Failed to delete previous poll: {e}")

    # Send new quiz poll and save the message ID
    poll_message = await app.send_poll(
        chat_id=chat_id,
        question=question,
        options=all_answers,
        is_anonymous=False,
        type=PollType.QUIZ,
        correct_option_id=cid,
    )
    # Store the message ID of the new poll
    active_polls[user_id] = poll_message.message_id

# /quiz on command to show time interval options
@app.on_message(filters.command("quiz on"))
async def quiz_on(client, message):
    user_id = message.from_user.id

    # Create time interval buttons arranged in 4x2 grid
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("30s", callback_data="30_sec"), InlineKeyboardButton("1min", callback_data="1_min")],
            [InlineKeyboardButton("5min", callback_data="5_min"), InlineKeyboardButton("10min", callback_data="10_min")],
        ]
    )

    # Send buttons with a description
    await message.reply_text(
        "**Choose how often you want the quiz to run:**\n\n"
        "- 30s: Quiz every 30 seconds\n"
        "- 1min: Quiz every 1 minute\n"
        "- 5min: Quiz every 5 minutes\n"
        "- 10min: Quiz every 10 minutes\n\n"
        "**Use** `/quiz off` **to stop the quiz loop at any time.**",
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

    # Determine interval based on the button pressed
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

    # Delete the original message with buttons
    await callback_query.message.delete()

    # Confirm that the quiz loop has started
    await callback_query.message.reply_text(f"✅ Quiz loop started! You'll receive a quiz every {interval_text}.")

    quiz_loops[user_id] = True  # Mark loop as running

    # Start the quiz loop with the selected interval
    while quiz_loops.get(user_id, False):
        await send_quiz_poll(client, chat_id, user_id)
        await asyncio.sleep(interval)  # Wait for the selected interval before sending the next quiz

# /quiz off command to stop the quiz loop
@app.on_message(filters.command("quiz off"))
async def stop_quiz(client, message):
    user_id = message.from_user.id

    if user_id not in quiz_loops:
        await message.reply_text("No quiz loop is running.")
    else:
        quiz_loops.pop(user_id)  # Stop the loop
        await message.reply_text("⛔ Quiz loop stopped!")

        # Delete the active poll if there's one
        if user_id in active_polls:
            try:
                await app.delete_messages(chat_id=message.chat.id, message_ids=active_polls[user_id])
                active_polls.pop(user_id)
            except Exception as e:
                print(f"Failed to delete active poll: {e}")


__MODULE__ = "Qᴜɪᴢ"
__HELP__ = """
/quiz on - Sᴛᴀʀᴛ ǫᴜɪᴢ ᴍᴏᴅᴇ. Sᴇʟᴇᴄᴛ ᴛʜᴇ ɪɴᴛᴇʀᴠᴀʟ ғᴏʀ ǫᴜɪᴢᴢᴇs ᴛᴏ ʙᴇ sᴇɴᴛ. 

• **Intervals:**
   - 30 seconds
   - 1 minute
   - 5 minutes
   - 10 minutes
•  "**Use** `/quiz off` **to stop the quiz loop at any time.**".
"""
