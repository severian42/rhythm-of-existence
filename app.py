import gradio as gr
import sqlite3
import pandas as pd
from datetime import datetime, time, timedelta, date
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import calendar
import random
import json

DB_FILE = "life_tracker.db"

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        category TEXT,
        subcategory TEXT,
        start_time TEXT,
        end_time TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS qualitative_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        life_score INTEGER,
        work_score INTEGER,
        health_score INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quantitative_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        wake_up_time TEXT,
        workouts INTEGER,
        meditation_minutes INTEGER,
        brain_training_minutes INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        category TEXT,
        description TEXT,
        target_value REAL,
        current_value REAL,
        start_date TEXT,
        end_date TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_settings (
        user_id INTEGER PRIMARY KEY,
        default_wake_time TEXT,
        work_weight REAL,
        life_weight REAL,
        health_weight REAL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS custom_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        category_name TEXT,
        subcategories TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_checklist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        checklist_data TEXT,
        notes TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def create_connection():
    return sqlite3.connect(DB_FILE)

def add_user_profile(name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def delete_user_profile(name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE name = ?", (name,))
    conn.commit()
    conn.close()

def generate_placeholder_data(user_name):
    conn = create_connection()
    cursor = conn.cursor()
    
    # Get user ID
    cursor.execute("SELECT id FROM users WHERE name = ?", (user_name,))
    user_id = cursor.fetchone()[0]
    
    # Generate placeholder data for the last 30 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    categories = ["Work", "Life", "Health", "Sleep"]
    subcategories = {
        "Work": ["Meetings", "Project A", "Project B"],
        "Life": ["Family", "Friends", "Hobbies"],
        "Health": ["Exercise", "Meditation", "Personal Care"],
        "Sleep": ["Night Sleep"]
    }
    
    for day in range(31):
        current_date = start_date + timedelta(days=day)
        
        # Daily activities
        for category in categories:
            for _ in range(random.randint(1, 3)):
                subcategory = random.choice(subcategories[category])
                start_time = time(hour=random.randint(0, 23), minute=random.randint(0, 59))
                duration = timedelta(hours=random.randint(1, 4))
                end_time = (datetime.combine(current_date, start_time) + duration).time()
                
                cursor.execute('''
                INSERT INTO daily_activities (user_id, date, category, subcategory, start_time, end_time)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, current_date.isoformat(), category, subcategory, start_time.isoformat(), end_time.isoformat()))
        
        # Qualitative metrics
        cursor.execute('''
        INSERT INTO qualitative_metrics (user_id, date, life_score, work_score, health_score)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, current_date.isoformat(), random.randint(1, 10), random.randint(1, 10), random.randint(1, 10)))
        
        # Quantitative metrics
        wake_up_time = time(hour=random.randint(5, 9), minute=random.randint(0, 59))
        cursor.execute('''
        INSERT INTO quantitative_metrics (user_id, date, wake_up_time, workouts, meditation_minutes, brain_training_minutes)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, current_date.isoformat(), wake_up_time.isoformat(),
              random.randint(0, 2), random.randint(0, 60), random.randint(0, 60)))
    
    # Generate some goals
    goal_categories = ["Work", "Life", "Health"]
    for category in goal_categories:
        cursor.execute('''
        INSERT INTO goals (user_id, category, description, target_value, current_value, start_date, end_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, category, f"Improve {category.lower()} balance", random.randint(50, 100),
              random.randint(0, 50), start_date.isoformat(), end_date.isoformat()))
    
    # Set user settings
    default_wake_time = time(hour=6, minute=0)
    cursor.execute('''
    INSERT OR REPLACE INTO user_settings (user_id, default_wake_time, work_weight, life_weight, health_weight)
    VALUES (?, ?, ?, ?, ?)
    ''', (user_id, default_wake_time.isoformat(), 1.0, 1.0, 1.0))
    
    conn.commit()
    conn.close()

def get_weekly_data(user_name):
    conn = create_connection()
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)
    
    query = '''
    SELECT date, category, subcategory, start_time, end_time
    FROM daily_activities
    WHERE user_id = (SELECT id FROM users WHERE name = ?) AND date BETWEEN ? AND ?
    ORDER BY date, start_time
    '''
    df = pd.read_sql_query(query, conn, params=(user_name, start_date, end_date))
    conn.close()
    
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Convert start_time and end_time to datetime
    df['start_time'] = pd.to_datetime(df['date'].dt.strftime('%Y-%m-%d') + ' ' + df['start_time'])
    df['end_time'] = pd.to_datetime(df['date'].dt.strftime('%Y-%m-%d') + ' ' + df['end_time'])
    
    return df

def get_monthly_data(user_name, year=None, month=None):
    if year is None or month is None:
        current_date = datetime.now()
        year = year or current_date.year
        month = month or current_date.month
    
    conn = create_connection()
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]}"
    query = '''
    SELECT date, category, subcategory, start_time, end_time
    FROM daily_activities
    WHERE user_id = (SELECT id FROM users WHERE name = ?) AND date BETWEEN ? AND ?
    ORDER BY date, start_time
    '''
    df = pd.read_sql_query(query, conn, params=(user_name, start_date, end_date))
    conn.close()
    
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Convert start_time and end_time to datetime
    df['start_time'] = pd.to_datetime(df['date'].dt.strftime('%Y-%m-%d') + ' ' + df['start_time'])
    df['end_time'] = pd.to_datetime(df['date'].dt.strftime('%Y-%m-%d') + ' ' + df['end_time'])
    
    return df

def format_monthly_data(df, year, month):
    # Create a DataFrame with all days of the month
    all_days = pd.date_range(start=f"{year}-{month:02d}-01", end=f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]}", freq='D')
    calendar_df = pd.DataFrame({'date': all_days})
    
    # Calculate total hours for each category
    df['duration'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 3600
    category_hours = df.groupby(['date', 'category'])['duration'].sum().unstack(fill_value=0)
    
    # Merge with the calendar DataFrame
    calendar_df = calendar_df.merge(category_hours, left_on='date', right_index=True, how='left')
    calendar_df = calendar_df.fillna(0)
    
    return calendar_df

def save_day_activities(user_name, date, work, life, health, sleep):
    conn = create_connection()
    cursor = conn.cursor()
    
    # Delete existing activities for the day
    cursor.execute('''
    DELETE FROM daily_activities
    WHERE user_id = (SELECT id FROM users WHERE name = ?) AND date = ?
    ''', (user_name, date))
    
    # Insert new activities
    activities = [
        ('Work', work),
        ('Life', life),
        ('Health', health),
        ('Sleep', sleep)
    ]
    
    for category, hours in activities:
        if hours > 0:
            start_time = '00:00'
            end_time = f'{int(hours):02d}:{int((hours % 1) * 60):02d}'
            cursor.execute('''
            INSERT INTO daily_activities (user_id, date, category, subcategory, start_time, end_time)
            VALUES ((SELECT id FROM users WHERE name = ?), ?, ?, 'Default', ?, ?)
            ''', (user_name, date, category, start_time, end_time))
    
    conn.commit()
    conn.close()

def log_activity(user_name, date, category, subcategory, start_time, end_time):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO daily_activities (user_id, date, category, subcategory, start_time, end_time)
    VALUES ((SELECT id FROM users WHERE name = ?), ?, ?, ?, ?, ?)
    ''', (user_name, date, category, subcategory, start_time, end_time))
    conn.commit()
    conn.close()

def get_activities(user_name, date):
    conn = create_connection()
    categories, _ = get_custom_categories(user_name)
    category_list = ', '.join([f"'{cat}'" for cat in categories])
    
    query = f'''
    SELECT category, subcategory, start_time, end_time
    FROM daily_activities
    WHERE user_id = (SELECT id FROM users WHERE name = ?) AND date = ? AND category IN ({category_list})
    ORDER BY start_time
    '''
    df = pd.read_sql_query(query, conn, params=(user_name, date))
    conn.close()
    return df

def log_qualitative_metrics(user_name, date, life_score, work_score, health_score):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO qualitative_metrics (user_id, date, life_score, work_score, health_score)
    VALUES ((SELECT id FROM users WHERE name = ?), ?, ?, ?, ?)
    ''', (user_name, date, life_score, work_score, health_score))
    conn.commit()
    conn.close()

def log_quantitative_metrics(user_name, date, wake_up_time, workouts, meditation_minutes, brain_training_minutes):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO quantitative_metrics (user_id, date, wake_up_time, workouts, meditation_minutes, brain_training_minutes)
    VALUES ((SELECT id FROM users WHERE name = ?), ?, ?, ?, ?, ?)
    ''', (user_name, date, wake_up_time, workouts, meditation_minutes, brain_training_minutes))
    conn.commit()
    conn.close()

def get_metrics(user_name, date):
    conn = create_connection()
    qual_query = '''
    SELECT life_score, work_score, health_score
    FROM qualitative_metrics
    WHERE user_id = (SELECT id FROM users WHERE name = ?) AND date = ?
    '''
    quant_query = '''
    SELECT wake_up_time, workouts, meditation_minutes, brain_training_minutes
    FROM quantitative_metrics
    WHERE user_id = (SELECT id FROM users WHERE name = ?) AND date = ?
    '''
    qual_df = pd.read_sql_query(qual_query, conn, params=(user_name, date))
    quant_df = pd.read_sql_query(quant_query, conn, params=(user_name, date))
    conn.close()
    return pd.concat([qual_df, quant_df], axis=1)

def analyze_weekly_data(user_name):
    df = get_weekly_data(user_name)
    df['duration'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 3600
    
    category_summary = df.groupby('category')['duration'].sum().sort_values(ascending=False)
    total_hours = category_summary.sum()
    
    category_percentages = (category_summary / total_hours * 100).round(2)
    
    # Create a more detailed pie chart
    pie_chart = go.Figure(data=[go.Pie(
        labels=category_percentages.index,
        values=category_percentages.values,
        hole=.3,
        textinfo='label+percent',
        insidetextorientation='radial'
    )])
    pie_chart.update_layout(title="Weekly Activity Distribution")
    
    daily_scores = get_weekly_scores(user_name)
    
    # Create a more detailed line chart
    line_chart = go.Figure()
    for column in ['life_score', 'work_score', 'health_score']:
        line_chart.add_trace(go.Scatter(
            x=daily_scores['date'],
            y=daily_scores[column],
            mode='lines+markers',
            name=column.replace('_', ' ').title()
        ))
    line_chart.update_layout(title="Weekly Score Trends", xaxis_title="Date", yaxis_title="Score")
    
    return pie_chart, line_chart, total_hours

def analyze_monthly_data(user_name):
    year, month = datetime.now().year, datetime.now().month
    df = get_monthly_data(user_name, year, month)
    df['duration'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 3600
    
    category_summary = df.groupby('category')['duration'].sum().sort_values(ascending=False)
    total_hours = category_summary.sum()
    
    category_percentages = (category_summary / total_hours * 100).round(2)
    
    pie_chart = px.pie(values=category_percentages.values, names=category_percentages.index, title="Monthly Activity Distribution")
    
    weekly_scores = get_monthly_scores(user_name)
    
    # Use 'date' instead of 'week' for the x-axis
    line_chart = px.line(weekly_scores, x='date', y=['life_score', 'work_score', 'health_score'], title="Monthly Score Trends")
    
    return pie_chart, line_chart, total_hours

def get_monthly_scores(user_name):
    conn = create_connection()
    end_date = datetime.now().date()
    start_date = end_date.replace(day=1)
    
    query = '''
    SELECT 
        date,
        AVG(life_score) as life_score,
        AVG(work_score) as work_score,
        AVG(health_score) as health_score
    FROM qualitative_metrics
    WHERE user_id = (SELECT id FROM users WHERE name = ?) AND date BETWEEN ? AND ?
    GROUP BY date
    ORDER BY date
    '''
    
    df = pd.read_sql_query(query, conn, params=(user_name, start_date, end_date))
    conn.close()
    return df

def get_weekly_scores(user_name):
    conn = create_connection()
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)
    
    query = '''
    SELECT 
        date,
        life_score,
        work_score,
        health_score
    FROM qualitative_metrics
    WHERE user_id = (SELECT id FROM users WHERE name = ?) AND date BETWEEN ? AND ?
    ORDER BY date
    '''
    
    df = pd.read_sql_query(query, conn, params=(user_name, start_date, end_date))
    conn.close()
    return df

def set_goal(user_name, category, description, target_value, start_date, end_date):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO goals (user_id, category, description, target_value, current_value, start_date, end_date)
    VALUES ((SELECT id FROM users WHERE name = ?), ?, ?, ?, 0, ?, ?)
    ''', (user_name, category, description, float(target_value), start_date, end_date))
    conn.commit()
    conn.close()

def get_goals(user_name):
    conn = create_connection()
    query = '''
    SELECT category, description, target_value, current_value, start_date, end_date
    FROM goals
    WHERE user_id = (SELECT id FROM users WHERE name = ?)
    '''
    df = pd.read_sql_query(query, conn, params=(user_name,))
    conn.close()
    return df

def update_goal_progress(user_name, goal_id, current_value):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE goals
    SET current_value = ?
    WHERE id = ? AND user_id = (SELECT id FROM users WHERE name = ?)
    ''', (current_value, goal_id, user_name))
    conn.commit()
    conn.close()

def get_user_settings(user_name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT default_wake_time, work_weight, life_weight, health_weight
    FROM user_settings
    WHERE user_id = (SELECT id FROM users WHERE name = ?)
    ''', (user_name,))
    settings = cursor.fetchone()
    conn.close()
    return settings if settings else (None, 1.0, 1.0, 1.0)

def update_user_settings(user_name, default_wake_time, work_weight, life_weight, health_weight):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO user_settings (user_id, default_wake_time, work_weight, life_weight, health_weight)
    VALUES ((SELECT id FROM users WHERE name = ?), ?, ?, ?, ?)
    ''', (user_name, default_wake_time, work_weight, life_weight, health_weight))
    conn.commit()
    conn.close()

def parse_date(date_str):
    if date_str.lower() == 'today':
        return datetime.now().date()
    else:
        return datetime.strptime(date_str, "%Y-%m-%d").date()

# Define a custom theme with a more modern look
custom_theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="gray",
    neutral_hue="slate",
    font=("Inter", "sans-serif")
)

# Custom CSS for full-screen layout
custom_css = """
html, body {
    margin: 0;
    padding: 0;
    height: 100%;
    font-size: 16px; /* Base font size */
}
.gradio-container {
    width: 100vw !important;
    max-width: 100vw !important;
    padding: 0 !important;
    margin: 0 !important;
    font-size: 1rem; /* Use relative units */
}
#component-0 {
    max-height: none !important;
    overflow: visible;
}
.main {
    height: auto !important;
    max-height: none !important;
    display: flex;
    flex-direction: row;
}
.contain {
    max-width: 100% !important;
    height: auto !important;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
}
.tabs {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
}
.tab-content {
    flex-grow: 1;
    overflow-y: visible;
}
.main-content {
    height: auto;
    display: flex;
    flex-direction: column;
}
footer {
    display: none !important;
}

/* Increase text size for various elements */
.gradio-container, .gradio-container *, .gradio-container .form, .gradio-container input, .gradio-container select, .gradio-container textarea {
    font-size: 1.1rem !important;
}

/* Increase text size for headers */
.gradio-container h1 { font-size: 2.5rem !important; }
.gradio-container h2 { font-size: 2rem !important; }
.gradio-container h3 { font-size: 1.75rem !important; }
.gradio-container h4 { font-size: 1.5rem !important; }

/* Increase text size for buttons */
.gradio-container button {
    font-size: 1.1rem !important;
    padding: 0.5rem 1rem !important;
}

/* Increase text size for dropdown options */
.gradio-container select option {
    font-size: 1.1rem !important;
}

/* Adjust padding and margins for better spacing */
.gradio-container .form > *, .gradio-container .form > div > * {
    margin-bottom: 1rem !important;
}

<script>
function edit_day(date) {
    document.querySelector('input[data-testid="textbox"]').value = date;
    document.querySelector('button[data-testid="button"]').click();
}
</script>
"""

# Create the main Gradio interface with the custom theme and CSS
with gr.Blocks(theme=custom_theme, css=custom_css) as demo:
    create_tables() 
    with gr.Row(equal_height=True):
        # Left sidebar
        with gr.Column(scale=1, min_width=200):
            gr.Markdown("## Life Tracking System")
            user_name = gr.Dropdown(label="User Name", choices=["John Doe"], value="John Doe")
            date = gr.Textbox(label="Date", value="today", placeholder="YYYY-MM-DD")
            
            with gr.Group():
                gr.Markdown("### Quick Glance")
                today_life_score = gr.Number(label="Today's Life Score", value=0)
                today_work_score = gr.Number(label="Today's Work Score", value=0)
                today_health_score = gr.Number(label="Today's Health Score", value=0)
                wake_up_time = gr.Textbox(label="Wake-up Time", value="")
                total_activities = gr.Number(label="Total Activities", value=0)
            
            quick_log_btn = gr.Button("Quick Log")
            
            # Add buttons for adding and deleting user profiles
            new_user_name = gr.Textbox(label="New User Name")
            add_user_btn = gr.Button("Add User")
            delete_user_btn = gr.Button("Delete User")
        
        # Main content area
        with gr.Column(scale=4):
            with gr.Tabs() as tabs:
                # Dashboard Tab
                with gr.TabItem("Dashboard"):
                    with gr.Row():
                        with gr.Column(scale=2):
                            gr.Markdown("### Log Daily Metrics")
                            life_score = gr.Slider(label="Life Score", minimum=1, maximum=10, step=1)
                            work_score = gr.Slider(label="Work Score", minimum=1, maximum=10, step=1)
                            health_score = gr.Slider(label="Health Score", minimum=1, maximum=10, step=1)
                            workouts = gr.Number(label="Workouts", minimum=0, step=1)
                            meditation_minutes = gr.Number(label="Meditation (minutes)", minimum=0)
                            brain_training_minutes = gr.Number(label="Brain Training (minutes)", minimum=0)
                            log_metrics_btn = gr.Button("Log Metrics")
                        
                        with gr.Column(scale=2):
                            gr.Markdown("### Log Activity")
                            category = gr.Dropdown(label="Category", choices=["Work", "Life", "Health", "Sleep"])
                            subcategory = gr.Textbox(label="Subcategory")
                            start_time = gr.Textbox(label="Start Time (HH:MM)")
                            end_time = gr.Textbox(label="End Time (HH:MM)")
                            log_activity_btn = gr.Button("Log Activity")
                    
                    gr.Markdown("### Today's Overview")
                    with gr.Row():
                        today_activities = gr.DataFrame(label="Today's Activities")
                        today_metrics = gr.DataFrame(label="Today's Metrics")
                    
                    gr.Markdown("### Weekly Summary")
                    with gr.Row():
                        weekly_pie_chart = gr.Plot(label="Activity Distribution")
                        weekly_line_chart = gr.Plot(label="Score Trends")
                    
                    update_dashboard_btn = gr.Button("Refresh Dashboard")

                # Analysis Tab
                with gr.TabItem("Analysis"):
                    analysis_period = gr.Radio(["Weekly", "Monthly"], label="Analysis Period", value="Weekly")
                    update_analysis_btn = gr.Button("Update Analysis")
                    with gr.Row():
                        analysis_pie_chart = gr.Plot(label="Activity Distribution")
                        analysis_line_chart = gr.Plot(label="Score Trends")
                    analysis_total_hours = gr.Number(label="Total Hours", precision=2)
                    
                    # Add a detailed breakdown table
                    analysis_breakdown = gr.DataFrame(label="Detailed Breakdown")
                    
                    def update_analysis(user_name, period):
                        if period == "Weekly":
                            pie_chart, line_chart, total_hours = analyze_weekly_data(user_name)
                            breakdown_data = get_weekly_data(user_name)
                        else:
                            pie_chart, line_chart, total_hours = analyze_monthly_data(user_name)
                            breakdown_data = get_monthly_data(user_name)
                        
                        breakdown_data['duration'] = breakdown_data['end_time'] - breakdown_data['start_time']
                        breakdown_data['duration_hours'] = breakdown_data['duration'].dt.total_seconds() / 3600
                        breakdown_summary = breakdown_data.groupby(['category', 'subcategory'])['duration_hours'].sum().reset_index()
                        breakdown_summary = breakdown_summary.sort_values('duration_hours', ascending=False)
                        
                        return pie_chart, line_chart, total_hours, breakdown_summary
                    
                    update_analysis_btn.click(update_analysis, inputs=[user_name, analysis_period], outputs=[analysis_pie_chart, analysis_line_chart, analysis_total_hours, analysis_breakdown])

                # Goals Tab
                with gr.TabItem("Goals"):
                    with gr.Row():
                        goal_category = gr.Dropdown(label="Category", choices=["Work", "Life", "Health"])
                        goal_description = gr.Textbox(label="Goal Description")
                        goal_target = gr.Number(label="Target Value")
                    with gr.Row():
                        goal_start_date = gr.Textbox(label="Start Date", placeholder="YYYY-MM-DD")
                        goal_end_date = gr.Textbox(label="End Date", placeholder="YYYY-MM-DD")
                    set_goal_btn = gr.Button("Set Goal")
                    goals_table = gr.DataFrame(label="Current Goals")

                # Settings Tab
                with gr.TabItem("Settings"):
                    preset_dropdown = gr.Dropdown(label="Preset Templates", choices=["Custom", "Rob Dyrdek", "Student"])
                    default_wake_time = gr.Textbox(label="Default Wake-up Time (HH:MM)")
                    with gr.Row():
                        work_weight = gr.Slider(label="Work Weight", minimum=0, maximum=2, step=0.1, value=1.0)
                        life_weight = gr.Slider(label="Life Weight", minimum=0, maximum=2, step=0.1, value=1.0)
                        health_weight = gr.Slider(label="Health Weight", minimum=0, maximum=2, step=0.1, value=1.0)
                    update_settings_btn = gr.Button("Update Settings")

                # New: Documentation Tab
                with gr.TabItem("Documentation"):
                    gr.Markdown("""
                    # Life Tracking System Documentation

                    Welcome to the Life Tracking System, inspired by Rob Dyrdek's philosophy of maintaining a "Rhythm of Existence". This system is designed to help you monitor and optimize various aspects of your life, including work, health, personal life, and sleep.

                    ## Getting Started

                    1. Use the Setup tab to configure your profile and preferences.
                    2. Choose a preset template or customize your own categories and subcategories.
                    3. Set your default wake-up time and adjust weights for work, life, and health.
                    4. Use the Dashboard to log your daily activities and metrics.
                    5. Review your progress in the Analysis tab.
                    6. Set and track your goals in the Goals tab.

                    ## Key Features

                    - Guided setup process
                    - Daily activity tracking
                    - Qualitative and quantitative metric logging
                    - Weekly and monthly analysis
                    - Visualization and reporting
                    - Goal setting and progress monitoring
                    - Customizable categories and subcategories

                    ## Tips for Success

                    - Be consistent in logging your activities and metrics.
                    - Review your weekly and monthly analyses regularly.
                    - Adjust your goals as needed based on your progress.
                    - Use the preset templates to get started quickly.
                    - Customize your categories and subcategories to fit your lifestyle.

                    ## Rob Dyrdek's Philosophy

                    Rob Dyrdek's approach to life and success emphasizes:
                    1. Passion-driven productivity
                    2. Taking calculated risks
                    3. Setting big goals
                    4. Hard work and perseverance
                    5. Innovation and creativity
                    6. Authenticity in decision-making
                    7. Learning from failures

                    Incorporate these principles into your daily routine to maximize your potential and achieve your goals.

                    For more detailed information on how to use specific features, please refer to the respective tabs in the application.
                    """)

                # New: Daily Checklist Tab
                with gr.TabItem("Daily Checklist"):
                    gr.Markdown("## Daily Checklist and Notes")
                    checklist_date = gr.Textbox(label="Date", value=datetime.now().strftime("%Y-%m-%d"), placeholder="YYYY-MM-DD")
                    
                    with gr.Row():
                        with gr.Column(scale=2):
                            checklist_items = [
                                gr.Checkbox(label="Wake up & Mindfulness (30 minutes)"),
                                gr.Checkbox(label="Exercise (30-45 minutes)"),
                                gr.Checkbox(label="Meditation (20 minutes)"),
                                gr.Checkbox(label="Morning Walk with Nala (1 hour 15 minutes)"),
                                gr.Checkbox(label="Active Learning with Breakfast (1 hour)"),
                                gr.Checkbox(label="Work (3 hours 30 minutes)"),
                                gr.Checkbox(label="Lunch Break (30 minutes)"),
                                gr.Checkbox(label="Work (4 hours)"),
                                gr.Checkbox(label="Active Learning (20 mins - 1 hour, 3x a week)"),
                                gr.Checkbox(label="Brain Training"),
                                gr.Checkbox(label="Reading"),
                                gr.Checkbox(label="Journaling"),
                                gr.Checkbox(label="Evening Reflection"),
                                gr.Checkbox(label="Plan for Tomorrow"),
                            ]
                        
                        with gr.Column(scale=1):
                            notes = gr.TextArea(label="Daily Notes")
                    
                    save_checklist_btn = gr.Button("Save Daily Checklist")
                    load_checklist_btn = gr.Button("Load Checklist for Selected Date")

                    def get_daily_checklist(user_name, date):
                        conn = create_connection()
                        cursor = conn.cursor()
                        cursor.execute('''
                        SELECT checklist_data, notes FROM daily_checklist
                        WHERE user_id = (SELECT id FROM users WHERE name = ?) AND date = ?
                        ''', (user_name, date))
                        result = cursor.fetchone()
                        conn.close()
                        if result:
                            return json.loads(result[0]), result[1]
                        return {}, ""

                    def save_daily_checklist(user_name, date, checklist_data, notes):
                        conn = create_connection()
                        cursor = conn.cursor()
                        cursor.execute('''
                        INSERT OR REPLACE INTO daily_checklist (user_id, date, checklist_data, notes)
                        VALUES ((SELECT id FROM users WHERE name = ?), ?, ?, ?)
                        ''', (user_name, date, json.dumps(checklist_data), notes))
                        conn.commit()
                        conn.close()
                    
                    def save_checklist(user_name, date_str, notes, *checklist_values):
                        try:
                            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                            checklist_data = {item.label: value for item, value in zip(checklist_items, checklist_values)}
                            save_daily_checklist(user_name, date_obj, checklist_data, notes)
                            return "Checklist saved successfully!"
                        except ValueError:
                            return "Invalid date format. Please use YYYY-MM-DD."


                    def load_checklist(user_name, date_str):
                        try:
                            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                            checklist_data, notes_text = get_daily_checklist(user_name, date_obj)
                            checkbox_values = [checklist_data.get(item.label, False) for item in checklist_items]
                            return checkbox_values + [notes_text, "Checklist loaded successfully!"]
                        except ValueError:
                            return [False] * len(checklist_items) + ["", "Invalid date format. Please use YYYY-MM-DD."]

                    save_checklist_btn.click(
                        save_checklist,
                        inputs=[user_name, checklist_date, notes] + checklist_items,
                        outputs=[gr.Text(label="Save Status")]
                    )

                    load_checklist_btn.click(
                        load_checklist,
                        inputs=[user_name, checklist_date],
                        outputs=checklist_items + [notes, gr.Text(label="Load Status")]
                    )

                # Monthly Calendar Tab
                with gr.TabItem("Monthly Calendar"):
                    gr.Markdown("## Monthly Time Allocation")
                    with gr.Row():
                        calendar_date = gr.Textbox(label="Select Month (YYYY-MM)", value=datetime.now().strftime("%Y-%m"))
                        update_calendar_btn = gr.Button("Update Calendar")
                    monthly_calendar = gr.DataFrame(label="Monthly Time Allocation")
                    
                    day_edit_form = gr.Group(visible=False)
                    with day_edit_form:
                        selected_date = gr.Textbox(label="Date")
                        work_hours = gr.Number(label="Work Hours", minimum=0, maximum=24)
                        life_hours = gr.Number(label="Life Hours", minimum=0, maximum=24)
                        health_hours = gr.Number(label="Health Hours", minimum=0, maximum=24)
                        sleep_hours = gr.Number(label="Sleep Hours", minimum=0, maximum=24)
                        save_day_btn = gr.Button("Save")
                    
                    edit_buttons = gr.HTML()  # This will hold our edit buttons

                    def open_day_edit_form(date):
                        return gr.update(visible=True), gr.update(value=date)
                    
                    def save_day_data(user_name, date, work, life, health, sleep):
                        save_day_activities(user_name, date, work, life, health, sleep)
                        return gr.update(visible=False), update_monthly_calendar(user_name, calendar_date.value)
                    
                    save_day_btn.click(
                        save_day_data,
                        inputs=[user_name, selected_date, work_hours, life_hours, health_hours, sleep_hours],
                        outputs=[day_edit_form, monthly_calendar]
                    )
                    
                    def update_monthly_calendar(user_name, date):
                        try:
                            year, month = map(int, date.split('-'))
                        except ValueError:
                            year, month = datetime.now().year, datetime.now().month
                        
                        df = get_monthly_data(user_name, year, month)
                        calendar_df = format_monthly_data(df, year, month)
                        return calendar_df
                    
                    def create_day_buttons(df):
                        buttons_html = ""
                        for _, row in df.iterrows():
                            date = row['date']
                            buttons_html += f'<button onclick="edit_day(\'{date}\')">{date}</button>'
                        return buttons_html
                    
                    update_calendar_btn.click(
                        lambda user, date: (update_monthly_calendar(user, date), create_day_buttons(update_monthly_calendar(user, date))),
                        inputs=[user_name, calendar_date],
                        outputs=[monthly_calendar, edit_buttons]
                    )

    # Event handlers and function definitions
    def log_and_display(user_name, date, category, subcategory, start_time, end_time):
        log_activity(user_name, date, category, subcategory, start_time, end_time)
        activities = get_activities(user_name, date)
        return activities, len(activities)

    def log_and_display_metrics(user_name, date, life_score, work_score, health_score, wake_up_time, workouts, meditation_minutes, brain_training_minutes):
        log_qualitative_metrics(user_name, date, life_score, work_score, health_score)
        log_quantitative_metrics(user_name, date, wake_up_time, workouts, meditation_minutes, brain_training_minutes)
        metrics = get_metrics(user_name, date)
        return metrics, life_score, work_score, health_score, wake_up_time

    def update_dashboard(user_name, date):
        today_activities_data = get_activities(user_name, date)
        today_metrics_data = get_metrics(user_name, date)
        weekly_pie_chart_data, weekly_line_chart_data, total_hours = analyze_weekly_data(user_name)
        
        # Calculate quick glance metrics
        life_score = today_metrics_data['life_score'].values[0] if not today_metrics_data.empty else 0
        work_score = today_metrics_data['work_score'].values[0] if not today_metrics_data.empty else 0
        health_score = today_metrics_data['health_score'].values[0] if not today_metrics_data.empty else 0
        wake_up = today_metrics_data['wake_up_time'].values[0] if not today_metrics_data.empty else ""
        total_acts = len(today_activities_data)
        
        return (today_activities_data, today_metrics_data, weekly_pie_chart_data, weekly_line_chart_data,
                life_score, work_score, health_score, wake_up, total_acts)

    def update_analysis(user_name, period):
        current_date = datetime.now()
        year, month = current_date.year, current_date.month

        if period == "Weekly":
            df = get_weekly_data(user_name)
            scores = get_weekly_scores(user_name)
        else:  # Monthly
            df = get_monthly_data(user_name, year, month)
            scores = get_monthly_scores(user_name)

        # Ensure df is not empty
        if df.empty:
            return px.pie(), px.line(), 0, pd.DataFrame()

        # Calculate duration in hours
        df['duration'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 3600
        
        breakdown_data = df.groupby(['category', 'subcategory'])['duration'].sum().reset_index()
        breakdown_data = breakdown_data.sort_values('duration', ascending=False)
        
        total_hours = breakdown_data['duration'].sum()
        
        pie_chart = px.pie(breakdown_data, values='duration', names='category', title=f"{period} Activity Distribution")
        
        # Ensure 'date' column exists in scores DataFrame
        if 'date' not in scores.columns:
            scores['date'] = scores.index if isinstance(scores.index, pd.DatetimeIndex) else pd.to_datetime(scores.index)
        
        line_chart = px.line(scores, x='date', y=['life_score', 'work_score', 'health_score'], title=f"{period} Score Trends")
        
        return pie_chart, line_chart, total_hours, breakdown_data


    def set_new_goal(user_name, category, description, target, start_date, end_date):
        set_goal(user_name, category, description, target, start_date, end_date)
        return get_goals(user_name)

    def load_user_settings(user_name):
        settings = get_user_settings(user_name)
        return settings[0], settings[1], settings[2], settings[3]

    def save_user_settings(user_name, wake_time, w_weight, l_weight, h_weight):
        update_user_settings(user_name, wake_time, w_weight, l_weight, h_weight)
        return "Settings updated successfully"

    def create_preset_template(preset_name):
        if preset_name == "Rob Dyrdek":
            return {
                "default_wake_time": "05:00",
                "work_weight": 1.0,
                "life_weight": 1.0,
                "health_weight": 1.0,
                "categories": ["Work", "Life", "Health", "Sleep"],
                "subcategories": {
                    "Work": ["Drydek Machine", "Television", "Other"],
                    "Life": ["Rob & Bre", "Kids", "Friends & Social", "Other"],
                    "Health": ["Gym", "Meditation", "Personal Care", "Other"],
                    "Sleep": []
                }
            }
        elif preset_name == "Student":
            return {
                "default_wake_time": "07:00",
                "work_weight": 1.2,
                "life_weight": 0.8,
                "health_weight": 1.0,
                "categories": ["Study", "Life", "Health", "Sleep"],
                "subcategories": {
                    "Study": ["Classes", "Homework", "Research", "Other"],
                    "Life": ["Family", "Friends", "Hobbies", "Other"],
                    "Health": ["Exercise", "Meditation", "Personal Care", "Other"],
                    "Sleep": []
                }
            }
        else:
            # Return None or a default preset if the preset name is not recognized
            return None

    def update_settings_from_preset(preset_name):
        if preset_name == "Custom":
            return gr.update(), gr.update(), gr.update(), gr.update()
        
        preset = create_preset_template(preset_name)
        if preset is None:
            return gr.update(), gr.update(), gr.update(), gr.update()
        
        return (
            gr.update(value=preset.get("default_wake_time", "")),
            gr.update(value=preset.get("work_weight", 1.0)),
            gr.update(value=preset.get("life_weight", 1.0)),
            gr.update(value=preset.get("health_weight", 1.0))
        )

    def finish_guided_setup(user_name, preset, wake_time, w_weight, l_weight, h_weight, categories, subcategories, initial_goal):
        # Save user settings
        update_user_settings(user_name, wake_time, w_weight, l_weight, h_weight)
        
        # Save categories and subcategories
        save_custom_categories(user_name, categories, subcategories)
        
        # Set initial goal
        set_goal(user_name, "General", initial_goal, 100, datetime.now().date(), datetime.now().date() + timedelta(days=30))
        
        return "Setup completed successfully!"

    # Connect event handlers to UI components
    log_activity_btn.click(log_and_display, inputs=[user_name, date, category, subcategory, start_time, end_time], outputs=[today_activities, total_activities])
    log_metrics_btn.click(log_and_display_metrics, inputs=[user_name, date, life_score, work_score, health_score, wake_up_time, workouts, meditation_minutes, brain_training_minutes], outputs=[today_metrics, today_life_score, today_work_score, today_health_score, wake_up_time])
    update_dashboard_btn.click(update_dashboard, inputs=[user_name, date], outputs=[today_activities, today_metrics, weekly_pie_chart, weekly_line_chart, today_life_score, today_work_score, today_health_score, wake_up_time, total_activities])
    update_analysis_btn.click(update_analysis, inputs=[user_name, analysis_period], outputs=[analysis_pie_chart, analysis_line_chart, analysis_total_hours])
    set_goal_btn.click(set_new_goal, inputs=[user_name, goal_category, goal_description, goal_target, goal_start_date, goal_end_date], outputs=[goals_table])
    update_settings_btn.click(save_user_settings, inputs=[user_name, default_wake_time, work_weight, life_weight, health_weight], outputs=[gr.Textbox(label="Settings Status")])
    preset_dropdown.change(update_settings_from_preset, inputs=[preset_dropdown], outputs=[default_wake_time, work_weight, life_weight, health_weight])

    # Additional functions that might be needed

    def save_custom_categories(user_name, categories, subcategories):
        conn = create_connection()
        cursor = conn.cursor()
        
        # First, delete existing custom categories for the user
        cursor.execute("DELETE FROM custom_categories WHERE user_id = (SELECT id FROM users WHERE name = ?)", (user_name,))
        
        # Insert new custom categories
        for category in categories:
            cursor.execute("""
            INSERT INTO custom_categories (user_id, category_name, subcategories)
            VALUES ((SELECT id FROM users WHERE name = ?), ?, ?)
            """, (user_name, category, ','.join(subcategories.get(category, []))))
        
        conn.commit()
        conn.close()

    def get_custom_categories(user_name):
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT category_name, subcategories
        FROM custom_categories
        WHERE user_id = (SELECT id FROM users WHERE name = ?)
        """, (user_name,))
        
        results = cursor.fetchall()
        conn.close()
        
        categories = [row[0] for row in results]
        subcategories = {row[0]: row[1].split(',') for row in results}
        
        return categories, subcategories

    # Add this function to update the category dropdown in the UI
    def update_category_dropdown(user_name):
        categories, _ = get_custom_categories(user_name)
        return gr.update(choices=categories)

    # Connect the update_category_dropdown function to the user_name input
    user_name.change(update_category_dropdown, inputs=[user_name], outputs=[category])

    # Add event handlers for adding and deleting user profiles
    def add_user(new_name):
        add_user_profile(new_name)
        generate_placeholder_data(new_name)
        return gr.update(choices=get_user_list(), value=new_name)

    def delete_user(name):
        delete_user_profile(name)
        return gr.update(choices=get_user_list(), value=get_user_list()[0] if get_user_list() else None)

    add_user_btn.click(add_user, inputs=[new_user_name], outputs=[user_name])
    delete_user_btn.click(delete_user, inputs=[user_name], outputs=[user_name])

    # Function to get the list of users
    def get_user_list():
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM users")
        users = [row[0] for row in cursor.fetchall()]
        if not users:
            cursor.execute("INSERT INTO users (name) VALUES (?)", ("John Doe",))
            conn.commit()
            users = ["John Doe"]
        conn.close()
        return users

    # Update the user_name dropdown when the interface loads
    demo.load(lambda: gr.update(choices=get_user_list()), outputs=[user_name])

    # Launch the application
    demo.launch()