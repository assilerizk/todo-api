from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import sqlite3

app = Flask(__name__)
CORS(app, origins=["http://localhost:5500", "http://127.0.0.1:5500"])  # Make sure both are allowed

def init_db():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def validate_json(*required_fields):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            data = request.get_json()
            if not data:
                return jsonify({"error": "Missing JSON body"}), 400
            for field in required_fields:
                val = data.get(field)
                if val is None or (isinstance(val, str) and not val.strip()):
                    return jsonify({"error": f"Field '{field}' is required and cannot be empty"}), 400
            return f(*args, **kwargs)
        return wrapped
    return decorator

@app.route("/")
def home():
    return "To-Do API is live!"

@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, completed FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    tasks = [{"id": r[0], "title": r[1], "completed": bool(r[2])} for r in rows]
    return jsonify(tasks)

@app.route("/tasks", methods=["POST"])
@validate_json('title')
def create_task():
    data = request.get_json()
    title = data.get('title').strip()
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, completed) VALUES (?, ?)", (title, 0))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": new_id, "title": title, "completed": False}), 201

@app.route("/tasks/<int:task_id>", methods=["PATCH"])
def update_task(task_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    title = data.get('title')
    completed = data.get('completed')

    if title is not None and (not isinstance(title, str) or not title.strip()):
        return jsonify({"error": "Title must be a non-empty string"}), 400

    if completed is not None and not isinstance(completed, bool):
        return jsonify({"error": "Completed must be a boolean"}), 400

    if title is None and completed is None:
        return jsonify({"error": "At least one of 'title' or 'completed' must be provided"}), 400

    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    if title is not None:
        cursor.execute("UPDATE tasks SET title = ? WHERE id = ?", (title.strip(), task_id))
    if completed is not None:
        cursor.execute("UPDATE tasks SET completed = ? WHERE id = ?", (int(completed), task_id))
    conn.commit()
    changes = conn.total_changes
    conn.close()

    if changes == 0:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({"id": task_id, "title": title, "completed": completed}), 200

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    changes = conn.total_changes
    conn.close()

    if changes == 0:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({"message": f"Task {task_id} deleted"}), 200

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
