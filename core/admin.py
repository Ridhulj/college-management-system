from django.contrib import admin
from .models import Course, StudentProfile, Subject, FacultyProfile, AttendanceRecord, AttendanceSession, PlacementApplication, Placement,CourseMaterial

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['name', 'code']

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['roll_no', 'user', 'course', 'semester']
    search_fields = ['roll_no', 'user__username', 'course__name']
    list_filter = ['course', 'semester']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'semester', 'faculty')
    list_filter = ('course', 'semester')
    search_fields = ('name', 'course__name', 'faculty__first_name', 'faculty__last_name')

admin.site.register(FacultyProfile)

@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ('subject', 'faculty', 'date', 'created_at')
    list_filter = ('subject', 'faculty', 'date')
    search_fields = ('subject__name', 'faculty__username')

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('session', 'student', 'status')
    list_filter = ('status', 'session__subject__name')
    search_fields = ('student__user__username', 'student__roll_no')

@admin.register(Placement)
class PlacementAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'position', 'type', 'last_date_to_apply', 'created_at')
    search_fields = ('title', 'company', 'skills_required')
    list_filter = ('type', 'company', 'last_date_to_apply')

@admin.register(PlacementApplication)
class PlacementApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'placement', 'applied_at')
    search_fields = ('student__roll_no', 'placement__title')
    list_filter = ('applied_at',)

@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'uploaded_by', 'uploaded_at')
    list_filter = ('subject', 'uploaded_by', 'uploaded_at')
    search_fields = ('title', 'subject__name', 'uploaded_by__username')