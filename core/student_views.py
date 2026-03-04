from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from core.models import Subject, AttendanceRecord, AttendanceSession, Marks
from users.models import CustomUser
from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import render, redirect
from django.contrib import messages
from core.models import StudentProfile,Placement,PlacementApplication,Notification,Assignment,AssignmentSubmission,CourseMaterial
from .forms import StudentProfileForm , PlacementApplicationForm,AssignmentForm,AssignmentSubmissionForm
from django.utils import timezone
from django.db.models import Count, Q
from django.http import HttpResponseForbidden
from django.db import models
@login_required
def student_profile(request):
    student = request.user.student_profile
    user = request.user

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            user.email = request.POST.get('email')  # update email from request
            user.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('student_profile')
        else:
            messages.error(request, "There was an error updating your profile.")
    else:
        form = StudentProfileForm(instance=student)

    return render(request, 'student/student_profile.html', {
        'title': 'My Profile',
        'form': form,
        'student': student,
        'user': user,
    })


@login_required
def student_dashboard_overview(request):
    student = request.user.student_profile
    subjects = Subject.objects.filter(course=student.course, semester=student.semester)
    total_subjects = subjects.count()

    total_sessions = 0
    present_sessions = 0

    for subject in subjects:
        sessions = AttendanceSession.objects.filter(subject=subject)
        total_sessions += sessions.count()
        for session in sessions:
            if AttendanceRecord.objects.filter(session=session, student=student, status='present').exists():
                present_sessions += 1

    overall_attendance_percent = (
        Decimal((present_sessions / total_sessions) * 100).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
        if total_sessions else 0
    )

    # ✅ FIX: Use Q from django.db.models, and correct field is recipient_role
    notifications = Notification.objects.filter(
        Q(recipient_role='student') | Q(recipient_role='all')
    ).order_by('-created_at')[:5]

    upcoming_assignments = Assignment.objects.filter(
        subject__in=subjects,
        deadline__gte=timezone.now()
    ).order_by('deadline')[:5]

    return render(request, 'student/student_dashboard.html', {
        'title': 'Dashboard',
        'student': student,
        'total_subjects': total_subjects,
        'overall_attendance_percent': overall_attendance_percent,
        'notifications': notifications,
        'upcoming_assignments': upcoming_assignments,
    })

@login_required
def student_manage_subjects_view(request):
    student = request.user.student_profile

    subjects = Subject.objects.filter(course=student.course, semester=student.semester).select_related('faculty')

    subject_data = []
    for subject in subjects:
        total_sessions = AttendanceSession.objects.filter(subject=subject).count()
        present_count = AttendanceRecord.objects.filter(
            session__subject=subject,
            student=student,
            status='present'
        ).count()

        attendance_percentage = round((present_count / total_sessions) * 100, 2) if total_sessions > 0 else 0

        subject_data.append({
            'subject': subject,
            'faculty_name': subject.faculty.get_full_name() if subject.faculty else 'N/A',
            'attendance_percent': attendance_percentage,
        })

    return render(request, 'student/student_subjects.html', {
        'title': 'My Subjects',
        'subject_data': subject_data
    })


@login_required
def student_view_attendance(request, subject_id):
    student = request.user.student_profile
    subject = get_object_or_404(Subject, id=subject_id, course=student.course, semester=student.semester)

    sessions = AttendanceSession.objects.filter(subject=subject).order_by('date')
    records = AttendanceRecord.objects.filter(session__in=sessions, student=student).select_related('session')

    total_classes = sessions.count()
    attended_classes = records.filter(status='present').count()
    percentage = round((attended_classes / total_classes) * 100, 2) if total_classes > 0 else 0

    return render(request, 'student/student_attendance.html', {
        'title': 'My Attendance',
        'subject': subject,
        'records': records,
        'total_classes': total_classes,
        'attended_classes': attended_classes,
        'percentage': percentage
    })


@login_required
def student_view_marks(request, subject_id):
    student = request.user.student_profile
    subject = get_object_or_404(Subject, id=subject_id, course=student.course, semester=student.semester)

    marks = Marks.objects.filter(student=student, subject=subject)

    return render(request, 'student/student_marks.html', {
        'title': 'My Marks',
        'subject': subject,
        'marks': marks
    })

@login_required
def list_placements_cards(request):
    student = request.user.student_profile
    student_course = student.course

    # Get all upcoming placements for the student's course
    placements = Placement.objects.filter(
        last_date_to_apply__gte=timezone.now().date(),
        eligible_courses=student_course
    ).order_by('-created_at').distinct()

    # Get IDs of placements the student has applied to
    applied_ids = set(
        PlacementApplication.objects.filter(student=student).values_list('placement_id', flat=True)
    )

    return render(request, 'student/placement_list.html', {
        'placements': placements,
        'applied_ids': applied_ids,
        'title': 'Placement Opportunities'
    })



@login_required
def placement_detail_view(request, placement_id):
    student = request.user.student_profile
    placement = get_object_or_404(Placement, id=placement_id)

    if student.course not in placement.eligible_courses.all():
        messages.warning(request, "You are not eligible for this placement.")
        return redirect('list_placements_cards')

    already_applied = PlacementApplication.objects.filter(student=student, placement=placement).exists()

    return render(request, 'student/placement_detail.html', {
        'placement': placement,
        'already_applied': already_applied,
        'title': f"{placement.title} at {placement.company}"
    })

@login_required
def apply_for_placement(request, placement_id):
    student = request.user.student_profile
    placement = get_object_or_404(Placement, id=placement_id)

    # Prevent duplicate application
    if PlacementApplication.objects.filter(student=student, placement=placement).exists():
        messages.warning(request, 'You have already applied for this opportunity.')
        return redirect('list_placements_cards')

    if request.method == 'POST':
        form = PlacementApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.student = student
            application.placement = placement
            application.save()
            messages.success(request, 'Application submitted successfully.')
            return redirect('list_placements_cards')
    else:
        form = PlacementApplicationForm()

    return render(request, 'student/apply_placement.html', {
        'form': form,
        'placement': placement,
        'title': 'Apply for Placement'
    })


@login_required
def my_applications(request):
    student = request.user.student_profile
    applications = PlacementApplication.objects.filter(student=student).select_related('placement').order_by('-applied_at')

    return render(request, 'student/my_applications.html', {
        'applications': applications,
        'title': 'My Applications'
    })


@login_required
def student_view_notifications(request):
    user = request.user
    role = user.role  # assuming this is 'student' or 'faculty'

    notifications = Notification.objects.filter(
        Q(recipient_role=role) | Q(recipient_role='all')
    ).order_by('-created_at')

    return render(request, 'student/notifications_list.html', {
        'notifications': notifications,
        'title': 'Notifications'
    })


@login_required
def list_assignments(request):
    student = request.user.student_profile
    subjects = student.course.subject_set.filter(semester=student.semester)
    assignments = Assignment.objects.filter(
        subject__in=subjects, deadline__gte=timezone.now()
    ).order_by('-created_at')

    submissions = AssignmentSubmission.objects.filter(student=student)
    submitted_ids = submissions.values_list('assignment_id', flat=True)

    return render(request, 'student/list_assignments.html', {
        'assignments': assignments,
        'submitted_ids': set(submitted_ids),
        'student': student,  # ✅ Pass student to template
        'title': 'Assignments',
    })

@login_required
def assignment_detail(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    student = request.user.student_profile
    submission = AssignmentSubmission.objects.filter(student=student, assignment=assignment).first()
    deadline_passed = timezone.now() > assignment.deadline

    if request.method == 'POST' and not submission and not deadline_passed:
        form = AssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            new_submission = form.save(commit=False)
            new_submission.assignment = assignment
            new_submission.student = student
            new_submission.save()
            messages.success(request, "Assignment submitted successfully.")
            return redirect('assignment_detail', assignment_id=assignment.id)
    else:
        form = AssignmentSubmissionForm()

    return render(request, 'student/assignment_detail.html', {
        'assignment': assignment,
        'submission': submission,
        'deadline_passed': deadline_passed,
        'form': form,
        'title': assignment.title
    })

@login_required
def student_view_materials(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    
    # Only show if student is assigned to this subject
    if request.user.role != 'student':
        return HttpResponseForbidden("You are not allowed to view these materials.")
    
    # Get materials related to the subject
    materials = CourseMaterial.objects.filter(subject=subject).order_by('-uploaded_at')

    return render(request, 'student/view_materials.html', {
        'subject': subject,
        'materials': materials
    })