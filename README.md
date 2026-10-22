# 🎓 Student Task Management System

A clean, modern, and beginner-friendly web application designed for college students to organize, prioritize, and track their coursework, lab practicals, assignments, projects, and exam preparation.

Built with **Python (Flask)**, **SQLite3**, **Jinja2 templates**, **HTML5**, **CSS3**, and **Vanilla JavaScript**.

---

## 📌 1. Project Overview & Objectives

College students face multiple concurrent academic deadlines across theory assignments, laboratory practical submissions, semester mini-projects, and exam revisions. Missing submissions or mismanaging time leads to academic stress and lower grades.

**EduTask - Student Task Management System** solves this by providing:
1. **Centralized Academic Hub:** All coursework items categorized under Assignments, Practicals, Projects, Exam Preparation, or Personal goals.
2. **Dynamic Overdue Tracking:** Automatically detects passed deadlines for pending tasks and highlights them in bold red badges.
3. **Progress Visualization:** Visual progress bar calculating the live percentage of completed tasks.
4. **Instant Status Toggling:** One-click task completion toggling directly from the dashboard or task table.
5. **Search & Multi-criteria Filtering:** Filter tasks by status, category, priority, and sort by due dates or importance.

---

## 🛠️ 2. Technology Stack

- **Backend:** Python 3.x with **Flask** (lightweight WSGI web framework)
- **Database:** **SQLite3** (`tasks.db` created and auto-seeded on first launch)
- **Templating Engine:** **Jinja2** (server-side HTML rendering)
- **Frontend UI:** **HTML5** & **CSS3** (custom responsive SaaS dashboard, no heavy third-party CSS libraries)
- **Interactivity:** **Vanilla JavaScript** (sidebar drawer, delete confirmation modal, auto-fading flash alerts, form validation)
- **Development Environment:** Windows (Powershell / Command Prompt)

---

## 🏛️ 3. Architecture & System Flow

```
+-------------------------------------------------------------+
|                      Client Browser                         |
|  - HTML5 dashboard views & Jinja2 rendered pages            |
|  - CSS3 SaaS styling (responsive flexbox & grid)            |
|  - JavaScript for modals, mobile drawer & form validation   |
+-------------------------------------------------------------+
                                ▲  | HTTP GET / POST
                                |  ▼
+-------------------------------------------------------------+
|                       Flask Backend                         |
|                       (`app.py`)                            |
|  - Route controllers: /, /tasks, /tasks/add, /tasks/edit... |
|  - Server-side input validation                             |
|  - Dynamic metrics & overdue days calculation               |
+-------------------------------------------------------------+
                                ▲  | Parameterized SQL
                                |  ▼
+-------------------------------------------------------------+
|                     SQLite Database                         |
|                       (`tasks.db`)                          |
|  - Table: `tasks` (id, title, description, category,        |
|                    due_date, priority, status, created_at)  |
+-------------------------------------------------------------+
```

### How the Components Interact:
1. **Frontend to Flask:** When a student navigates to a URL or submits a form, the browser issues an HTTP request (`GET` or `POST`) to the Flask web server.
2. **Flask to SQLite:** The Flask controller executes parameterized SQL queries using Python's native `sqlite3` driver, ensuring fast execution and complete protection against SQL injection attacks.
3. **SQLite to Template:** Query results are converted to dictionary objects, enriched with calculated overdue flags and days countdowns, and rendered into Jinja2 HTML templates.
4. **Template to Browser:** The finished HTML is sent back to the browser and styled seamlessly with `style.css`.

---

## 📁 4. Project Folder Structure

```
student_task_manager/
├── app.py                  # Core Flask backend with routes and database operations
├── tasks.db                # SQLite database (auto-created on first run)
├── requirements.txt        # Python package dependencies (Flask)
├── README.md               # Complete setup, technical documentation & presentation guide
├── test_app.py             # Automated unit tests covering all routes & features
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Master layout with sidebar, navbar, flash messages & modal
│   ├── index.html          # Main Dashboard with metrics, progress bar & recent tasks
│   ├── tasks.html          # Tasks list with search, category/priority filters & sorting
│   ├── add_task.html       # Task creation form with server & client validation
│   └── edit_task.html      # Task modification form with pre-filled values
└── static/                 # Static assets
    ├── style.css           # Modern SaaS dashboard design, badges & responsive styles
    └── script.js           # Modal handler, mobile drawer toggle & flash animations
```

---

## 🗄️ 5. Database Schema

The database `tasks.db` contains a single table `tasks`:

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Unique identifier for each task |
| `title` | `TEXT` | `NOT NULL` | Coursework title (e.g., DBMS Lab Experiment 4) |
| `description`| `TEXT` | `NULLABLE` | Detailed notes, submission guidelines, links |
| `category` | `TEXT` | `NOT NULL` | Assignment, Practical, Project, Exam Preparation, or Personal |
| `due_date` | `TEXT` | `NOT NULL` | Deadline in `YYYY-MM-DD` format |
| `priority` | `TEXT` | `NOT NULL` | `Low`, `Medium`, or `High` |
| `status` | `TEXT` | `NOT NULL DEFAULT 'Pending'`| `Pending` or `Completed` |
| `created_at` | `TIMESTAMP`| `DEFAULT CURRENT_TIMESTAMP` | Date and time when the task was added |

### Overdue Calculation Logic
A task is dynamically classified as **Overdue** if:
$$\text{status} = \text{'Pending'} \quad \text{AND} \quad \text{due\_date} < \text{today's date}$$

---

## 🚀 6. Step-by-Step Windows Setup Instructions

### Prerequisites
- Windows 10 or Windows 11
- Python 3.8 or higher installed on your computer.
  *(Make sure **"Add Python to PATH"** was checked during Python installation).*

### Step 1: Open Terminal in Project Directory
Open **PowerShell** or **Command Prompt** and navigate to the project directory:
```powershell
cd C:\Users\ASUS\.gemini\antigravity\scratch\student_task_manager
```

### Step 2: (Optional) Create a Python Virtual Environment
Creating a virtual environment ensures clean dependencies:
```powershell
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Required Dependencies
Install Flask using `requirements.txt`:
```powershell
pip install -r requirements.txt
```

### Step 4: Run the Application
Start the Flask development server:
```powershell
python app.py
```

You will see output similar to:
```text
============================================================
 Student Task Management System is running!
 Local URL: http://127.0.0.1:5000
 Press Ctrl+C in this terminal to stop the server.
============================================================
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Step 5: Open in Your Web Browser
Open your preferred browser (Google Chrome, Microsoft Edge, Firefox) and visit:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🧪 7. Feature Testing Guide

To test and demonstrate all features of the application:

1. **Viewing Dashboard Metrics:**
   - On the homepage `http://127.0.0.1:5000`, observe the 4 metric cards: **Total Tasks**, **Pending Tasks**, **Completed Tasks**, and **Overdue Tasks**.
   - Notice the **Overall Task Completion** progress bar dynamically reflecting the percentage of finished tasks.

2. **Creating a New Task (Add Task):**
   - Click the blue **"Add New Task"** button in the sidebar or top navigation.
   - Enter a title (e.g., *"Web Technology Lab 5"*), choose category *"Practical"*, select deadline date, and priority *"High"*.
   - Click **"Save Task"**.
   - Notice the green confirmation message: *"Task 'Web Technology Lab 5' created successfully!"*.

3. **Toggling Completion Status:**
   - In the task list, click the circular checkbox next to any pending task.
   - The status immediately updates to **Completed**, the title shows a strikethrough effect, and the dashboard completion rate increases!
   - Click it again to return the task to **Pending**.

4. **Editing a Task:**
   - Click the pencil edit icon next to any task.
   - Change the priority to *"Medium"* or modify the due date.
   - Click **"Update Task"**; the changes will be persisted immediately in SQLite.

5. **Searching & Filtering Tasks:**
   - Go to **"All Tasks"** from the sidebar.
   - Type a keyword like *"Journal"* in the search box and press Enter.
   - Use the **Category** dropdown to show only *"Assignment"* or *"Project"*.
   - Click the **Overdue** tab to see tasks whose due dates have passed.
   - Click **"Reset All Filters"** to clear the criteria.

6. **Deleting a Task with Confirmation:**
   - Click the trash can icon next to a task.
   - A modal dialog appears asking: *"Are you sure you want to permanently delete this task?"*.
   - Click **"Cancel"** to abort, or click **"Yes, Delete Task"** to permanently remove it.

7. **Running Automated Unit Tests:**
   Run the included test suite in your terminal:
   ```powershell
   python test_app.py
   ```
   You should see `Ran 9 tests in 0.4xxs ... OK`.

---

## 🎤 8. College Project Presentation Guide

When presenting this project to your college professors or external examiner:

### 1. Introduction (30 seconds)
> *"Good morning, Respected Faculty. Today I am presenting my project: the **Student Task Management System (EduTask)**. It is a full-stack web application developed using Python Flask, SQLite, and modern responsive web technologies to help engineering students systematically manage their coursework, assignments, practical submissions, and exam revisions."*

### 2. Live Demo Flow (2 to 3 minutes)
1. **Show the Dashboard:** Point out the 4 dynamic cards (Total, Pending, Completed, Overdue) and the progress bar. Explain how these metrics are calculated live from the SQLite database.
2. **Demonstrate Overdue Detection:** Point out the red badge on overdue tasks. Explain: *"The system compares the task due date against today's date dynamically. If a task is pending and the deadline has elapsed, it is automatically flagged as overdue."*
3. **Create a Task:** Add a sample task like *"AI Term Project Phase 1"* with High priority and show the flash success notification.
4. **Demonstrate 1-Click Toggle:** Check the completion checkbox and show how the progress percentage instantly adjusts.
5. **Show Filter & Search:** Filter by Category *"Practical"* and Priority *"High"* to show how students can find urgent submissions quickly.
6. **Show Safe Deletion:** Trigger the delete button to demonstrate the confirmation modal that prevents accidental deletions.

### 3. Common Viva Questions & Answers

- **Q1: Why did you choose SQLite instead of MySQL or PostgreSQL?**
  *Answer:* SQLite is serverless, zero-configuration, and stores the entire database in a single lightweight file (`tasks.db`). For an individual student task management tool and college presentation, it provides maximum portability without requiring external database servers to be installed or configured.

- **Q2: How do you prevent SQL Injection attacks?**
  *Answer:* We use parameterized SQL queries with `?` placeholders (e.g., `cursor.execute("SELECT * FROM tasks WHERE category = ?", (category,))`). The SQLite driver safely escapes all user input before execution.

- **Q3: How does the frontend communicate with Flask?**
  *Answer:* Through standard HTTP protocols (`GET` and `POST`). Flask uses the Jinja2 templating engine to inject server-side Python data directly into HTML templates, allowing fast server-side rendering without frontend framework overhead.

- **Q4: How is responsiveness handled?**
  *Answer:* Using CSS3 Flexbox, CSS Grid, and media queries (`@media (max-width: 768px)`). On mobile devices, the left sidebar becomes a slide-out drawer accessible via the hamburger button.
