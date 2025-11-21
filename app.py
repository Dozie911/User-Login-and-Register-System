from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret-change-me")  # change in real apps

# --- Database settings: update to match your phpMyAdmin MySQL account ---
DB_CONFIG = {
    "host": "localhost",
    "database": "flask_app_db",   # the database you created in phpMyAdmin
    "user": "root",               # or the dedicated user you created in phpMyAdmin
    "password": "",               # put the password for that user here
    "charset": "utf8mb4",
}

def get_db_connection():
    """Return a new connection to the MySQL database or None if error."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print("Database connection error:", e)
        return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # Basic server-side validation
        if not username or not password:
            flash("Both username and password are required.", "danger")
            return redirect(url_for("signup"))

        if len(username) < 3:
            flash("Username must be at least 3 characters.", "danger")
            return redirect(url_for("signup"))

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return redirect(url_for("signup"))

        # Hash the password before storing
        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        if conn is None:
            flash("Could not connect to the database. Check your DB settings.", "danger")
            return redirect(url_for("signup"))

        try:
            cursor = conn.cursor()
            insert_sql = "INSERT INTO tbl_user (username, password_hash) VALUES (%s, %s)"
            cursor.execute(insert_sql, (username, password_hash))
            conn.commit()
            flash("Signup successful! You can now log in (login not implemented here).", "success")
            return redirect(url_for("index"))
        except mysql.connector.IntegrityError:
            flash("Username already taken. Please choose another.", "warning")
            return redirect(url_for("signup"))
        except Error as e:
            print("Database error:", e)
            flash("An error occurred while creating the account.", "danger")
            return redirect(url_for("signup"))
        finally:
            try:
                cursor.close()
                conn.close()
            except Exception:
                pass

    # GET request: render signup form
    return render_template("signup.html")


if __name__ == "__main__":
    # debug=True is helpful during development; remove for production
    app.run(debug=True)
