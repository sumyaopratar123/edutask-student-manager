"""
Student Task Management System
A clean, beginner-friendly Flask web application for students to organize,
track, and manage college tasks, assignments, practicals, projects, and exam preparation.
"""

import os
import sqlite3
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, abort

# Initialize Flask application
app = Flask(__name__)
# Secret key for session security and flash messaging
app.secret_key = "student_task_manager_secret_key_change_in_production"

# Database path (stored in the same directory as this script)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "tasks.db")

# Predefined categories and priorities
CATEGORIES = ["Assignment", "Practical", "Project", "Exam Preparation", "Personal"]
PRIORITIES = ["Low", "Medium", "High"]


def get_db_connection():
    """
    Creates and returns a connection to the SQLite database.
    row_factory = sqlite3.Row allows accessing columns by name like dictionary keys.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initializes the SQLite database:
    1. Creates the 'tasks' table if it doesn't already exist.
    2. Seeds initial sample tasks if the table is empty, so students and teachers
       have realistic data to view immediately during demonstrations.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create the tasks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            due_date TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    # Check if table is empty, and seed sample tasks if so
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    if count == 0:
        today = date.today()
        yesterday = (today - timedelta(days=2)).strftime("%Y-%m-%d")
        tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        in_3_days = (today + timedelta(days=3)).strftime("%Y-%m-%d")
        in_7_days = (today + timedelta(days=7)).strftime("%Y-%m-%d")

        sample_tasks = [
            (
                "DBMS Lab Practical Journal Submission",
                "Complete experiment 8 (PL/SQL Triggers and Cursors) and get it verified by the lab faculty.",
                "Practical",
                yesterday,
                "High",
                "Pending"
            ),
            (
                "Operating Systems Assignment 2",
                "Solve scheduling algorithm problems (FCFS, Round Robin, SJF) with Gantt charts.",
                "Assignment",
                tomorrow,
                "High",
                "Pending"
            ),
            (
                "Computer Networks Seminar Presentation",
                "Prepare 15 slides on TCP/IP 3-Way Handshake and congestion control protocols.",
                "Project",
                in_3_days,
                "Medium",
                "Pending"
            ),
            (
                "Data Structures Mid-Term Exam Prep",
                "Revise Binary Search Trees, AVL Trees, and Graph Traversal algorithms (BFS & DFS).",
                "Exam Preparation",
                in_7_days,
                "High",
                "Pending"
            ),
            (
                "Update Engineering Portfolio & Resume",
                "Add recent semester projects, GitHub repositories, and tech stack details.",
                "Personal",
                tomorrow,
                "Low",
                "Completed"
            )
        ]

        cursor.executemany("""
            INSERT INTO tasks (title, description, category, due_date, priority, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, sample_tasks)
        conn.commit()

    conn.close()


def enrich_task(task_row):
    """
    Helper function to convert a sqlite3.Row object into a mutable dictionary
    and add dynamic helper properties:
    - is_overdue: True if task is Pending and due_date < today
    - days_info: Friendly human-readable text (e.g. 'Due today', 'Overdue by 2 days', etc.)
    """
    task = dict(task_row)
    today = date.today()
    try:
        due = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
        diff = (due - today).days

        if task["status"] == "Completed":
            task["is_overdue"] = False
            task["days_info"] = "Completed"
        elif diff < 0:
            task["is_overdue"] = True
            days_over = abs(diff)
            task["days_info"] = f"Overdue by {days_over} day{'s' if days_over > 1 else ''}"
        elif diff == 0:
            task["is_overdue"] = False
            task["days_info"] = "Due today"
        elif diff == 1:
            task["is_overdue"] = False
            task["days_info"] = "Due tomorrow"
        else:
            task["is_overdue"] = False
            task["days_info"] = f"Due in {diff} days"
    except (ValueError, TypeError):
        task["is_overdue"] = False
        task["days_info"] = task.get("due_date", "")

    return task


def get_task_counts():
    """
    Calculates summary counts dynamically from the database:
    - total: All tasks
    - pending: Tasks with status 'Pending'
    - completed: Tasks with status 'Completed'
    - overdue: Tasks with status 'Pending' and due_date < today
    """
    today_str = date.today().strftime("%Y-%m-%d")
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM tasks")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'Pending'")
    pending = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'Completed'")
    completed = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'Pending' AND due_date < ?", (today_str,))
    overdue = cursor.fetchone()[0]

    conn.close()

    completion_rate = round((completed / total * 100)) if total > 0 else 0

    return {
        "total": total,
        "pending": pending,
        "completed": completed,
        "overdue": overdue,
        "completion_rate": completion_rate
    }


# Context processor makes current date and common lists available to all Jinja templates
@app.context_processor
def inject_global_data():
    return {
        "today_str": date.today().strftime("%Y-%m-%d"),
        "ALL_CATEGORIES": CATEGORIES,
        "ALL_PRIORITIES": PRIORITIES
    }


# ==========================================
# ROUTES
# ==========================================

@app.route("/")
def index():
    """
    Dashboard page:
    - Summary metrics (Total, Pending, Completed, Overdue)
    - Progress bar
    - List of 5 recently added tasks
    - Upcoming high-priority / imminent deadlines
    """
    counts = get_task_counts()
    today_str = date.today().strftime("%Y-%m-%d")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch 5 most recent tasks
    cursor.execute("SELECT * FROM tasks ORDER BY id DESC LIMIT 5")
    recent_tasks_raw = cursor.fetchall()
    recent_tasks = [enrich_task(t) for t in recent_tasks_raw]

    # Fetch urgent upcoming tasks (pending tasks with due dates in next 7 days, ordered by due_date)
    cursor.execute("""
        SELECT * FROM tasks
        WHERE status = 'Pending' AND due_date >= ?
        ORDER BY due_date ASC, CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END
        LIMIT 4
    """, (today_str,))
    upcoming_tasks_raw = cursor.fetchall()
    upcoming_tasks = [enrich_task(t) for t in upcoming_tasks_raw]

    conn.close()

    return render_template(
        "index.html",
        counts=counts,
        recent_tasks=recent_tasks,
        upcoming_tasks=upcoming_tasks
    )


@app.route("/tasks")
def tasks():
    """
    All Tasks view with comprehensive search, filtering, and sorting:
    - Search: matches keyword in title or description
    - Status filter: 'all', 'pending', 'completed', 'overdue'
    - Category filter: 'all' or specific category
    - Priority filter: 'all' or 'Low', 'Medium', 'High'
    - Sort options: 'due_asc', 'due_desc', 'newest', 'oldest', 'priority'
    """
    counts = get_task_counts()
    today_str = date.today().strftime("%Y-%m-%d")

    # Read query parameters
    search_query = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "all").strip().lower()
    category_filter = request.args.get("category", "all").strip()
    priority_filter = request.args.get("priority", "all").strip()
    sort_by = request.args.get("sort", "due_asc").strip()

    # Build SQL dynamically with parameterized inputs for security
    sql_parts = ["SELECT * FROM tasks WHERE 1=1"]
    params = []

    # Filter by search keyword
    if search_query:
        sql_parts.append("AND (title LIKE ? OR description LIKE ?)")
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    # Filter by status
    if status_filter == "pending":
        sql_parts.append("AND status = 'Pending'")
    elif status_filter == "completed":
        sql_parts.append("AND status = 'Completed'")
    elif status_filter == "overdue":
        sql_parts.append("AND status = 'Pending' AND due_date < ?")
        params.append(today_str)

    # Filter by category
    if category_filter and category_filter != "all":
        sql_parts.append("AND category = ?")
        params.append(category_filter)

    # Filter by priority
    if priority_filter and priority_filter != "all":
        sql_parts.append("AND priority = ?")
        params.append(priority_filter)

    # Sorting
    if sort_by == "due_desc":
        sql_parts.append("ORDER BY due_date DESC")
    elif sort_by == "newest":
        sql_parts.append("ORDER BY id DESC")
    elif sort_by == "oldest":
        sql_parts.append("ORDER BY id ASC")
    elif sort_by == "priority":
        sql_parts.append("ORDER BY CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END, due_date ASC")
    else:  # default 'due_asc'
        sql_parts.append("ORDER BY due_date ASC, CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END")

    final_sql = " ".join(sql_parts)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(final_sql, params)
    tasks_raw = cursor.fetchall()
    conn.close()

    tasks_list = [enrich_task(t) for t in tasks_raw]

    return render_template(
        "tasks.html",
        tasks=tasks_list,
        counts=counts,
        current_status=status_filter,
        current_category=category_filter,
        current_priority=priority_filter,
        current_sort=sort_by,
        search_query=search_query
    )


@app.route("/tasks/add", methods=["GET", "POST"])
def add_task():
    """
    Add a new task:
    - GET: Displays the blank task creation form.
    - POST: Validates inputs, saves to database, flashes confirmation message.
    """
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        due_date = request.form.get("due_date", "").strip()
        priority = request.form.get("priority", "").strip()

        # Server-side validation
        errors = []
        if not title:
            errors.append("Task title is required.")
        elif len(title) > 150:
            errors.append("Task title must be 150 characters or less.")

        if category not in CATEGORIES:
            errors.append(f"Invalid category selected. Must be one of: {', '.join(CATEGORIES)}.")

        if priority not in PRIORITIES:
            errors.append("Invalid priority selected. Must be Low, Medium, or High.")

        if not due_date:
            errors.append("Due date is required.")
        else:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                errors.append("Invalid due date format. Please use YYYY-MM-DD.")

        if errors:
            for error in errors:
                flash(error, "danger")
            # Return form with pre-filled inputs
            return render_template(
                "add_task.html",
                form_data={
                    "title": title,
                    "description": description,
                    "category": category,
                    "due_date": due_date,
                    "priority": priority
                }
            )

        # Insert new task into database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (title, description, category, due_date, priority, status)
            VALUES (?, ?, ?, ?, ?, 'Pending')
        """, (title, description, category, due_date, priority))
        conn.commit()
        conn.close()

        flash(f"Task '{title}' created successfully!", "success")
        return redirect(url_for("tasks"))

    # Default values for GET request
    default_date = (date.today() + timedelta(days=2)).strftime("%Y-%m-%d")
    return render_template(
        "add_task.html",
        form_data={
            "due_date": default_date,
            "category": "Assignment",
            "priority": "Medium"
        }
    )


@app.route("/tasks/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    """
    Edit an existing task:
    - GET: Loads task details into edit form.
    - POST: Validates inputs, updates SQLite record, flashes success message.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task_row = cursor.fetchone()

    if task_row is None:
        conn.close()
        flash(f"Task #{task_id} not found.", "danger")
        return redirect(url_for("tasks"))

    task = enrich_task(task_row)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        due_date = request.form.get("due_date", "").strip()
        priority = request.form.get("priority", "").strip()
        status = request.form.get("status", "Pending").strip()

        # Validation
        errors = []
        if not title:
            errors.append("Task title is required.")
        elif len(title) > 150:
            errors.append("Task title must be 150 characters or less.")

        if category not in CATEGORIES:
            errors.append("Invalid category selected.")

        if priority not in PRIORITIES:
            errors.append("Invalid priority selected.")

        if status not in ["Pending", "Completed"]:
            errors.append("Invalid status selected.")

        if not due_date:
            errors.append("Due date is required.")
        else:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                errors.append("Invalid due date format.")

        if errors:
            for error in errors:
                flash(error, "danger")
            conn.close()
            return render_template("edit_task.html", task=task)

        # Update in database
        cursor.execute("""
            UPDATE tasks
            SET title = ?, description = ?, category = ?, due_date = ?, priority = ?, status = ?
            WHERE id = ?
        """, (title, description, category, due_date, priority, status, task_id))
        conn.commit()
        conn.close()

        flash(f"Task '{title}' updated successfully!", "success")
        return redirect(url_for("tasks"))

    conn.close()
    return render_template("edit_task.html", task=task)


@app.route("/tasks/toggle/<int:task_id>", methods=["POST"])
def toggle_task(task_id):
    """
    Quickly toggle completion status between 'Pending' and 'Completed'.
    Updates the database immediately.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, status FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()

    if task is None:
        conn.close()
        flash(f"Task #{task_id} not found.", "danger")
        return redirect(url_for("tasks"))

    new_status = "Completed" if task["status"] == "Pending" else "Pending"
    cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
    conn.commit()
    conn.close()

    flash(f"Task '{task['title']}' marked as {new_status}!", "success")
    # Redirect back to where user was or fallback to tasks list
    return redirect(request.referrer or url_for("tasks"))


@app.route("/tasks/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    """
    Deletes a task from the SQLite database.
    Requires POST request to prevent accidental deletion via URL links.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()

    if task is None:
        conn.close()
        flash(f"Task #{task_id} not found.", "danger")
        return redirect(url_for("tasks"))

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    flash(f"Task '{task['title']}' was deleted successfully.", "info")
    return redirect(request.referrer or url_for("tasks"))


@app.errorhandler(404)
def page_not_found(e):
    """Friendly 404 error page"""
    return render_template("base.html", error_title="Page Not Found", error_message="The page you requested does not exist."), 404


# Initialize database when this script runs
init_db()

if __name__ == "__main__":
    # Use the port provided by Cloud Run; default to 5000 for local development.
    port = int(os.environ.get("PORT", 5000))
    print("=" * 60)
    print(" Student Task Management System is running!")
    print(f" Listening on port: {port}")
    print(" Press Ctrl+C in this terminal to stop the server.")
    print("=" * 60)
    app.run(host="0.0.0.0", port=port, debug=False)
