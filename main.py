from aiogram import Dispatcher, F, Bot
import asyncio
from datetime import datetime
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from configs import *
from aiogram.types import CallbackQuery, Message, BufferedInputFile
import io
from database import *
from keyboards import *
from reminder_math import *
import matplotlib.pyplot as plt

# List of tips
TIPS = [
    "💡 Set specific, measurable, and realistic goals for better results.",
    "💡 Consistency is the key to forming new habits!",
    "💡 Celebrate small wins to stay motivated on your journey.",
    "💡 Use reminders to never miss a habit or goal update.",
    "💡 Review your progress weekly to stay on track."
]

TOKEN = '8034732857:AAGMeZa0ZHziQul4uMfshX28GEe3v7bMBtc'

bot = Bot(TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_message(message: Message):
    await message.answer(f"🎉 Welcome, {message.from_user.full_name}! I'm your Habit Tracker Bot 🤖. "
                         f"Ready to crush your goals and build amazing habits? Let's get started! 💪")
    await register_user(message)


async def register_user(message: Message):
    chat_id = message.chat.id
    username = message.from_user.username
    user = select_user_from_db(chat_id)
    if user:
        await message.answer('Authentication is successful')
        await show_main_menu(message)
    else:
        add_new_user(username=username, chat_id=chat_id)
        await message.answer('Registration is successful, you can continue')


async def show_main_menu(message: Message):
    await message.answer('Choose one of the options below to get started: ', reply_markup=generate_main_menu())



# Making reaction for each buttons in the main menu



@dp.message(lambda message: '🏋️‍♀️ Start New Goal' in message.text or message.text == '/start_new_goal')
async def starting_new_goal(message: Message, state: FSMContext):
    await message.answer("Great! Let's get started with your new goal. Please provide the goal title.")
    await state.set_state(GoalStates.entering_title)

@dp.message(StateFilter(GoalStates.entering_title))
async def capturing_title(message: Message, state: FSMContext):
    title = message.text.strip()
    await state.update_data(title=title)  # Store the title in the state data
    await message.answer("Awesome! Now, please provide a brief description of your goal.")
    await state.set_state(GoalStates.entering_description)  # Transition to the next state

@dp.message(StateFilter(GoalStates.entering_description))
async def capturing_description(message: Message, state: FSMContext):
    description = message.text.strip()
    await state.update_data(description=description)  # Store the description
    await message.answer("Almost done! Please provide the deadline in the format YYYY-MM-DD.")
    await state.set_state(GoalStates.entering_deadline)  # Move to deadline entry


@dp.message(StateFilter(GoalStates.entering_deadline))
async def capturing_deadline(message: Message, state: FSMContext):
    deadline_str = message.text.strip()
    try:
        # Try to parse the deadline
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()

        # Get today's date
        today = datetime.today().date()

        # Check if the deadline is in the future
        if deadline < today:
            await message.answer(
                f"⚠️ Oops! The deadline {deadline} is in the past. Please choose a future date. 🙅‍♂️"
            )
            return

        # Store the deadline in the state data
        await state.update_data(deadline=deadline)

        # Ask user for reminder frequency with examples
        await message.answer(
            "🔔 Now, let's set up your reminder! How often would you like to be reminded about this goal?\n\n"
            "Choose one of the following options by typing the corresponding number:\n"
            "1️⃣ Every hour (Perfect for daily tasks!)\n"
            "2️⃣ Every day (For regular check-ins)\n"
            "3️⃣ Every week (For long-term goals)\n"
            "4️⃣ Every month (For big milestones)\n\n"
            "Just type the number (e.g., 1) corresponding to your choice, and let's keep you on track! 📅"
        )
        await state.set_state(GoalStates.selecting_reminder_frequency)

    except ValueError:
        await message.answer("⚠️ Invalid date format! Please use the correct format: YYYY-MM-DD. 🗓️")



@dp.message(StateFilter(GoalStates.selecting_reminder_frequency))
async def capturing_reminder_frequency(message: Message, state: FSMContext):
    user_input = str(message.text.strip())

    # Updated frequency_map to match expected database values
    frequency_map = {
        "1": "every hour",
        "2": "every day",
        "3": "every week",
        "4": "every month",
    }

    if user_input not in frequency_map:
        await message.answer(
            "Invalid choice. Please type one of the following options:\n"
            "1 - Every hour\n"
            "2 - Every day\n"
            "3 - Every week\n"
            "4 - Every month"
        )
        return

    frequency = frequency_map[user_input]
    print(frequency)
    await state.update_data(reminder_frequency=frequency)

    # Proceed to save the goal or handle further logic
    data = await state.get_data()
    title = data.get('title')
    description = data.get('description')
    deadline = data.get('deadline')
    user = select_user_from_db(message.chat.id)

    if not user:
        await message.answer("There was an issue retrieving your data. Please try again later.")
        return

    user_id = user[0]

    # Save the goal and reminder frequency to the database
    try:
        save_to_goals(user_id, title, description, deadline, frequency)
        reminder_time = calculate_next_reminder_time(frequency, deadline)
        goal_id = get_latest_goal_id(user_id)
        insert_into_goal_reminders(goal_id=goal_id, time=reminder_time, frequency=frequency, user_id=user_id)

        # Confirmation message with animation
        caption = (
            f'🎯 Goal "{title}" has been created successfully!\n'
            f'Deadline: {deadline}\n'
            f'Reminders: {frequency.capitalize()}\n'
            f"You will receive reminders accordingly. ✅"
        )
        await message.answer_animation(
            animation="https://media.tenor.com/3uoYRzrwbggAAAAC/goals-successful.gif",
            caption=caption
        )
        await state.clear()  # Clear state after saving the goal

    except Exception as e:
        print(f"Error saving goal: {e}")
        await message.answer("There was an issue saving your goal. Please try again later. ❌")


@dp.message(lambda message: '📊 My Goals' in message.text or message.text == '/my_goals')
async def my_goals(message: Message):
    chat_id = message.chat.id
    user_id = select_user_from_db(chat_id=chat_id)[0]
    await message.answer(text='Here are your most recent goals with closest deadlines. Tap a goal to view or manage it:', reply_markup=my_goals_display(user_id))


@dp.callback_query(lambda call: 'goal_name' in call.data)
async def see_goal_details(call: CallbackQuery):
    chat_id = call.message.chat.id
    goal_id = call.data.split('_')[-1]
    goal_id = int(goal_id)
    message_id = call.message.message_id
    await bot.edit_message_text(
        text = f'💪 Ready to make progress with your goal: \"{get_goals_by_goal_id(goal_id)[1].capitalize()}\"? Select an option to move forward!',
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=generate_goal_settings(goal_id))

@dp.callback_query(lambda call: 'view' in call.data)
async def see_goal_details(call: CallbackQuery):
    chat_id = call.message.chat.id
    view, goal_id = call.data.split('_')
    goal_id = int(goal_id)
    goal = get_goals_by_goal_id(goal_id)
    frequency = get_frequency_by_goal_id(goal_id)
    message_id = call.message.message_id
    text = f'''                ✨ Goal Details ✨

📝 Goal Title: <<< {goal[1].capitalize()} >>>
📖 Description: {goal[2].capitalize()}
⏰ Deadline: {goal[3]}
⏲️ Reminder: {frequency.capitalize()}

You're doing great! Keep up the hard work! 💪'''
    await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=generate_goal_detail(goal_id))

@dp.callback_query(lambda call: 'back_to_goal_detail' in call.data)
async def back_to_goal_settings(call: CallbackQuery):
    chat_id = call.message.chat.id
    messages_id = call.message.message_id
    goal_id = int(call.data.split('_')[-1])
    await bot.delete_message(chat_id=chat_id, message_id=messages_id)
    await bot.send_message(chat_id=chat_id,
       text=f'💪 Ready to make progress with your goal: \"{get_goals_by_goal_id(goal_id)[1].capitalize()}\"? '
       f'Select an option to move forward!', reply_markup=generate_goal_settings(goal_id))


@dp.callback_query(lambda call: 'edit_goal' in call.data)
async def edit_goal_menu(call: CallbackQuery):
    goal_id = int(call.data.split('_')[-1])
    goal = get_goals_by_goal_id(goal_id)
    new_text = f"🔧 Editing Goal: <<< {goal[1].capitalize()} >>> \n\nChoose the part of the goal you'd like to edit:"
    await call.message.answer(
        text=new_text,
        reply_markup=edit_goal_detail_buttons(goal_id)
    )

@dp.callback_query(lambda call: 'edit_title' in call.data)
async def edit_goal_title(call: CallbackQuery, state: FSMContext):
    goal_id = int(call.data.split('_')[-1])
    goal = get_goals_by_goal_id(goal_id)
    await state.update_data(goal_id=goal_id)
    await call.message.answer(
        text=f"✏️ You are editing the TITLE of your goal: {goal[1].capitalize()}. Please send the new title."
    )
    await state.set_state(GoalStates.updating_title)

@dp.message(StateFilter(GoalStates.updating_title))
async def update_goal_title(message: Message, state: FSMContext):
    new_title = message.text.strip()
    if len(new_title) < 3:
        await message.reply("⚠️ The title is too short. Please enter a TITLE with at least 3 characters.")
        return

    user_data = await state.get_data()
    goal_id = user_data.get('goal_id')
    update_goal_in_db(goal_id, 'goal_name', new_title)

    await message.reply(f"✅ The goal TITLE has been updated to: {new_title.capitalize()}")
    await state.clear()

@dp.callback_query(lambda call: 'edit_description' in call.data)
async def edit_goal_description(call: CallbackQuery, state: FSMContext):
    goal_id = int(call.data.split('_')[-1])
    goal = get_goals_by_goal_id(goal_id)
    await state.update_data(goal_id=goal_id)
    await call.message.edit_text(
        text=f"✏️ You are editing the DESCRIPTION of your goal: {goal[2]}. Please send the new description."
    )
    await state.set_state(GoalStates.updating_description)

@dp.message(StateFilter(GoalStates.updating_description))
async def update_goal_description(message: Message, state: FSMContext):
    new_description = message.text.strip()
    if len(new_description) < 10:
        await message.reply("⚠️ The description is too short. Please enter a description with at least 10 characters.")
        return

    user_data = await state.get_data()
    goal_id = user_data.get('goal_id')
    update_goal_in_db(goal_id, 'goal_description', new_description)

    await message.reply(f"✅ The goal DESCRIPTION has been updated to: {new_description.capitalize()}")
    await state.clear()

@dp.callback_query(lambda call: 'edit_deadline' in call.data)
async def edit_goal_deadline(call: CallbackQuery, state: FSMContext):
    goal_id = int(call.data.split('_')[-1])
    goal = get_goals_by_goal_id(goal_id)
    await state.update_data(goal_id=goal_id)
    await call.message.edit_text(
        text=f"✏️ You are updating the DEADLINE of your goal: {goal[1].capitalize()}.\n"
             f"Please provide the new deadline in the format **YYYY-MM-DD** (e.g., 2025-01-15)."
    )
    await state.set_state(GoalStates.updating_deadline)

@dp.message(StateFilter(GoalStates.updating_deadline))
async def update_goal_deadline(message: Message, state: FSMContext):
    new_deadline = message.text.strip()

    # Validate the date format
    try:
        from datetime import datetime
        deadline_date = datetime.strptime(new_deadline, "%Y-%m-%d")
        if deadline_date < datetime.now():
            await message.reply("⚠️ The deadline cannot be in the past. Please provide a future date.")
            return
    except ValueError:
        await message.reply("⚠️ Invalid date format. Please enter the date in the format **YYYY-MM-DD** (e.g., 2025-01-15).")
        return

    user_data = await state.get_data()
    goal_id = user_data.get('goal_id')
    update_goal_in_db(goal_id, 'goal_deadline', new_deadline)

    await message.reply(f"✅ The goal deadline has been successfully updated to: {new_deadline}.")
    await state.clear()



@dp.callback_query(lambda call: 'edit_reminder' in call.data)
async def edit_goal_reminder(call: CallbackQuery, state: FSMContext):
    goal_id = int(call.data.split('_')[-1])
    goal = get_goals_by_goal_id(goal_id)

    await state.update_data(goal_id=goal_id, goal_deadline=goal[3])  # Assuming goal[3] contains the deadline
    await call.message.edit_text(
        text=(
            "🔔 You are updating the reminder for this goal.\n\n"
            "Please choose one of the following options by typing the corresponding number:\n"
            "1️⃣ Remind every hour\n"
            "2️⃣ Remind every day\n"
            "3️⃣ Remind every week\n"
            "4️⃣ Remind every month\n\n"
            "Just type the number corresponding to your choice."
        )
    )
    await state.set_state(GoalStates.update_reminder)

@dp.message(StateFilter(GoalStates.update_reminder))
async def update_goal_reminder(message: Message, state: FSMContext):
    new_reminder = message.text.strip()
    reminder_map = {
        "1": "every hour",
        "2": "every day",
        "3": "every week",
        "4": "every month"
    }

    if new_reminder not in reminder_map:
        await message.reply("⚠️ Invalid option. Please select a valid number (1, 2, 3, or 4).")
        return

    user_data = await state.get_data()
    goal_id = user_data.get('goal_id')
    goal_deadline = user_data.get('goal_deadline')
    user_id = select_user_from_db(chat_id=message.chat.id)

    if user_id is None:
        await message.reply("⚠️ Error: Unable to identify the user.")
        await state.clear()
        return

    try:
        # Parse the deadline date
        deadline_date = datetime.strptime(goal_deadline, "%Y-%m-%d").date()
        frequency = reminder_map[new_reminder]

        # Calculate next reminder time
        next_reminder = calculate_next_reminder_time(frequency, deadline_date)

        # Update the reminder in the database
        try:
            update_goal_reminder_in_db(goal_id, frequency, next_reminder)
        except Exception as db_error:
            await message.reply(f"⚠️ Error updating the reminder in the database: {db_error}")
            return

        # Inform the user
        await message.reply(
            f"✅ The reminder has been updated to: {frequency.capitalize()}.\n"
            f"⏰ Next reminder is scheduled for: {next_reminder}."
        )
    except ValueError as e:
        await message.reply(f"⚠️ Error: {e}")
    except Exception as error:
        await message.reply(f"⚠️ Unexpected error: {error}")

    await state.clear()

@dp.callback_query(lambda call: 'complete' in call.data)
async def check_completed_goals(call: CallbackQuery):
    goal_id = call.data.split('_')[-1]
    mark_completed_in_db(goal_id)
    await call.message.edit_text("🎉 Congratulations! Your goal has been successfully marked as completed."
                                 " ✅ Goal completed! View this and all your completed goals with /completed_goals. Keep going!")


@dp.callback_query(lambda call: 'delete_goal' in call.data)
async def check_completed_goals(call: CallbackQuery):
    goal_id = int(call.data.split('_')[-1])
    goal = get_goals_by_goal_id(goal_id)
    await call.message.edit_text(f'{select_user_from_db(chat_id=call.message.chat.id)[2]} are you sure to delete your goal by title:'
                                 f' <<< {goal[1]} >>> ', reply_markup=deletion_validation(goal_id))

@dp.callback_query(lambda call: 'sure_deletion' in call.data)
async def sure_deletion(call: CallbackQuery):
    goal_id = int(call.data.split('_')[-1])
    goal = get_goals_by_goal_id(goal_id)
    delete_goal_from_db(goal_id)
    await call.message.edit_text(text=f'Goal named {goal[1]} has successfully been deleted')

@dp.callback_query(lambda call: 'not_sure' in call.data)
async def not_sure_deletion(call: CallbackQuery):
    goal_id = int(call.data.split('_')[-1])
    goal = get_goals_by_goal_id(goal_id)
    frequency = get_frequency_by_goal_id(goal_id)
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    text = f'''  ✨ Goal Details ✨
    
📝 Goal Title: <<< {goal[1].capitalize()} >>>
📖 Description: {goal[2].capitalize()}
⏰ Deadline: {goal[3]}
⏲️ Reminder: {frequency.capitalize()}

You're doing great! Keep up the hard work! 💪'''
    await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text,
                                reply_markup=generate_goal_detail(goal_id))


@dp.message(lambda message: 'Create a Habit' in message.text or message.text == '/start_habit')
async def create_habit(message: Message, state: FSMContext):
    await message.answer(text='Creating new habit path. Provide title for your habit: ')
    await state.set_state(GoalStates.entering_habit_title)

@dp.message(StateFilter(GoalStates.entering_habit_title))
async def save_title(message: Message, state: FSMContext):
    title = message.text.strip()
    await state.update_data(title=title)
    await message.answer("Awesome! Now, please provide a brief description of your goal.")
    await state.set_state(GoalStates.entering_habit_desc)

@dp.message(StateFilter(GoalStates.entering_habit_desc))
async def save_description(message: Message, state: FSMContext):
    description = message.text.strip()
    await state.update_data(description=description)
    await message.answer(
        "🔔 Now, let's set up your reminder! How often would you like to be reminded about this goal?\n\n"
        "Choose one of the following options by typing the corresponding number:\n"
        "1️⃣ Every hour (Perfect for daily tasks!)\n"
        "2️⃣ Every day (For regular check-ins)\n"
        "3️⃣ Every week (For long-term goals)\n"
        "4️⃣ Every month (For big milestones)\n\n"
        "Just type the number (e.g., 1) corresponding to your choice, and let's keep you on track! 📅"
    )
    await state.set_state(GoalStates.select_reminder)

@dp.message(StateFilter(GoalStates.select_reminder))
async def capturing_reminder_frequency(message: Message, state: FSMContext):
    user_input = str(message.text.strip())
    frequency_map = {
        "1": "every hour",
        "2": "every day",
        "3": "every week",
        "4": "every month",
    }

    if user_input not in frequency_map:
        await message.answer(
            "Invalid choice. Please type one of the following options:\n"
            "1 - Every hour\n"
            "2 - Every day\n"
            "3 - Every week\n"
            "4 - Every month"
        )
        return

    frequency = frequency_map[user_input]
    await state.update_data(reminder_frequency=frequency)
    data = await state.get_data()
    title = data.get('title')
    description = data.get('description')
    user = select_user_from_db(message.chat.id)

    if not user:
        await message.answer("There was an issue retrieving your data. Please try again later.")
        return

    user_id = user[0]

    try:
        insert_into_habit_tracker(user_id, title, description, frequency)
        reminder_time = calculate_next_reminder_time(frequency, datetime.strptime('2025-05-06', '%Y-%m-%d'))
        habit_id = get_habit_id(user_id)[-1][0]


        if habit_id:

            insert_into_habit_reminder(habit_id=habit_id, user_id=user_id, reminder_time=reminder_time, next_reminder=frequency)
            caption = (
                f'🎯 Goal "{title}" has been created successfully!\n'
                f'Reminders: {frequency.capitalize()}\n'
                f"You will receive reminders accordingly. ✅"
            )
            await message.answer_animation(
                animation="https://media.tenor.com/3uoYRzrwbggAAAAC/goals-successful.gif",
                caption=caption
            )
            await state.clear()
        else:
            await message.answer("Could not retrieve the habit ID. Please try again later.")

    except Exception as e:
        print(f"Error saving goal: {e}")
        await message.answer("There was an issue saving your goal. Please try again later. ❌")

@dp.message(lambda message: '❓ Help & Info' in message.text)
async def set_reminder(message: Message):
    await message.answer(text='For help please contact with the administrator(@d_azamjonov)')


@dp.message(lambda message: '📈 Update Progress(For habit)' in message.text or message.text == '/see_habit_details')
async def set_progress(message: Message):
    user_id = select_user_from_db(chat_id=message.chat.id)[0]
    await message.answer(text='Choose for which habit you want to edit: ', reply_markup=get_habits(user_id))

@dp.callback_query(lambda call: 'habit_edit' in call.data)
async def habit_selected(call: CallbackQuery):
    habit_id = int(call.data.split('_')[-1])
    habit = get_habit_details(habit_id)
    habit_progress = get_habit_progress_details(habit_id)
    if habit_progress:
        await call.message.answer(text = f''' Habit: {habit[2]}
Your progress: {habit_progress[3]}%
Last update time: {habit_progress[4]}
Status: {'Finished' if habit_progress[5] == 1 else 'Not completed'}
Notes: {habit_progress[-1]}
''', reply_markup=edit_habit_details(habit_id))
    else:
        await call.message.answer(text='No details about progress now, write now: ', reply_markup=edit_habit_details(habit_id))

@dp.callback_query(lambda call: 'progress_' in call.data)
async def saving_progress(call: CallbackQuery, state: FSMContext):
    habit_id = int(call.data.split('_')[-1])
    user_id = select_user_from_db(chat_id=call.message.chat.id)[0]
    habit = get_habit_details(habit_id)
    await call.message.edit_text(
        f'You selected habit {habit[2]}. Please provide your progress update (e.g., 50% completed, 30 minutes done, etc.):'
    )

    await state.set_state(GoalStates.entering_habit_progress)
    await state.update_data(habit_id=habit_id, user_id=user_id)


@dp.message(StateFilter(GoalStates.entering_habit_progress))
async def save_progress(message: Message, state: FSMContext):
    progress_text = message.text.strip()

    # Retrieve habit_id and user_id from the state
    data = await state.get_data()
    habit_id = data.get('habit_id')
    user_id = data.get('user_id')
    habit = get_habit_details(habit_id)
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    print(now)
    if habit_id is None or user_id is None:
        await message.answer("Error: Unable to retrieve habit or user data. Please try again later.")
        return
    try:
        insert_into_progress(user_id, habit_id, 'progress', progress_text, now)
        await message.answer(f'Your progress for habit {habit[2]} has been updated: "{progress_text}" ✅, type /see_habit_details')
        await state.clear()

    except Exception as e:
        await message.answer(f"Error saving progress: {e} ❌")


@dp.callback_query(lambda call: 'notes' in call.data)
async def save_progress_notes(call: CallbackQuery, state: FSMContext):
    habit_id = int(call.data.split('_')[-1])
    user_id = select_user_from_db(call.message.chat.id)[0]
    await call.message.answer("Please provide your notes for this habit progress:")
    await state.set_state(GoalStates.entering_notes)
    await state.update_data(habit_id=habit_id, user_id=user_id)


@dp.message(StateFilter(GoalStates.entering_notes))
async def save_progress_notes(message: Message, state: FSMContext):
    notes = message.text.strip()
    data = await state.get_data()
    habit_id = data.get('habit_id')
    user_id = data.get('user_id')

    if habit_id is None or user_id is None:
        await message.answer("Error: Unable to retrieve habit or user data. Please try again.")
        return

    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        database = sqlite3.connect('habit_tracker.db')
        cursor = database.cursor()
        cursor.execute('''
            SELECT update_id FROM progress_updates
            WHERE user_id = ? AND habit_id = ?
        ''', (user_id, habit_id))
        record = cursor.fetchone()

        if record:
            cursor.execute('''
                UPDATE progress_updates
                SET notes = ?, update_time = ?
                WHERE user_id = ? AND habit_id = ?
            ''', (notes, now, user_id, habit_id))
            operation = "updated"
        else:
            cursor.execute('''
                INSERT INTO progress_updates (user_id, habit_id, notes, update_time)
                VALUES (?, ?, ?, ?)
            ''', (user_id, habit_id, notes, now))
            operation = "saved"

        database.commit()
        database.close()

        await message.answer(
            f"Your notes for habit ID {habit_id} have been {operation} successfully! ✅\n\n"
            f"📋 Notes: {notes}"
        )
        await state.clear()

    except Exception as e:
        await message.answer(f"An error occurred while saving your notes: {e}")
        await state.clear()



@dp.callback_query(lambda call: 'back_to_habit_details' in call.data)
async def back_to_habit_detail(call: CallbackQuery):
    user_id = select_user_from_db(chat_id=call.message.chat.id)[0]
    await call.message.answer(text='Choose for which habit you want to edit: ', reply_markup=get_habits(user_id))



@dp.message(lambda message: '📝 See progress' in message.text)
async def get_progress_data(message: Message):
    user_id = select_user_from_db(chat_id=message.chat.id)[0]

    # Fetch progress data from the database
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
        SELECT habit_id, update_time, progress, notes
        FROM progress_updates
        WHERE user_id = ?
        ORDER BY update_time ASC
    ''', (user_id,))
    data = cursor.fetchall()
    database.close()

    if not data:
        await message.answer("No progress data available. Start tracking your habits to see progress!")
        return

    # Prepare data for visualization
    habits = {}
    for habit_id, update_time, progress, notes in data:
        # Skip rows with missing or invalid update_time
        if update_time is None:
            continue
        try:
            timestamp = datetime.strptime(update_time, '%Y-%m-%d %H:%M')  # Ensure valid datetime
        except ValueError:
            continue  # Skip invalid datetime formats

        if habit_id not in habits:
            habits[habit_id] = {'timestamps': [], 'progress': []}

        # Only add valid progress values
        if progress is not None:
            habits[habit_id]['timestamps'].append(timestamp)
            habits[habit_id]['progress'].append(float(progress))

    if not habits:
        await message.answer("No valid progress data to display. Please check your tracking records!")
        return

    # Create the plot
    plt.figure(figsize=(10, 6))
    for habit_id, habit_data in habits.items():
        plt.plot(
            habit_data['timestamps'],
            habit_data['progress'],
            marker='o',
            label=f"Habit ID {habit_id}"
        )

    plt.title("Progress Over Time")
    plt.xlabel("Time")
    plt.ylabel("Progress (%)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)

    # Save the plot to a buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    # Send the plot as an image
    photo = BufferedInputFile(buffer.read(), filename="progress.png")
    await message.answer_photo(photo, caption="Here's your progress overview 📊")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())
