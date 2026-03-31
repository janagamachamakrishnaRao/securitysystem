from flask import Flask, render_template, request, redirect, session, send_file
from datetime import datetime, timedelta

from models import (
    init_db,
    insert_entry,
    get_all_entries,
    search_entries,
    mark_exit,
    delete_entry,
    get_statistics,
    generate_today_report,
    get_recent_activity
)

app = Flask(__name__)
app.secret_key = "pennar_security_system_super_secret_key"
app.permanent_session_lifetime = timedelta(hours=8)

init_db()

# USERS
USERS = {
    "admin": {"password": "Admin@123", "role": "admin"},
    "guard": {"password": "Guard@123", "role": "guard"},
    "hr": {"password": "HR@123", "role": "admin"},
    "manager": {"password": "Manager@123", "role": "admin"}
}

# DATETIME FILTER
def format_datetime(value):
    if value:
        try:
            dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%d-%m-%Y %I:%M %p")
        except:
            return value
    return ""

app.jinja_env.filters["format_datetime"] = format_datetime


# INTRO
@app.route("/")
def intro():
    return render_template("intro.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = USERS.get(username)

        if user and user["password"] == password:

            session.permanent = True
            session["username"] = username
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect("/dashboard")
            else:
                return redirect("/entry")

        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)


# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ENTRY PAGE
@app.route("/entry")
def entry():
    if "username" not in session:
        return redirect("/login")
    return render_template("entry.html")


# NEW ENTRY (dashboard button)
@app.route("/new_entry")
def new_entry():
    if "username" not in session:
        return redirect("/login")
    return render_template("entry.html")


# SUBMIT ENTRY
@app.route("/submit", methods=["POST"])
def submit():

    if "username" not in session:
        return redirect("/login")

    entry_type = request.form.get("entry_type")
    name = request.form.get("visitor_name")
    purpose = request.form.get("purpose")
    to_whom = request.form.get("to_whom")

    entered_by = session["username"]

    insert_entry(entry_type, name, purpose, to_whom, entered_by)

    # ✅ Correct redirect
    return redirect("/inside")


# LOGS
@app.route("/logs")
def logs():

    if "username" not in session:
        return redirect("/login")

    search_query = request.args.get("search")
    filter_type = request.args.get("filter")

    if search_query:
        data = search_entries(search_query)

    elif filter_type == "today":
        all_data = get_all_entries()
        today = datetime.now().strftime("%Y-%m-%d")
        data = [r for r in all_data if r[6].startswith(today)]

    else:
        data = get_all_entries()

    total_count, inside_count, completed_count, today_count = get_statistics()

    return render_template(
        "logs.html",
        data=data,
        search_query=search_query,
        total_count=total_count,
        inside_count=inside_count,
        completed_count=completed_count,
        today_count=today_count
    )

# EXIT
@app.route("/exit/<int:id>")
def exit_entry(id):

    if "username" not in session:
        return redirect("/login")

    mark_exit(id)
    return redirect("/inside")


# DELETE
@app.route("/delete/<int:id>")
def delete_record(id):

    if "username" not in session:
        return redirect("/login")

    if session["role"] != "admin":
        return "Access Denied"

    delete_entry(id)
    return redirect("/logs")


# INSIDE (🔥 FIXED PROPERLY)
from datetime import datetime

@app.route("/inside")
def inside():

    if "username" not in session:
        return redirect("/login")

    rows = get_all_entries()

    data = []
    today = datetime.now().strftime("%Y-%m-%d")

    today_inside = 0

    for row in rows:
        if row[7] is None:
            data.append(row)

            if row[6].startswith(today):
                today_inside += 1

    return render_template("inside.html", data=data, today_inside=today_inside)


# RECENT
@app.route("/recent")
def recent():

    if "username" not in session:
        return redirect("/login")

    data = get_recent_activity()

    return render_template("recent.html", data=data)


# DASHBOARD
@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect("/login")

    total_count, inside_count, completed_count, today_count = get_statistics()
    data = get_all_entries()

    return render_template(
        "dashboard.html",
        data=data,
        total_count=total_count,
        inside_count=inside_count,
        completed_count=completed_count,
        today_count=today_count
    )


# EXPORT
@app.route("/export_today")
def export_today():

    if "username" not in session:
        return redirect("/login")

    filename = generate_today_report()

    return send_file(filename, as_attachment=True)


# RUN
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)