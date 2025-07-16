# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from functools import wraps
# from werkzeug.security import generate_password_hash, check_password_hash
# import jwt
# import datetime
# import sqlite3
# import logging

# app = Flask(__name__)
# CORS(app)

# def get_db_connection():
#     conn = sqlite3.connect('tasks.db')
#     conn.row_factory = sqlite3.Row
#     conn.execute("PRAGMA foreign_keys = ON")
#     return conn

# def init_db():
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username TEXT NOT NULL UNIQUE,
#             password TEXT NOT NULL
#         )
#     ''')
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS tasks (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id INTEGER NOT NULL,
#             title TEXT NOT NULL,
#             completed BOOLEAN NOT NULL DEFAULT 0,
#             FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
#         )
#     ''')
#     cursor.execute("SELECT id FROM users WHERE username = 'testuser'")
#     if not cursor.fetchone():
#         from werkzeug.security import generate_password_hash
#         hashed = generate_password_hash("test123")
#         cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('testuser', hashed))

#     conn.commit()
#     conn.close()

# def validate_json(*required_fields):
#     def decorator(f):
#         @wraps(f)
#         def wrapped(*args, **kwargs):
#             data = request.get_json()
#             if not data:
#                 return jsonify({"error": "Missing JSON body"}), 400
#             for field in required_fields:
#                 val = data.get(field)
#                 if val is None or (isinstance(val, str) and not val.strip()):
#                     return jsonify({"error": f"Field '{field}' is required and cannot be empty"}), 400
#             return f(*args, **kwargs)
#         return wrapped
#     return decorator

# @app.route('/register', methods=['POST'])
# def register():
#     try:
#         data = request.get_json()
#         username = data.get('username')
#         password = data.get('password')

#         if not username or not password:
#             return jsonify({'message': 'Username and password required'}), 400

#         # Bypass database and just assign a dummy user_id
#         user_id = 1  # ✅ Hardcoded just to move forward

#         return jsonify({'user_id': user_id}), 200

#     except Exception as e:
#         return jsonify({'message': str(e)}), 500

# # @app.route("/register", methods=["POST"])
# # def register():
# #     data = request.get_json()
# #     logging.info(f"Received registration data: {data}")
# #     username = data.get("username")
# #     password = data.get("password")

# #     if not username or not password:
# #         logging.warning("Missing username or password in registration")
# #         return jsonify({"error": "Username and password required"}), 400

# #     hashed_password = generate_password_hash(password)

# #     conn = get_db_connection()
# #     cursor = conn.cursor()

# #     # Check if username already exists
# #     cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
# #     if cursor.fetchone():
# #         conn.close()
# #         return jsonify({"error": "Username already taken"}), 409

# #     cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
# #     conn.commit()
# #     user_id = cursor.lastrowid
# #     conn.close()
# #     logging.info(f"User '{username}' registered successfully with id {user_id}")
# #     return jsonify({"message": "User registered successfully", "user_id": user_id}), 201

# @app.route("/")
# def home():
#     return "To-Do API is live!"

# @app.route("/tasks", methods=["GET"])
# def get_tasks():
#     user_id = request.args.get('user_id')
#     if not user_id:
#         return jsonify({"error": "User ID is required"}), 400
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT id, title, completed FROM tasks WHERE user_id = ?", (user_id,))
#     tasks = [
#         {"id": row["id"], "title": row["title"], "completed": bool(row["completed"])}
#         for row in cursor.fetchall()
#     ]
#     conn.close()
#     return jsonify(tasks), 200

# @app.route("/tasks", methods=["POST"])
# @validate_json('title', 'user_id')
# def create_task():
#     data = request.get_json()
#     user_id = data.get("user_id")
#     title = data.get('title').strip()

#     if not user_id or not title:
#         return jsonify({"error": "User ID and title are required"}), 400
    
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO tasks (user_id, title, completed) VALUES (?, ?, ?)", (user_id, title, 0))
#     conn.commit()
#     new_id = cursor.lastrowid
#     conn.close()
#     return jsonify({"id": new_id, "title": title, "completed": False}), 201

# @app.route("/tasks/<int:task_id>", methods=["PATCH"])
# def update_task(task_id):
#     data = request.get_json()
#     if not data:
#         return jsonify({"error": "Missing JSON body"}), 400

#     title = data.get('title')
#     completed = data.get('completed')

#     if title is not None and (not isinstance(title, str) or not title.strip()):
#         return jsonify({"error": "Title must be a non-empty string"}), 400

#     if completed is not None and not isinstance(completed, bool):
#         return jsonify({"error": "Completed must be a boolean"}), 400

#     if title is None and completed is None:
#         return jsonify({"error": "At least one of 'title' or 'completed' must be provided"}), 400

#     conn = get_db_connection()
#     cursor = conn.cursor()
#     if title is not None:
#         cursor.execute("UPDATE tasks SET title = ? WHERE id = ?", (title.strip(), task_id))
#     if completed is not None:
#         cursor.execute("UPDATE tasks SET completed = ? WHERE id = ?", (int(completed), task_id))
#     conn.commit()
#     changes = conn.total_changes
#     conn.close()

#     if changes == 0:
#         return jsonify({"error": "Task not found"}), 404

#     return jsonify({"id": task_id, "title": title, "completed": completed}), 200

# @app.route("/tasks/<int:task_id>", methods=["DELETE"])
# def delete_task(task_id):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
#     conn.commit()
#     changes = conn.total_changes
#     conn.close()

#     if changes == 0:
#         return jsonify({"error": "Task not found"}), 404

#     return jsonify({"message": f"Task {task_id} deleted"}), 200

# if __name__ == "__main__":
#     init_db()
#     app.run(debug=True)

from flask import Flask, request, jsonify
import sqlite3

from flask_cors import CORS

app = Flask(__name__)
CORS(app)
def get_db_connection():
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# Initialize DB with minimal tables (run once)
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Username already taken'}), 409
    conn.close()
    return jsonify({'user_id': user_id}), 201

@app.route('/tasks', methods=['GET'])
def get_tasks():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify([])  # empty if no user_id
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, completed FROM tasks WHERE user_id = ?", (user_id,))
    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    user_id = data.get('user_id')
    title = data.get('title', '').strip()
    if not user_id or not title:
        return jsonify({'error': 'User ID and task title required'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (user_id, title, completed) VALUES (?, ?, ?)", (user_id, title, 0))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': task_id, 'title': title, 'completed': False}), 201

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
