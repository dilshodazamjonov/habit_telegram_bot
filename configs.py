from aiogram.fsm.state import StatesGroup, State

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

class GoalStates(StatesGroup):
    entering_title = State()
    entering_description = State()
    entering_deadline = State()
    confirming_goal = State()
    waiting_for_date = State()
    selecting_reminder_frequency = State()
    waiting_for_reminder = State()
    updating_title = State()
    updating_description = State()
    updating_deadline = State()
    updating_reminder = State()
    update_reminder = State()
    entering_habit_title = State()
    entering_habit_desc = State()
    select_reminder = State()
    entering_habit_progress = State()
    entering_notes = State()