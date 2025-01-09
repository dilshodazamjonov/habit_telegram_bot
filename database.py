import sqlite3
from datetime import datetime


# Users Table
def create_table_user():
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            chat_id BIGINT NOT NULL UNIQUE,
            username TEXT,
            streak INTEGER DEFAULT 0
        )
    ''')
    database.commit()
    database.close()
create_table_user()

def add_new_user(username, chat_id):
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
    INSERT INTO users(username, chat_id) VALUES(?, ?)
    ''', (username, chat_id))
    database.commit()
    database.close()

def select_user_from_db(chat_id):
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
        SELECT * FROM users WHERE chat_id = ?
    ''', (chat_id,))
    user = cursor.fetchone()
    database.close()
    return user

# Habit Tracker Table
def create_habit_tracker_table():
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habit_tracker (
            habit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            habit_title TEXT,
            description TEXT,
            status_update BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    database.commit()
    database.close()
create_habit_tracker_table()


# Goals Table
def create_goals_table():
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_name TEXT, 
            goal_description TEXT,
            goal_deadline DATETIME,
            goal_reminder TEXT,
            goal_done_passed BOOLEAN DEFAULT FALSE,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    database.commit()
    database.close()
create_goals_table()


# Reminders Table
def create_reminders_table():
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habit_reminders (
            reminder_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            habit_id INTEGER,
            reminder_time TEXT,  -- Time the reminder is set for
            next_reminder DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (habit_id) REFERENCES habit_tracker(habit_id)
        )
    ''')
    database.commit()
    database.close()
create_reminders_table()


# Progress Updates Table
def create_progres_update_table():
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress_updates (
            update_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            habit_id INTEGER,
            progress INTEGER DEFAULT 0 CHECK(progress >= 0 AND progress <= 100),  -- Current progress in percentage
            update_time DATETIME,  -- Timestamp when the progress was updated
            completed BOOLEAN DEFAULT FALSE, 
            notes TEXT,  -- Optional notes about the progress
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (habit_id) REFERENCES habit_tracker(habit_id)
        )
    ''')
    database.commit()
    database.close()
create_progres_update_table()


# Gamification Table
def create_gamification_table():
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gamification(
            gamification_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(user_id),
            points INTEGER DEFAULT 0,  -- Points the user has earned
            streak INTEGER DEFAULT 0,  -- Current streak of consecutive goal completions
            badges TEXT  -- Comma-separated list of badges the user has earned
        )
    ''')
    database.commit()
    database.close()
create_gamification_table()


# Challenges Table
def create_challenges_table():
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS challenges (
            challenge_id INTEGER PRIMARY KEY AUTOINCREMENT,
            challenge_name TEXT,
            description TEXT,
            start_date TEXT,  -- Start date of the challenge
            end_date TEXT     -- End date of the challenge
        )
    ''')
    database.commit()
    database.close()
create_challenges_table()


# Challengers Table
def create_challengers_table():
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS challengers(
            challenge_id INTEGER REFERENCES challenges(challenge_id),
            user_id INTEGER REFERENCES users(user_id),
            progress INTEGER,
            status VARCHAR(50),
            PRIMARY KEY(user_id, challenge_id)
        )
    ''')
    database.commit()
    database.close()
create_challengers_table()


def save_to_goals(user_id, title, description, deadline, frequency):

    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
        INSERT INTO goals (goal_name, goal_description, goal_deadline, user_id, goal_reminder) VALUES(?, ?, ?, ?, ?)
    ''', (title, description, deadline, user_id, frequency))
    database.commit()
    database.close()

# save_to_goals(user_id=1, title="Read 10 books", description="Complete 10 books this month", deadline="2025-01-31")


def create_goal_reminders():
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('PRAGMA foreign_keys = ON;')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goal_reminders (
            goal_reminder_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            frequency TEXT NOT NULL, 
            next_reminder TEXT NOT NULL,
            goal_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (goal_id) REFERENCES goals (goal_id),
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        );
    ''')
    database.commit()
    database.close()

create_goal_reminders()

def insert_into_goal_reminders(goal_id, frequency, time, user_id):
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
        INSERT INTO goal_reminders(goal_id, frequency, next_reminder, user_id) VALUES(?, ?, ?, ?)
    ''', (goal_id, frequency, time, user_id))
    database.commit()
    database.close()


def get_goal_id(user_id):
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
        SELECT * FROM goals WHERE user_id = ?
    ''', (user_id,))
    goals = cursor.fetchall()
    database.close()
    return goals


def get_latest_goal_id(user_id):
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
        SELECT goal_id FROM goals 
        WHERE user_id = ? 
        ORDER BY goal_id DESC 
        LIMIT 1
    ''', (user_id,))
    result = cursor.fetchone()
    database.close()
    return result[0] if result else None

def get_goals_by_user(user_id):
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
            SELECT * 
            FROM goals 
            WHERE user_id = ? AND goal_done_passed = 0 
            ORDER BY goal_deadline ASC 
            LIMIT 8
    ''', (user_id,))
    result = cursor.fetchall()
    database.close()
    return result

def get_goals_by_goal_id(goal_id):
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
        SELECT * FROM goals WHERE goal_id = ?
    ''', (goal_id,))
    goal = cursor.fetchone()
    database.close()
    return goal

def update_goal_in_db(goal_id, field, new_value):
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute(f'''
        UPDATE goals SET {field} = ? WHERE goal_id = ?
    ''', (new_value, goal_id))
    database.commit()
    database.close()


def update_goal_reminder_in_db(goal_id, frequency, next_reminder):
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute(f'''
        UPDATE goal_reminders SET next_reminder = ?, frequency = ? WHERE goal_id = ?
    ''', (next_reminder, frequency, goal_id))
    database.commit()
    database.close()



def update_passed_goals():
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    now = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        UPDATE goals
        SET goal_done_passed = TRUE
        WHERE goal_deadline < ? AND goal_done_passed = FALSE
    ''', (now,))
    database.commit()
    database.close()

update_passed_goals()

def get_frequency_by_goal_id(goal_id):
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
        SELECT frequency FROM goal_reminders WHERE goal_id = ?
    ''',(goal_id,))
    frequency = cursor.fetchone()[0]
    database.close()
    return frequency

def mark_completed_in_db(goal_id):
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
        UPDATE goals
        SET goal_done_passed = TRUE
        WHERE goal_id = ?
    ''', (goal_id,))
    database.commit()
    database.close()

def delete_goal_from_db(goal_id):
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
            DELETE FROM goal_reminders WHERE goal_id = ?
        ''', (goal_id,))
    cursor.execute('''
           DELETE FROM goals WHERE goal_id = ?
       ''', (goal_id,))
    database.commit()
    database.close()

def insert_into_habit_reminder(habit_id, user_id, reminder_time, next_reminder):
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
        INSERT INTO habit_reminders(habit_id, user_id, reminder_time, next_reminder) VALUES(?, ?, ?, ?)
    ''', (habit_id, user_id, reminder_time, next_reminder))
    database.commit()
    database.close()

def get_habit_id(user_id):
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
        SELECT * FROM habit_tracker WHERE user_id = ?
    ''', (user_id,))
    habit_id = cursor.fetchall()
    database.close()
    return habit_id

def insert_into_habit_tracker(user_id, habit_title, description, reminder_time):
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
        INSERT INTO habit_tracker(user_id, habit_title, description, reminder_time) VALUES (?, ?, ?, ?)
    ''', (user_id, habit_title, description, reminder_time))
    database.commit()
    database.close()


def insert_into_progress_updates(user_id, habit_id, progress, update_time):
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
        INSERT INTO progress_updates(user_id, habit_id, progress, update_time) VALUES(?, ?, ?, ?)
    ''', (user_id, habit_id, progress, update_time))
    database.commit()
    database.close()

def get_habit_progress_details(habit_id):
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
        SELECT * FROM progress_updates WHERE habit_id = ?
    ''', (habit_id,))
    habit = cursor.fetchone()
    database.close()
    return habit

def get_habit_details(habit_id):
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute('''
        SELECT * FROM habit_tracker WHERE habit_id = ?
    ''', (habit_id,))
    habit = cursor.fetchone()
    database.close()
    return habit


def insert_into_progress(user_id, habit_id, field, progress_text, now):
    valid_fields = ['progress', 'notes']
    if field not in valid_fields:
        raise ValueError(f"Invalid field: {field}")
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    cursor.execute(f'''
        INSERT INTO progress_updates(user_id, habit_id, {field}, update_time) VALUES(?, ?, ?, ?)
    ''', (user_id, habit_id, progress_text, now))
    database.commit()
    database.close()



def update_progress(habit_id, field, progress_text, now):
    valid_fields = ['progress', 'notes']
    if field not in valid_fields:
        raise ValueError(f"Invalid field: {field}")
    database = sqlite3.connect('habit_tracker.db')
    cursor = database.cursor()
    try:
        cursor.execute(f'''
                UPDATE progress_updates
                SET {field} = ?, update_time = ?
                WHERE habit_id = ?
            ''', (progress_text, now, habit_id))
        database.commit()
    except sqlite3.Error as e:
        print(f"Error updating progress: {e}")
    finally:
        database.close()












