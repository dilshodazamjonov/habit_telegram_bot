from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from database import *


def generate_main_menu():
    button1 = KeyboardButton(text='🏋️‍♀️ Start New Goal')
    button2 = KeyboardButton(text='📊 My Goals')
    button8 = KeyboardButton(text='💪 Create a Habit')
    button4 = KeyboardButton(text='📈 Update Progress(For habit)')
    button5 = KeyboardButton(text='📝 See progress')
    button6 = KeyboardButton(text='❓ Help & Info')
    button7 = KeyboardButton(text='⚙️ Settings')

    main_menu = ReplyKeyboardMarkup(
        keyboard=[
            [button1, button2],
            [button5, button8],
            [button6, button4],
            [button7]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return main_menu

def my_goals_display(user_id):
    goals = get_goals_by_user(user_id)

    if not goals:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="No goals found", callback_data="no_goals")]
        ])
    buttons = [
        [InlineKeyboardButton(text=goal[1].capitalize(), callback_data=f"goal_name_{goal[0]}")]
        for goal in goals
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    return markup

def generate_goal_settings(goal_id):
    goal = get_goals_by_goal_id(goal_id)
    if not goal:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Goal not found", callback_data="goal_not_found")]
        ])

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔍 View Details", callback_data=f"view_{goal_id}"),
            InlineKeyboardButton(text="✅ Mark as Complete", callback_data=f"complete_{goal_id}")
        ],
        [
            InlineKeyboardButton(text="↩️ Back to Goals", callback_data="back_to_goals")
        ]
    ])

    return markup



def generate_goal_detail(goal_id):
    goal = get_goals_by_goal_id(goal_id=goal_id)
    if not goal:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Goal not found", callback_data="goal_not_found")]
        ])

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ Edit Goal", callback_data=f"edit_goal_{goal_id}"),
            InlineKeyboardButton(text="🗑️ Delete Goal", callback_data=f"delete_goal_{goal_id}")
        ],
        [
            InlineKeyboardButton(text="↩️ Go Back", callback_data=f'back_to_goal_detail_{goal_id}')
        ]
    ])

    return markup




def edit_goal_detail_buttons(goal_id):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ Edit Title", callback_data=f"edit_title_{goal_id}"),
            InlineKeyboardButton(text="📝 Edit Description", callback_data=f"edit_description_{goal_id}")
        ],
        [
            InlineKeyboardButton(text="📅 Edit Deadline", callback_data=f"edit_deadline_{goal_id}"),
            InlineKeyboardButton(text="⏰ Edit Reminder", callback_data=f"edit_reminder_{goal_id}")
        ],
        [InlineKeyboardButton(text="↩️ Back to Goal Details", callback_data=f"back_to_goal_detail_{goal_id}")]
    ])
    return markup


def deletion_validation(goal_id):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Pretty sure", callback_data=f"sure_deletion_{goal_id}"),
            InlineKeyboardButton(text="↩️ Not really, back to goal", callback_data=f"not_sure_{goal_id}")
        ]
    ])

    return markup

def get_habits(user_id):
    markup = InlineKeyboardMarkup(inline_keyboard=[])
    habits = get_habit_id(user_id)
    row = []
    for idx, habit in enumerate(habits):
        button = InlineKeyboardButton(text=str(habit[2]), callback_data=f'habit_edit_{habit[0]}')
        row.append(button)
        if len(row) == 2:
            markup.inline_keyboard.append(row)
            row = []
    if row:
        markup.inline_keyboard.append(row)

    return markup

def edit_habit_details(habit_id):
    button1 = InlineKeyboardButton(text='Progress', callback_data=f'progress_{habit_id}')
    button2 = InlineKeyboardButton(text='Notes', callback_data=f'notes_{habit_id}')
    button3 = InlineKeyboardButton(text='↩️ Back to habit details', callback_data=f'back_to_habit_details_{habit_id}')  # Added callback data
    mark_up = InlineKeyboardMarkup(inline_keyboard=[
        [button1, button2],
        [button3]
    ])
    return mark_up
