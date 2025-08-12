from flask import Flask, redirect, render_template, request, url_for, flash
import json
import os
from form import Registration
import logging
# logging.basicConfig(filename='app.log', level=logging.DEBUG)

# Remove all handlers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Add both file and console logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
app.secret_key = 'student_recored'

FILENAME = 'Resgistered_Students'
ATTENDANCE_FILE = 'attendance_records'


# ---------- Utility Functions With Error Handling ----------
def save_student(data):
    try:
        if os.path.exists(FILENAME):
            with open(FILENAME, 'r') as f:
                students = json.load(f)
        else:
            students = []

        students.append(data)

        with open(FILENAME, 'w') as f:
            json.dump(students, f, indent=4)

    except Exception as e:
        logging.error(f"Error saving student: {str(e)}")
        flash("Error saving student data!", "danger")


def load_students():
    try:
        if os.path.exists(FILENAME):
            with open(FILENAME, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        logging.error(f"Error loading students: {str(e)}")
        flash("Failed to load student list!", "danger")
        return []


def save_attendance(data):
    try:
        if os.path.exists(ATTENDANCE_FILE):
            with open(ATTENDANCE_FILE, 'r') as f:
                all_attendance = json.load(f)
        else:
            all_attendance = []

        all_attendance.append(data)

        with open(ATTENDANCE_FILE, 'w') as f:
            json.dump(all_attendance, f, indent=4)
    except Exception as e:
        logging.error(f"Error saving attendance: {str(e)}")
        flash("Error saving attendance!", "danger")


# ---------- Routes ----------
@app.route('/')
def home():
    return render_template("home.html")


@app.route('/registration', methods=["POST", "GET"])
def registration():
    form = Registration()
    if form.validate_on_submit():
        new_student = {
            "name": form.name.data,
            "roll_no": form.roll_no.data,
            "class": form.student_class.data
        }
        save_student(new_student)
        flash("Student registered successfully!", "success")
        return redirect(url_for('registration'))

    return render_template("registration.html", form=form)


@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    students = load_students()

    if request.method == 'POST':
        attendance_data = []

        try:
            for student in students:
                status_key = f'status_{student["roll_no"]}'
                status = request.form.get(status_key)

                attendance_data.append({
                    "name": student["name"],
                    "roll_no": student["roll_no"],
                    "class": student["class"],
                    "status": status
                })

            save_attendance(attendance_data)
            flash("Attendance Saved Successfully!", "success")
            return redirect(url_for('attendance'))

        except Exception as e:
            logging.error(f"Error processing attendance: {str(e)}")
            flash("Something went wrong while saving attendance!", "danger")

    return render_template("attendance.html", students=students)


@app.route('/attendance_record')
def attendance_record():
    try:
        if os.path.exists(ATTENDANCE_FILE):
            with open(ATTENDANCE_FILE, 'r') as f:
                attendance_data = json.load(f)
        else:
            attendance_data = []
    except Exception as e:
        logging.error(f"Error reading attendance record: {str(e)}")
        flash("Could not load attendance record!", "danger")
        attendance_data = []

    # ✅ Fetch the latest record (a list of student dicts)
    latest_record = attendance_data[-1] if attendance_data else []

    # ✅ Filter present and absent students
    present_students = [student for student in latest_record if student.get("status") == "Present"]
    absent_students = [student for student in latest_record if student.get("status") == "Absent"]

    return render_template("attendance_record.html", students=latest_record, present_students=present_students,
absent_students=absent_students)





@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    roll_no = request.form['roll_no']
    status = request.form['status']

    # Load students
    with open(ATTENDANCE_FILE, "r") as f:
        students = json.load(f)

    for student in students:
        if student['roll_no'] == roll_no:
            student['attendance'] = status
            break

    with open(ATTENDANCE_FILE, "w") as f:
        json.dump(students, f, indent=4)

    flash(f"Attendance marked {status} for Roll No {roll_no}", "success")
    return redirect(url_for("attendance_record"))

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")



if __name__ == '__main__':
    app.run(debug=True, port=8000)
