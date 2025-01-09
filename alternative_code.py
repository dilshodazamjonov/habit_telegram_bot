""" For the button that reacts for 'Start new goal' in one go. But step by step goal creation is better
    so I choose that code type """

@dp.message(lambda message: '🏋️‍♀️ Start New Goal' in message.text)
async def starting_new_goal(message: Message, state: FSMContext):
    print(repr(message.text))  # Log the exact message text
    await message.answer(
        "Please enter your goal in the following format:\n"
        "Title: [Goal Title]\n"
        "Description: [Brief Description]\n"
        "Deadline: [YYYY-MM-DD]"
    )
    await state.set_state(GoalStates.entering_title)  # Set the state to expect goal details

@dp.message(StateFilter(GoalStates.entering_title))
async def capturing_new_goal_details(message: Message, state: FSMContext):
    current_state = await state.get_state()
    print(f"Current state: {current_state}")  # Log the current state
    user_input = message.text
    chat_id = message.chat.id

    try:
        lines = user_input.split('\n')
        title = lines[0].replace('Title:', '').strip()
        description = lines[1].replace('Description:', '').strip()
        deadline_str = lines[2].replace('Deadline:', '').strip()

        deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()

        # Save goal to the database
        user = select_user_from_db(chat_id)
        user_id = user[0]  # Assuming `user_id` is the first element in the user tuple
        save_to_goals(user_id, title, description, deadline)

        await message.answer(f'Goal "{title}" has been created successfully!')
        await state.clear()  # Clear the state after goal creation
    except (IndexError, ValueError):
        await message.answer(
            "Invalid format. Please ensure you follow this format:\n"
            "Title: [Goal Title]\n"
            "Description: [Brief Description]\n"
            "Deadline: [YYYY-MM-DD]"
        )