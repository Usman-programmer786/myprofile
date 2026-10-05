from flask import Flask, request, render_template, session, redirect, url_for
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
import secrets

app = Flask(__name__)

app.secret_key = os.environ["FLASK_SECRET_KEY"]


#connect sqlite3
def get_db():
    conn = sqlite3.connect("messages.db")
    conn.row_factory = sqlite3.Row
    return conn
 
    #creating Tables   
def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    
#writing admin table
def create_admin():
    conn = get_db()

    existing_admin = conn.execute(
        "SELECT id FROM admins LIMIT 1"
    ).fetchone()

    if existing_admin is None:
        password_hash = generate_password_hash("1234")

        conn.execute(
            "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
            ("admin", password_hash)
        )

        conn.commit()

    conn.close()


# Home page
@app.route("/")
def home():
    name = "MUHAMMAD USMAN"
    return render_template("Profile.html", name = name)


#login
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db()

        admin = conn.execute(
            "SELECT * FROM admins WHERE username = ?",
            (username,)
        ).fetchone()

        conn.close()

        if admin is None:
            return render_template(
                "login.html",
                error="Invalid username or password"
            )

        if not check_password_hash(
            admin["password_hash"],
            password
        ):
            return render_template(
                "login.html",
                error="Invalid username or password"
            )

        session["logged_in"] = True
        session["admin_id"] = admin["id"]
        session["username"] = admin["username"]

        return redirect(url_for("admin"))

    return render_template("login.html")
    
    
 #logout
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))   
    

#settings
@app.route("/settings", methods=["GET", "POST"])
def settings():

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if request.method == "POST":

        current_password = request.form.get("current_password", "").strip()
        new_username = request.form.get("new_username", "").strip()
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Current password is always required
        if not current_password:
            return render_template(
                "settings.html",
                error="Current password is required."
            )

        conn = get_db()

        admin = conn.execute(
            "SELECT * FROM admins WHERE id = ?",
            (session["admin_id"],)
        ).fetchone()

        if not admin:
            conn.close()
            session.clear()
            return redirect(url_for("login"))

        # Verify current password
        if not check_password_hash(
            admin["password_hash"],
            current_password
        ):
            conn.close()

            return render_template(
                "settings.html",
                error="Current password is incorrect."
            )

        # Nothing was entered to change
        if not new_username and not new_password:
            conn.close()

            return render_template(
                "settings.html",
                error="Enter a new username or password."
            )

        # -------------------------
        # USERNAME CHANGE
        # -------------------------

        if new_username:

            if len(new_username) < 3:
                conn.close()

                return render_template(
                    "settings.html",
                    error="Username must be at least 3 characters long."
                )

            existing_username = conn.execute(
                "SELECT id FROM admins WHERE username = ? AND id != ?",
                (new_username, session["admin_id"])
            ).fetchone()

            if existing_username:
                conn.close()

                return render_template(
                    "settings.html",
                    error="Username already exists."
                )

            conn.execute(
                "UPDATE admins SET username = ? WHERE id = ?",
                (new_username, session["admin_id"])
            )

            session["username"] = new_username

        # -------------------------
        # PASSWORD CHANGE
        # -------------------------

        if new_password:

            if len(new_password) < 6:
                conn.close()

                return render_template(
                    "settings.html",
                    error="New password must be at least 6 characters long."
                )

            if new_password != confirm_password:
                conn.close()

                return render_template(
                    "settings.html",
                    error="New passwords do not match."
                )

            new_hash = generate_password_hash(new_password)

            conn.execute(
                "UPDATE admins SET password_hash = ? WHERE id = ?",
                (new_hash, session["admin_id"])
            )

        conn.commit()
        conn.close()

        return render_template(
            "settings.html",
            success="Settings updated successfully."
        )

    return render_template("settings.html")
                
# Contact form
@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    conn = get_db()

    conn.execute(
        "INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
        (name, email, message)
    )

    conn.commit()
    conn.close()

    return render_template(
        "success.html",
        name=name,
        email=email,
        message=message
    )
    
init_db()
create_admin()
def get_messages():
    conn = get_db()

    messages = conn.execute(
        "SELECT * FROM messages"
    ).fetchall()

    conn.close()

    return messages

@app.route("/messages")
def messages():

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    all_messages = get_messages()

    return render_template(
        "messages.html",
        messages=all_messages
    )

    
@app.route("/admin")
def admin():

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    all_messages = get_messages()

    return render_template(
        "admin.html",
        messages=all_messages
    )     
           
    
@app.route("/delete/<int:message_id>", methods=["POST"])
def delete_message(message_id):

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    conn = get_db()

    # Check whether message exists
    existing_message = conn.execute(
        "SELECT id FROM messages WHERE id = ?",
        (message_id,)
    ).fetchone()

    if existing_message is None:
        conn.close()
        return "Message not found", 404

    # Delete message
    conn.execute(
        "DELETE FROM messages WHERE id = ?",
        (message_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("messages"))
    
    
@app.route("/edit/<int:message_id>")
def edit_message(message_id):

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    conn = get_db()

    message = conn.execute(
        "SELECT * FROM messages WHERE id = ?",
        (message_id,)
    ).fetchone()

    conn.close()

    if message is None:
        return "Message not found", 404

    return render_template(
        "edit.html",
        message=message
    )
    
    
@app.route("/edit/<int:message_id>", methods=["POST"])
def update_message(message_id):

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()

    # Basic validation
    if not name or not email or not message:
        return "All fields are required", 400

    conn = get_db()

    # Check whether message exists
    existing_message = conn.execute(
        "SELECT id FROM messages WHERE id = ?",
        (message_id,)
    ).fetchone()

    if existing_message is None:
        conn.close()
        return "Message not found", 404

    # Update message
    conn.execute(
        """
        UPDATE messages
        SET name = ?, email = ?, message = ?
        WHERE id = ?
        """,
        (name, email, message, message_id)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("messages"))

# Start Flask server
if __name__ == "__main__":
    app.run(debug=True)
