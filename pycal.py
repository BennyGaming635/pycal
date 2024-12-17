from flask import Flask, render_template, request, redirect, jsonify, url_for
import sqlite3

app = Flask(__name__)

# Initialize Database
def init_db():
    with sqlite3.connect("db.sqlite3") as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS events (
                            id INTEGER PRIMARY KEY,
                            title TEXT NOT NULL,
                            date TEXT NOT NULL
                          )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS todos (
                            id INTEGER PRIMARY KEY,
                            task TEXT NOT NULL,
                            completed INTEGER DEFAULT 0,
                            list_name TEXT DEFAULT 'General'
                          )''')

init_db()

# Calendar Routes
@app.route("/")
@app.route("/calendar")
def calendar():
    return render_template("calendar.html")

@app.route("/calendar/events")
def calendar_events():
    with sqlite3.connect("db.sqlite3") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, date FROM events")
        events = cursor.fetchall()
    return jsonify([{"id": e[0], "title": e[1], "start": e[2]} for e in events])

@app.route("/add_event", methods=["POST"])
def add_event():
    title = request.form["title"]
    date = request.form["date"]
    with sqlite3.connect("db.sqlite3") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO events (title, date) VALUES (?, ?)", (title, date))
    return redirect(url_for("calendar"))

# To-Do Routes
@app.route("/todo/<list_name>")
def todo(list_name="General"):
    with sqlite3.connect("db.sqlite3") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM todos WHERE list_name = ? ORDER BY completed ASC, id DESC", (list_name,))
        todos = cursor.fetchall()
    return render_template("todo.html", todos=todos, list_name=list_name)

@app.route("/add_task", methods=["POST"])
def add_task():
    task = request.form["task"]
    list_name = request.form["list_name"]
    with sqlite3.connect("db.sqlite3") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO todos (task, list_name) VALUES (?, ?)", (task, list_name))
    return redirect(url_for("todo", list_name=list_name))

@app.route("/toggle_task/<int:task_id>")
def toggle_task(task_id):
    with sqlite3.connect("db.sqlite3") as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE todos SET completed = 1 - completed WHERE id = ?", (task_id,))
    return redirect(request.referrer)

@app.route("/delete_task/<int:task_id>")
def delete_task(task_id):
    with sqlite3.connect("db.sqlite3") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM todos WHERE id = ?", (task_id,))
    return redirect(request.referrer)

if __name__ == "__main__":
    app.run(debug=True)
