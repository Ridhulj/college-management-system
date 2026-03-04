from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import CustomUser
from core.models import StudentProfile, Course, FacultyProfile, Subject,Placement, PlacementApplication,Notification,Assignment
from .forms import  StudentFullForm,CourseForm,FacultyFullForm,SubjectForm,PlacementForm,NotificationForm,CustomPasswordChangeForm
from django.utils.dateparse import parse_date
from datetime import datetime
from django.http import HttpResponse
import csv
from django.contrib.auth import update_session_auth_hash


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)  # Keep the user logged in
            messages.success(request, "Password changed successfully.")

            role = request.user.role
            if role == 'admin':
                return redirect('admin_dashboard')
            elif role == 'faculty':
                return redirect('faculty_dashboard')
            elif role == 'student':
                return redirect('student_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'partials/change_password.html', {
        'form': form,
        'title': 'Change Password',
    })

#################### student views starts

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return render(request, 'unauthorized.html')

    student_count = StudentProfile.objects.count()
    faculty_count = FacultyProfile.objects.count()
    course_count = Course.objects.count()
    subject_count = Subject.objects.count()
    placements_count = Placement.objects.count()
    notification_count = Notification.objects.count()

    recent_students = StudentProfile.objects.select_related('user').order_by('-id')[:5]
    recent_faculty = FacultyProfile.objects.select_related('user').order_by('-id')[:5]
    recent_notifications = Notification.objects.select_related('sender').order_by('-created_at')[:5]
    recent_placement_submissions = PlacementApplication.objects.select_related(
    'student__user', 'placement'
).order_by('-applied_at')[:5]

    stats_cards = [
        {"label": "Total Students", "count": student_count, "color": "primary", "icon": "user-graduate"},
        {"label": "Total Faculty", "count": faculty_count, "color": "success", "icon": "chalkboard-teacher"},
        {"label": "Total Courses", "count": course_count, "color": "info", "icon": "book"},
        {"label": "Total Subjects", "count": subject_count, "color": "warning", "icon": "book-reader"},
        {"label": "Total Placements", "count": placements_count, "color": "dark", "icon": "briefcase"},
        {"label": "Total Notifications", "count": notification_count, "color": "danger", "icon": "bell"},
    ]

    context = {
        'stats_cards': stats_cards,
        'recent_students': recent_students,
        'recent_faculty': recent_faculty,
        'recent_notifications': recent_notifications,
        'recent_placement_submissions': recent_placement_submissions,
    }
    return render(request, 'admin/admin_dashboard.html', context)

@login_required
def manage_students(request):
    if request.user.role != 'admin':
        return render(request, 'unauthorized.html')

    students = CustomUser.objects.filter(role='student').select_related('student_profile')

    # Optional: Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        students = students.filter(
            student_profile__date_added__date__range=[start_date, end_date]
        )

    context = {
        'students': students,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'admin/manage_students.html', context)


@login_required
def add_student(request):
    if request.user.role != 'admin':
        return render(request, 'unauthorized.html')

    if request.method == 'POST':
        form = StudentFullForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Student added successfully.")
            return redirect('manage_students')
    else:
        form = StudentFullForm()

    return render(request, 'admin/add_student.html', {'form': form})


@login_required
def edit_student(request, user_id):
    if request.user.role != 'admin':
        return render(request, 'unauthorized.html')

    # Get the CustomUser instance with role='student'
    user = get_object_or_404(CustomUser, id=user_id, role='student')

    # Ensure the student has a related profile
    profile = getattr(user, 'student_profile', None)
    if not profile:
        messages.error(request, "Student profile not found.")
        return redirect('manage_students')

    if request.method == 'POST':
        form = StudentFullForm(request.POST, instance=profile, user_instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Student updated successfully.")
            return redirect('manage_students')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StudentFullForm(instance=profile, user_instance=user)

    return render(request, 'admin/edit_student.html', {
        'form': form,
        'student': user
    })


@login_required
def delete_student(request, user_id):
    if request.user.role != 'admin':
        return render(request, 'unauthorized.html')

    user = get_object_or_404(CustomUser, id=user_id, role='student')
    user.delete()
    messages.success(request, "Student deleted successfully.")
    return redirect('manage_students')


#################### student views ends

#################### course views starts

@login_required
def manage_courses(request):
    if request.user.role != 'admin':
        return render(request, 'unauthorized.html')

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    courses = Course.objects.all()

    if start_date and end_date:
        courses = courses.filter(date_added__date__range=[start_date, end_date])

    return render(request, 'admin/manage_courses.html', {
        'courses': courses,
        'start_date': start_date,
        'end_date': end_date,
    })

@login_required
def add_course(request):
    if request.user.role != 'admin':
        return render(request, 'unauthorized.html')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course added successfully.')
            return redirect('manage_courses')
    else:
        form = CourseForm()

    return render(request, 'admin/add_course.html', {
        'form': form,
        'title': 'Add Course'
    })


@login_required
def edit_course(request, course_id):
    if request.user.role != 'admin':
        return render(request, 'unauthorized.html')

    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully.')
            return redirect('manage_courses')
    else:
        form = CourseForm(instance=course)

    return render(request, 'admin/edit_course.html', {
        'form': form,
        'title': 'Edit Course'
    })



@login_required
def delete_course(request, course_id):
    if request.user.role != 'admin':
        return render(request, 'unauthorized.html')

    course = get_object_or_404(Course, id=course_id)
    course.delete()
    messages.success(request, 'Course deleted successfully.')
    return redirect('manage_courses')

#################### course views ends

#################### faculty views starts

@login_required
def manage_faculty(request):
    if request.user.role != 'admin':
        return render(request, 'unauthorized.html')

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    faculty_list = CustomUser.objects.filter(role='faculty').select_related('faculty_profile')

    if start_date and end_date:
        faculty_list = faculty_list.filter(faculty_profile__date_added__date__range=[start_date, end_date])

    return render(request, 'admin/manage_faculty.html', {
        'faculty_list': faculty_list,
        'start_date': start_date,
        'end_date': end_date,
    })

@login_required
def add_faculty(request):
    if request.user.role != 'admin':
        return render(request, 'unauthorized.html')

    if request.method == 'POST':
        form = FacultyFullForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Faculty added successfully.")
            return redirect('manage_faculty')
    else:
        form = FacultyFullForm()

    return render(request, 'admin/add_faculty.html', {
        'form': form,
        'title': 'Add Faculty'
    })


@login_required
def edit_faculty(request, user_id):
    if request.user.role != 'admin':
        return render(request, 'unauthorized.html')

    user = get_object_or_404(CustomUser, id=user_id, role='faculty')
    profile = user.faculty_profile

    if request.method == 'POST':
        form = FacultyFullForm(request.POST, instance=user)
        form.fields['department'].initial = profile.department
        form.fields['phone'].initial = profile.phone

        if form.is_valid():
            form.save(user_instance=user)
            messages.success(request, "Faculty updated successfully.")
            return redirect('manage_faculty')
    else:
        form = FacultyFullForm(instance=user)
        form.fields['department'].initial = profile.department
        form.fields['phone'].initial = profile.phone

    return render(request, 'admin/edit_faculty.html', {
        'form': form,
        'title': 'Edit Faculty'
    })



@login_required
def delete_faculty(request, user_id):
    if request.user.role != 'admin':
        return render(request, 'unauthorized.html')

    user = get_object_or_404(CustomUser, id=user_id, role='faculty')
    user.delete()
    messages.success(request, "Faculty deleted successfully.")
    return redirect('manage_faculty')

#################### faculty views ends


#################### subject views starts

@login_required
def manage_subjects(request):
    if request.user.role != 'admin':
        return render(request, 'unauthorized.html')

    subjects = Subject.objects.all()
    return render(request, 'admin/manage_subjects.html', {'subjects': subjects})

@login_required
def add_subject(request):
    if request.user.role != 'admin':
        return render(request, 'unauthorized.html')

    form = SubjectForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Subject added successfully.")
        return redirect('manage_subjects')

    return render(request, 'admin/add_subject.html', {
        'form': form,
        'title': 'Add Subject'
    })

@login_required
def edit_subject(request, subject_id):
    if request.user.role != 'admin':
        return render(request, 'unauthorized.html')

    subject = get_object_or_404(Subject, id=subject_id)
    form = SubjectForm(request.POST or None, instance=subject)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Subject updated successfully.")
        return redirect('manage_subjects')

    return render(request, 'admin/edit_subject.html', {
        'form': form,
        'title': 'Edit Subject'
    })


@login_required
def delete_subject(request, subject_id):
    if request.user.role != 'admin':
        return render(request, 'unauthorized.html')

    subject = get_object_or_404(Subject, id=subject_id)
    subject.delete()
    messages.success(request, "Subject deleted successfully.")
    return redirect('manage_subjects')


#################### subject views ends


@login_required
def manage_placements(request):
    placements = Placement.objects.order_by('-created_at')
    return render(request, 'admin/placement_management.html', {
        'placements': placements,
        'title': 'Manage Placements'
    })

@login_required
def add_placement(request):
    if request.method == 'POST':
        form = PlacementForm(request.POST)
        if form.is_valid():
            placement = form.save(commit=False)
            placement.save()
            form.save_m2m()  # ✅ This line saves eligible_courses relationships
            messages.success(request, "Placement posted successfully.")
            return redirect('manage_placements')
    else:
        form = PlacementForm()

    return render(request, 'admin/add_edit_placement.html', {
        'form': form,
        'title': 'Add Placement',
        'button_label': 'Create'
    })


@login_required
def edit_placement(request, placement_id):
    placement = get_object_or_404(Placement, id=placement_id)

    if request.method == 'POST':
        form = PlacementForm(request.POST, instance=placement)
        if form.is_valid():
            placement = form.save(commit=False)
            placement.save()
            form.save_m2m()  # ✅ Important here too
            messages.success(request, "Placement updated successfully.")
            return redirect('manage_placements')
    else:
        form = PlacementForm(instance=placement)

    return render(request, 'admin/add_edit_placement.html', {
        'form': form,
        'title': 'Edit Placement',
        'button_label': 'Update'
    })

@login_required
def delete_placement(request, placement_id):
    placement = get_object_or_404(Placement, id=placement_id)
    placement.delete()
    messages.success(request, "Placement deleted.")
    return redirect('manage_placements')



@login_required
def view_applicants(request, placement_id):
    placement = get_object_or_404(Placement, id=placement_id)
    applications = PlacementApplication.objects.filter(
        placement=placement
    ).select_related('student__user', 'student__course')

    # CSV export
    if 'export' in request.GET and request.GET['export'] == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{placement.title}_applicants.csv"'

        writer = csv.writer(response)
        writer.writerow(['Name', 'Roll No', 'Email', 'Course', 'Semester', 'Applied On', 'Resume URL', 'Additional Info'])

        for app in applications:
            student = app.student
            writer.writerow([
                student.user.get_full_name(),
                student.roll_no,
                student.user.email,
                student.course.name,
                student.semester,
                app.applied_at.strftime('%Y-%m-%d %H:%M'),
                app.resume,
                app.additional_info or '-'
            ])
        return response

    return render(request, 'admin/view_applicants.html', {
        'placement': placement,
        'applications': applications,
        'title': f"Applicants for {placement.title}"
    })

@login_required
def manage_notifications(request):
    notifications = Notification.objects.order_by('-created_at')
    return render(request, 'admin/manage_notifications.html', {
        'notifications': notifications,
        'title': 'Manage Notifications'
    })


@login_required
def add_notification(request):
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            notification = form.save(commit=False)
            notification.sender = request.user
            notification.recipient_role = 'all'  # <-- Important line
            notification.save()
            messages.success(request, 'Notification sent to all users.')
            return redirect('manage_notifications')
    else:
        form = NotificationForm()

    return render(request, 'admin/add_notification.html', {
        'form': form,
        'title': 'Send Notification'
    })


@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    notification.delete()
    messages.success(request, 'Notification deleted successfully.')
    return redirect('manage_notifications')
