from django.urls import path
from core.admin_views import (
    admin_dashboard, manage_students,
    add_student, edit_student, delete_student,
    manage_courses, add_course, edit_course, delete_course,
    manage_faculty, add_faculty, edit_faculty, delete_faculty,
    manage_subjects, add_subject, edit_subject, delete_subject,
    manage_placements, add_placement, edit_placement, delete_placement, view_applicants,
    manage_notifications, add_notification, delete_notification,change_password_view
)

from core.faculty_views import (
    faculty_dashboard, faculty_subjects, take_attendance, view_attendance,
    faculty_attendance_subjects, faculty_attendance_summary,
    faculty_marks, upload_marks, view_marks,faculty_view_notifications,
    manage_faculty_notifications, send_notification_to_students, delete_faculty_notification,
    faculty_assignments, add_assignment, view_submissions,faculty_profile_view,
    course_materials,delete_material,edit_assignment,delete_assignment
)

from core.student_views import (
     student_dashboard_overview, student_manage_subjects_view, student_view_attendance, 
     student_view_marks, student_profile,list_placements_cards, placement_detail_view, apply_for_placement,
       my_applications,student_view_notifications,list_assignments,assignment_detail,student_view_materials

    
)

urlpatterns = [
    # admin urls start
    path('change-password/', change_password_view, name='change_password'),

    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/students/', manage_students, name='manage_students'),
    path('admin/students/add/', add_student, name='add_student'),
    path('admin/students/edit/<int:user_id>/', edit_student, name='edit_student'),
    path('admin/students/delete/<int:user_id>/', delete_student, name='delete_student'),

    path('admin/courses/', manage_courses, name='manage_courses'),
    path('admin/courses/add/', add_course, name='add_course'),
    path('admin/courses/edit/<int:course_id>/', edit_course, name='edit_course'),
    path('admin/courses/delete/<int:course_id>/', delete_course, name='delete_course'),

    path('admin/faculty/', manage_faculty, name='manage_faculty'),
    path('admin/faculty/add/', add_faculty, name='add_faculty'),
    path('admin/faculty/edit/<int:user_id>/', edit_faculty, name='edit_faculty'),
    path('admin/faculty/delete/<int:user_id>/', delete_faculty, name='delete_faculty'),

    path('admin/subjects/', manage_subjects, name='manage_subjects'),
    path('admin/subjects/add/', add_subject, name='add_subject'),
    path('admin/subjects/edit/<int:subject_id>/', edit_subject, name='edit_subject'),
    path('admin/subjects/delete/<int:subject_id>/', delete_subject, name='delete_subject'),

    path('admin/placements/', manage_placements, name='manage_placements'),
    path('admin/placements/add/', add_placement, name='add_placement'),
    path('admin/placements/edit/<int:placement_id>/', edit_placement, name='edit_placement'),
    path('admin/placements/delete/<int:placement_id>/', delete_placement, name='delete_placement'),
    path('admin/placements/applicants/<int:placement_id>/', view_applicants, name='view_applicants'),

    path('admin/notifications/', manage_notifications, name='manage_notifications'),
    path('admin/notifications/add/', add_notification, name='add_notification'),
    path('admin/notifications/delete/<int:notification_id>/', delete_notification, name='delete_notification'),
    # admin urls end

    # faculty urls start
    path('faculty/dashboard/', faculty_dashboard, name='faculty_dashboard'),
    path('faculty/subjects/', faculty_subjects, name='faculty_subjects'),
    path('faculty/attendance/take/<int:subject_id>/', take_attendance, name='take_attendance'),
    path('faculty/attendance/view/<int:subject_id>/', view_attendance, name='view_attendance'),
    path('faculty/attendance/report/', faculty_attendance_subjects, name='attendance_report'),
    path('faculty/attendance/report/<int:subject_id>/', faculty_attendance_summary, name='attendance_summary'),

    path('faculty/profile/', faculty_profile_view, name='faculty_profile'),

    path('faculty/marks/', faculty_marks, name='faculty_marks'),
    path('faculty/marks/upload/<int:subject_id>/', upload_marks, name='upload_marks'),
    path('faculty/marks/view/<int:subject_id>/', view_marks, name='view_marks'),

    path('faculty/manage-notifications/', manage_faculty_notifications, name='manage_faculty_notifications'),
    path('faculty/notifications/send/', send_notification_to_students, name='send_faculty_notification'),
    path('faculty/notifications/delete/<int:notification_id>/', delete_faculty_notification, name='delete_faculty_notification'),
    path('faculty/notifications/', faculty_view_notifications, name='faculty_notifications'),

    path('faculty/assignments/', faculty_assignments, name='faculty_assignments'),
    path('faculty/assignments/add/', add_assignment, name='add_assignment'),
    path('faculty/assignments/<int:assignment_id>/edit/', edit_assignment, name='edit_assignment'),
    path('faculty/assignments/<int:assignment_id>/delete/', delete_assignment, name='delete_assignment'),
    path('faculty/assignments/<int:assignment_id>/submissions/', view_submissions, name='view_submissions'),
    path('subjects/<int:subject_id>/materials/',course_materials, name='course_materials'),
    path('faculty/materials/<int:subject_id>/<int:material_id>/delete/', delete_material, name='delete_material'),
    # faculty urls end

    # student urls start
    path('student/dashboard/', student_dashboard_overview, name='student_dashboard'),
    path('student/subjects/', student_manage_subjects_view, name='student_subjects'),
    path('student/attendance/<int:subject_id>/', student_view_attendance, name='student_view_attendance'),
    path('student/marks/<int:subject_id>/', student_view_marks, name='student_view_marks'),

    path('student/profile/', student_profile, name='student_profile'),

    path('student/placements/', list_placements_cards, name='list_placements_cards'),
    path('student/placements/<int:placement_id>/', placement_detail_view, name='placement_detail_view'),
    path('student/placements/apply/<int:placement_id>/', apply_for_placement, name='apply_for_placement'),
    path('student/my-applications/', my_applications, name='my_applications'),

    path('student/notifications/', student_view_notifications, name='student_notifications'),

    path('student/assignments/', list_assignments, name='list_assignments'),
    path('student/assignments/<int:assignment_id>/', assignment_detail, name='assignment_detail'),
    path('materials/<int:subject_id>/',student_view_materials, name='student_view_materials'),


    # student urls end
]
