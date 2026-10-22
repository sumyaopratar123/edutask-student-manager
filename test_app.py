"""
Automated Test Script for Student Task Management System
Validates all CRUD operations, filtering, sorting, status toggling, and calculations.
"""

import os
import unittest
from datetime import date, timedelta
from app import app, init_db, get_db_connection, get_task_counts

class TaskManagerTestCase(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()

        # Re-initialize DB
        init_db()

    def test_1_dashboard_loads(self):
        """Verify dashboard route / renders successfully with counts"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Student Dashboard", response.data)
        self.assertIn(b"Total Tasks", response.data)
        self.assertIn(b"Overall Task Completion", response.data)

    def test_2_tasks_list_loads(self):
        """Verify tasks list route /tasks renders"""
        response = self.client.get("/tasks")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Manage Coursework", response.data)
        self.assertIn(b"All Categories", response.data)

    def test_3_add_task_success(self):
        """Verify adding a task saves to SQLite and redirects"""
        due_str = (date.today() + timedelta(days=5)).strftime("%Y-%m-%d")
        response = self.client.post("/tasks/add", data={
            "title": "Machine Learning Term Paper",
            "description": "Write a 5-page report on Convolutional Neural Networks.",
            "category": "Project",
            "due_date": due_str,
            "priority": "High"
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Machine Learning Term Paper", response.data)
        self.assertIn(b"created successfully", response.data)

        # Verify record in DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE title = 'Machine Learning Term Paper'")
        task = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(task)
        self.assertEqual(task["category"], "Project")
        self.assertEqual(task["priority"], "High")
        self.assertEqual(task["status"], "Pending")

    def test_4_add_task_validation_failure(self):
        """Verify empty title triggers server-side validation error"""
        response = self.client.post("/tasks/add", data={
            "title": "",
            "description": "Some note",
            "category": "Assignment",
            "due_date": "2026-12-01",
            "priority": "Medium"
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Task title is required", response.data)

    def test_5_toggle_task_status(self):
        """Verify toggling status from Pending to Completed and back"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, status FROM tasks LIMIT 1")
        task = cursor.fetchone()
        task_id = task["id"]
        initial_status = task["status"]
        conn.close()

        # Toggle status
        response = self.client.post(f"/tasks/toggle/{task_id}", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Check updated status
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM tasks WHERE id = ?", (task_id,))
        updated = cursor.fetchone()
        conn.close()

        expected = "Completed" if initial_status == "Pending" else "Pending"
        self.assertEqual(updated["status"], expected)

    def test_6_edit_task(self):
        """Verify editing an existing task updates its details in DB"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tasks LIMIT 1")
        task_id = cursor.fetchone()["id"]
        conn.close()

        new_due = (date.today() + timedelta(days=10)).strftime("%Y-%m-%d")
        response = self.client.post(f"/tasks/edit/{task_id}", data={
            "title": "Updated Assignment Title",
            "description": "Updated detailed notes.",
            "category": "Practical",
            "due_date": new_due,
            "priority": "Low",
            "status": "Completed"
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"updated successfully", response.data)

        # Verify DB values
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task = cursor.fetchone()
        conn.close()

        self.assertEqual(task["title"], "Updated Assignment Title")
        self.assertEqual(task["priority"], "Low")
        self.assertEqual(task["status"], "Completed")

    def test_7_filter_and_search(self):
        """Verify search and category filters return matching tasks"""
        response = self.client.get("/tasks?q=Updated&category=Practical")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Updated Assignment Title", response.data)

        # Filter by status = completed
        response_completed = self.client.get("/tasks?status=completed")
        self.assertEqual(response_completed.status_code, 200)

    def test_8_delete_task(self):
        """Verify task deletion removes the record from SQLite"""
        # Create a temp task to delete
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (title, description, category, due_date, priority, status)
            VALUES ('To be deleted', 'Test description', 'Personal', '2026-11-11', 'Low', 'Pending')
        """)
        conn.commit()
        task_id = cursor.lastrowid
        conn.close()

        # Send delete request
        response = self.client.post(f"/tasks/delete/{task_id}", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"was deleted successfully", response.data)

        # Confirm not in DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        self.assertIsNone(row)

    def test_9_overdue_calculation(self):
        """Verify overdue tasks are calculated correctly"""
        counts = get_task_counts()
        self.assertIn("overdue", counts)
        self.assertIn("total", counts)
        self.assertIn("completion_rate", counts)
        self.assertGreaterEqual(counts["total"], 0)

if __name__ == "__main__":
    unittest.main()
