# College Management System

A comprehensive College Management System built with Django, designed to streamline administrative, academic, and student-related processes. The system provides role-based access for Administrators, Faculty, and Students, each with tailored dashboards and functionalities.

## 🚀 Features

### 👨‍💼 Administrator Portal
* **User Management**: Add, edit, and delete Student and Faculty profiles.
* **Academic Management**: Manage Courses and Subjects.
* **Placement Cell**: Add placement/internship opportunities, manage eligibility criteria, and track student applications.
* **Communication**: Broadcast notifications to Students, Faculty, or both.

### 👨‍🏫 Faculty Portal
* **Dashboard**: Overview of assigned subjects and quick actions.
* **Attendance Management**: Take and view student attendance with detailed summaries and reports.
* **Academic Performance**: Upload and view student marks for various exams (Test 1, Test 2, Model Exam, Final).
* **Course Materials**: Upload study materials and resources for students.
* **Assignments**: Create, manage, and review student assignment submissions.
* **Communication**: Send direct notifications to students of specific subjects.

### 👨‍🎓 Student Portal
* **Dashboard & Profile**: View personal details, enrolled course, and current semester.
* **Academic Tracking**: View attendance records and exam marks across subjects.
* **Assignments**: View pending assignments and submit completed work.
* **Course Materials**: Access and download study materials shared by faculty.
* **Placements**: Browse eligible placement/internship opportunities and apply directly using a resume link.
* **Notifications**: Receive important updates from faculty and administrators.

## 🛠️ Technology Stack
* **Backend Framework**: Django 5.2.1 (Python)
* **Database**: SQLite (Default)
* **Frontend**: HTML, CSS, JavaScript (Django Templates)
* **Authentication**: Django's built-in Auth system with a custom User model

## 📂 Project Structure
* `college_mgmt/` - Main project configuration (settings, core URLs, WSGI/ASGI).
* `core/` - Main application handling the logical flow (models, admin views, faculty views, student views).
* `users/` - Application handling custom user models, authentication, and roles (Admin, Faculty, Student).
* `templates/` - HTML templates structured by role (`admin/`, `faculty/`, `student/`).
* `static/` - Static assets including CSS, JavaScript, and images.
* `media/` - Uploaded files such as user assignments and course materials.

## ⚙️ Local Development Setup

### Prerequisites
* Python 3.8+
* Git

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone <your-github-repo-url>
   cd college_management
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (Admin account):**
   ```bash
   python manage.py createsuperuser
   ```
   > Follow the prompts to set up an admin username, email, and password.

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

7. **Access the application:**
   Open a web browser and navigate to `http://127.0.0.1:8000/`. You can log in using the superuser credentials you just created.

---

*This README was generated to reflect the current state of the College Management System.*
