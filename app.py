from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = "smart-travel-development-key"

DATABASE = "travel.db"


# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create database table automatically
def initialize_database():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            budget REAL NOT NULL,
            interests TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# Homepage
@app.route("/")
def home():
    return render_template("index.html")


# Display trip planner form
@app.route("/planner")
def planner():
    return render_template("trip_planner.html")


# Process submitted trip form
@app.route("/create-trip", methods=["POST"])
def create_trip():
    destination = request.form.get("destination", "").strip()
    start_date = request.form.get("start_date", "").strip()
    end_date = request.form.get("end_date", "").strip()
    budget_text = request.form.get("budget", "").strip()
    interests = request.form.getlist("interests")

    # Validate required fields
    if not destination or not start_date or not end_date or not budget_text:
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("planner"))

    # Validate dates
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)

        if start < date.today():
            flash("The start date cannot be in the past.", "error")
            return redirect(url_for("planner"))

        if end < start:
            flash("The end date must be on or after the start date.", "error")
            return redirect(url_for("planner"))

    except ValueError:
        flash("Please enter valid travel dates.", "error")
        return redirect(url_for("planner"))

    # Validate budget
    try:
        budget = float(budget_text)

        if budget <= 0:
            flash("Your budget must be greater than zero.", "error")
            return redirect(url_for("planner"))

    except ValueError:
        flash("Please enter a valid numeric budget.", "error")
        return redirect(url_for("planner"))

    # Validate interests
    allowed_interests = {
        "nature",
        "adventure",
        "culture",
        "food",
        "sightseeing",
        "relaxation"
    }

    if not interests or not set(interests).issubset(allowed_interests):
        flash("Please select at least one valid interest.", "error")
        return redirect(url_for("planner"))

    # Save trip to database
    conn = get_db_connection()

    cursor = conn.execute("""
        INSERT INTO trips
        (destination, start_date, end_date, budget, interests)
        VALUES (?, ?, ?, ?, ?)
    """, (
        destination,
        start_date,
        end_date,
        budget,
        ", ".join(interests)
    ))

    trip_id = cursor.lastrowid

    conn.commit()
    conn.close()

    flash("Your trip has been created successfully!", "success")

    return redirect(url_for("trip_confirmation", trip_id=trip_id))


# Display trip confirmation
@app.route("/trip/<int:trip_id>")
def trip_confirmation(trip_id):
    conn = get_db_connection()

    trip = conn.execute(
        "SELECT * FROM trips WHERE id = ?",
        (trip_id,)
    ).fetchone()

    conn.close()

    if trip is None:
        return "Trip not found.", 404

    return render_template("trip_confirmation.html", trip=trip)


# Travel services page
@app.route("/services")
def services():
    return """
        <h1>Travel Service Booking</h1>
        <p>Travel services module is under development.</p>
        <a href="/">Back to Home</a>
    """


# Booking history page
@app.route("/bookings")
def bookings():
    return """
        <h1>My Bookings</h1>
        <p>Your booking history will appear here.</p>
        <a href="/">Back to Home</a>
    """


# Initialize the database when the application starts
initialize_database()


if __name__ == "__main__":
    app.run(debug=True)