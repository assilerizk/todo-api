from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app, origins=["http://localhost:5500"])


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

    tasks = []
    for row in rows:
        task = {
            "id": row[0],
            "title": row[1],
            "completed": row[2]
        }
        tasks.append(task)
    return jsonify(tasks)    


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    title = data.get("title")

    if not title:
        return jsonify({"error": "Title is required"}), 400

    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, completed) VALUES (?, ?)", (title, 0))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "id": new_id,
        "title": title,
        "completed": 0
    }), 201

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

@app.route("/tasks/<int:task_id>", methods=["PATCH"])
def update_task(task_id):
    data = request.get_json()
    title = data.get('title')
    completed = data.get("completed")

    if completed is not None and not isinstance(completed, bool):
        return jsonify({"error": "Field 'completed' must be boolean"}), 400

    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()

    if title is not None:
        cursor.execute('UPDATE tasks SET title = ? WHERE id = ?', (title, task_id))

    if completed is not None:
        cursor.execute("UPDATE tasks SET completed = ? WHERE id = ?", (int(completed), task_id))

    conn.commit()
    changes = conn.total_changes
    conn.close()

    if changes == 0:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({"id": task_id, "title": title, "completed": completed}), 200

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
