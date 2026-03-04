from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import AttendanceRecord,Subject,StudentProfile, AttendanceSession, Course, Subject,Marks,Notification,Assignment,AssignmentSubmission,CourseMaterial
from datetime import date
from django.utils.dateparse import parse_date
from django.db.models import Count, Q
from datetime import datetime
from core.forms import FacultyNotificationForm,AssignmentForm,FacultyProfileForm,CourseMaterialForm
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from django.utils import timezone
CustomUser = get_user_model()


@login_required
def faculty_dashboard(request):
    if request.user.role != 'faculty':
        return render(request, 'unauthorized.html')

    subjects = Subject.objects.filter(faculty=request.user).select_related('course')

    # Assignments count per subject
    assignment_counts = {
        subject: Assignment.objects.filter(subject=subject).count()
        for subject in subjects
    }

    # Recent materials uploaded by faculty
    recent_materials = CourseMaterial.objects.filter(subject__in=subjects).order_by('-uploaded_at')[:5]



    # Attendance summary per subject
    attendance_summary = {}
    for subject in subjects:
        sessions = AttendanceSession.objects.filter(subject=subject)
        total_sessions = sessions.count()
        if total_sessions:
            total_records = AttendanceRecord.objects.filter(session__in=sessions, status=True).count()
            total_students = AttendanceRecord.objects.filter(session__in=sessions).values('student').distinct().count()
            avg_attendance = round((total_records / (total_sessions * total_students)) * 100, 2) if total_students else 0
        else:
            avg_attendance = 0
        attendance_summary[subject] = {
            'total_sessions': total_sessions,
            'avg_attendance': avg_attendance
        }

    # Upcoming deadlines
    upcoming_deadlines = Assignment.objects.filter(subject__in=subjects, deadline__gte=timezone.now()).order_by('deadline')[:5]

    # Recent notifications
    notifications = Notification.objects.filter(sender=request.user).order_by('-created_at')[:5]

    return render(request, 'faculty/faculty_dashboard.html', {
        'subjects': subjects,
        'assignment_counts': assignment_counts,
        'recent_materials': recent_materials,
        'attendance_summary': attendance_summary,
        'upcoming_deadlines': upcoming_deadlines,
        'notifications': notifications,
    })
@login_required
def faculty_profile_view(request):
    profile = request.user.faculty_profile

    if request.method == 'POST':
        form = FacultyProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('faculty_profile')
    else:
        form = FacultyProfileForm(instance=profile, user=request.user)

    return render(request, 'faculty/faculty_profile.html', {
        'form': form,
        'title': 'My Profile'
    })



@login_required
def faculty_subjects(request):
    if request.user.role != 'faculty':
        return render(request, 'unauthorized.html')

    subjects = Subject.objects.filter(faculty=request.user).select_related('course')

    return render(request, 'faculty/faculty_subjects.html', {
        'subjects': subjects
    })

@login_required
def take_attendance(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id, faculty=request.user)
    students = StudentProfile.objects.filter(course=subject.course, semester=subject.semester)

    if request.method == 'POST':
        selected_date = request.POST.get('attendance_date')
        if not selected_date:
            messages.error(request, 'Please select a date.')
            return redirect('take_attendance', subject_id=subject.id)

        present_student_ids = request.POST.getlist("present_students")

        session, _ = AttendanceSession.objects.get_or_create(
            subject=subject,
            date=selected_date,
            faculty=request.user
        )

        for student in students:
            status = 'present' if str(student.id) in present_student_ids else 'absent'
            AttendanceRecord.objects.update_or_create(
                session=session,
                student=student,
                defaults={'status': status}
            )

        messages.success(request, 'Attendance recorded successfully.')
        return redirect('faculty_subjects')
    return render(request, 'faculty/take_attendance.html', {
        'students': students,
        'subject': subject,
        'today': date.today(),
        'title': 'Take Attendance'
    })

@login_required
def view_attendance(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id, faculty=request.user)

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    sessions = AttendanceSession.objects.filter(subject=subject)
    if start_date:
        sessions = sessions.filter(date__gte=start_date)
    if end_date:
        sessions = sessions.filter(date__lte=end_date)
    sessions = sessions.order_by('-date')

    records = AttendanceRecord.objects.filter(session__in=sessions).select_related('student', 'student__user', 'session')

    return render(request, 'faculty/view_attendance.html', {
        'subject': subject,
        'records': records,
        'start_date': start_date,
        'end_date': end_date,
        'title': 'View Attendance'
    })

@login_required
def faculty_attendance_subjects(request):
    subjects = Subject.objects.filter(faculty=request.user)
    return render(request, 'faculty/attendance_subjects.html', {
        'subjects': subjects,
        'title': 'Attendance Report'
    })


@login_required
def faculty_attendance_summary(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id, faculty=request.user)
    students = StudentProfile.objects.filter(course=subject.course, semester=subject.semester)

    # Total sessions held
    total_sessions = AttendanceSession.objects.filter(subject=subject).count()

    summary = []

    for student in students:
        attended_count = AttendanceRecord.objects.filter(
            session__subject=subject,
            student=student,
            status='present'
        ).count()

        percent = (attended_count / total_sessions) * 100 if total_sessions > 0 else 0

        summary.append({
            'student': student,
            'attended': attended_count,
            'total': total_sessions,
            'percent': round(percent, 2)
        })

    return render(request, 'faculty/attendance_summary.html', {
        'subject': subject,
        'summary': summary,
        'title': f'{subject.name} - Attendance Summary'
    })

@login_required
def faculty_marks(request):
    if request.user.role != 'faculty':
        return render(request, 'unauthorized.html')

    subjects = Subject.objects.filter(faculty=request.user)

    return render(request, 'faculty/manage_marks.html', {
        'subjects': subjects,
        'title': 'Manage Marks'
    })

@login_required
def upload_marks(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id, faculty=request.user)
    students = StudentProfile.objects.filter(course=subject.course, semester=subject.semester)

    if request.method == 'POST':
        exam_type = request.POST.get('exam_type')
        max_marks_input = request.POST.get('max_marks')

        if not exam_type or not max_marks_input:
            messages.error(request, "Please fill in all required fields.")
            return redirect('upload_marks', subject_id=subject_id)

        try:
            max_marks = float(max_marks_input)
            if max_marks <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Maximum marks must be a positive number.")
            return redirect('upload_marks', subject_id=subject_id)

        for student in students:
            mark_input = request.POST.get(f'marks_{student.id}')
            if mark_input:
                try:
                    marks_obtained = float(mark_input)
                    if marks_obtained < 0:
                        raise ValueError
                    if marks_obtained > max_marks:
                        messages.error(request, f"{student.user.get_full_name()}: Marks cannot exceed maximum {max_marks}.")
                        return redirect('upload_marks', subject_id=subject_id)

                    Marks.objects.update_or_create(
                        student=student,
                        subject=subject,
                        exam_type=exam_type,
                        defaults={'marks_obtained': marks_obtained, 'max_marks': max_marks}
                    )
                except ValueError:
                    messages.error(request, f"Invalid marks input for {student.user.get_full_name()}.")
                    return redirect('upload_marks', subject_id=subject_id)

        messages.success(request, "Marks uploaded successfully.")
        return redirect('faculty_marks')

    return render(request, 'faculty/upload_marks.html', {
        'subject': subject,
        'students': students,
        'exam_choices': Marks.EXAM_TYPE_CHOICES,
        'title': 'Upload Marks'
    })


@login_required
def view_marks(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id, faculty=request.user)

    # Filters from GET
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    exam_type = request.GET.get('exam_type')

    marks = Marks.objects.filter(subject=subject).select_related('student__user')

    # Apply filters
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            marks = marks.filter(date_recorded__gte=start)
        except ValueError:
            pass

    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            marks = marks.filter(date_recorded__lte=end)
        except ValueError:
            pass

    if exam_type:
        marks = marks.filter(exam_type=exam_type)

    exam_type_choices = dict(Marks.EXAM_TYPE_CHOICES)

    return render(request, 'faculty/view_marks.html', {
        'subject': subject,
        'marks': marks,
        'title': 'View Marks',
        'start_date': start_date,
        'end_date': end_date,
        'exam_type': exam_type,
        'exam_type_choices': exam_type_choices,
    })

@login_required
def faculty_view_notifications(request):
    user = request.user
    role = user.role  # assuming this is 'student' or 'faculty'

    notifications = Notification.objects.filter(
        Q(recipient_role=role) | Q(recipient_role='all')
    ).order_by('-created_at')

    return render(request, 'faculty/notifications_list.html', {
        'notifications': notifications,
        'title': 'Notifications'
    })

@login_required
def manage_faculty_notifications(request):
    """List of notifications sent by the faculty."""
    notifications = Notification.objects.filter(sender=request.user).order_by('-created_at')
    return render(request, 'faculty/manage_notifications.html', {
        'notifications': notifications,
        'title': 'My Notifications'
    })

@login_required
def send_notification_to_students(request):
    """Send notification to students of a subject the faculty teaches."""
    if request.method == 'POST':
        form = FacultyNotificationForm(request.POST, faculty=request.user)
        if form.is_valid():
            notification = form.save(commit=False)
            notification.sender = request.user
            notification.recipient_role = 'student'
            notification.save()
            messages.success(request, "Notification sent successfully.")
            return redirect('manage_faculty_notifications')
    else:
        form = FacultyNotificationForm(faculty=request.user)

    return render(request, 'faculty/send_notifications.html', {
        'form': form,
        'title': 'Send Notification to Students'
    })

@login_required
def delete_faculty_notification(request, notification_id):
    """Delete a notification sent by the faculty."""
    notification = get_object_or_404(Notification, id=notification_id, sender=request.user)
    notification.delete()
    messages.success(request, "Notification deleted.")
    return redirect('faculty_notifications')



@login_required
def faculty_assignments(request):
    assignments = Assignment.objects.filter(faculty=request.user).order_by('-created_at')
    return render(request, 'faculty/manage_assignments.html', {
        'assignments': assignments,
        'title': 'My Assignments'
    })


@login_required
def add_assignment(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        form.fields['subject'].queryset = Subject.objects.filter(faculty=request.user)

        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.faculty = request.user
            assignment.save()
            messages.success(request, 'Assignment created successfully.')
            return redirect('faculty_assignments')
    else:
        form = AssignmentForm()
        form.fields['subject'].queryset = Subject.objects.filter(faculty=request.user)

    return render(request, 'faculty/add_assignments.html', {
        'form': form,
        'title': 'Add Assignment'
    })

@login_required
def edit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, faculty=request.user)

    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment)
        form.fields['subject'].queryset = Subject.objects.filter(faculty=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment updated successfully.')
            return redirect('faculty_assignments')
    else:
        form = AssignmentForm(instance=assignment)
        form.fields['subject'].queryset = Subject.objects.filter(faculty=request.user)

    return render(request, 'faculty/add_assignments.html', {
        'form': form,
        'title': 'Edit Assignment',
        'button_label': 'Update'
    })


@login_required
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, faculty=request.user)
    assignment.delete()
    messages.success(request, 'Assignment deleted successfully.')
    return redirect('faculty_assignments')


@login_required
def view_submissions(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, faculty=request.user)
    submissions = AssignmentSubmission.objects.filter(assignment=assignment).select_related('student', 'student__user')

    return render(request, 'faculty/view_submissions.html', {
        'assignment': assignment,
        'submissions': submissions,
        'title': f"Submissions - {assignment.title}"
    })

@login_required
def course_materials(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    materials = CourseMaterial.objects.filter(subject=subject)

    if request.method == 'POST':
        form = CourseMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.subject = subject
            material.uploaded_by = request.user  # ✅ Important
            material.save()
            messages.success(request, "Material uploaded successfully.")  # ✅ Optional
            return redirect('course_materials', subject_id=subject.id)
    else:
        form = CourseMaterialForm()

    return render(request, 'faculty/course_materials.html', {
        'subject': subject,
        'materials': materials,
        'form': form
    })


@login_required
def delete_material(request, subject_id, material_id):
    material = get_object_or_404(CourseMaterial, id=material_id, subject_id=subject_id)

    # Only allow the uploader (faculty) to delete
    if request.user != material.uploaded_by:
        return HttpResponseForbidden("You don't have permission to delete this file.")

    material.file.delete()
    material.delete()

    messages.success(request, "Course material deleted successfully.")
    return redirect('course_materials', subject_id=subject_id)