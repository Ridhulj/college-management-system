from django.db import models
from users.models import CustomUser
from django.utils import timezone


class Course(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.code:
            last_course = Course.objects.order_by('-id').first()
            next_code = 101 if not last_course else int(last_course.code) + 1
            self.code = str(next_code)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.name}"


# Define common choices for semesters
SEMESTER_CHOICES = [
    (1, 'Semester 1'),
    (2, 'Semester 2'),
    (3, 'Semester 3'),
    (4, 'Semester 4'),
    (5, 'Semester 5'),
    (6, 'Semester 6'),
    (7, 'Semester 7'),
    (8, 'Semester 8'),
    (9, 'Semester 9'),
    (10, 'Semester 10'),
]

class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    roll_no = models.CharField(max_length=30, unique=True, blank=True)
    dob = models.DateField()
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.roll_no and self.course:
            course_code = self.course.code
            existing_rolls = StudentProfile.objects.filter(course=self.course).count()
            self.roll_no = f"{course_code}-{existing_rolls + 1}"
        super().save(*args, **kwargs)

    def __str__(self):
     return f"{self.roll_no} - {self.user.get_full_name()} - {self.course} - Sem {self.semester}"


class FacultyProfile(models.Model):
    DEPARTMENT_CHOICES = [
        ('CSE', 'Computer Science'),
        ('ECE', 'Electronics'),
        ('EEE', 'Electrical'),
        ('MECH', 'Mechanical'),
        ('CIVIL', 'Civil'),
        ('MATHS', 'Mathematics'),
        ('PHY', 'Physics'),
        ('CHEM', 'Chemistry'),
        ('ENG', 'English'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='faculty_profile')
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.department}"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)  # changed from year to semester
    faculty = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'faculty'})

    def __str__(self):
        return f"{self.name} - {self.course.name} - Sem {self.semester}"
########################################################################


class AttendanceSession(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    faculty = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'faculty'})
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subject', 'date')  # Prevent duplicate entries for same subject-date

    def __str__(self):
        return f"{self.subject.name} - {self.date}"
    
class AttendanceRecord(models.Model):
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('present', 'Present'), ('absent', 'Absent')])

    class Meta:
        unique_together = ('session', 'student')  # One record per student per session

    def __str__(self):
        return f"{self.student.roll_no} - {self.session.subject.name} - {self.status}"


# models.py
class Marks(models.Model):
    EXAM_TYPE_CHOICES = [
        ('test1', 'Test 1'),
        ('test2', 'Test 2'),
        ('model_exam', 'Model Exam'),
        ('final_exam', 'Final Exam'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    max_marks = models.DecimalField(max_digits=5, decimal_places=2)
    date_recorded = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'subject', 'exam_type')

    def __str__(self):
        return f"{self.student.roll_no} - {self.subject.name} - {self.exam_type}"

    @property
    def grade(self):
        if not self.max_marks:
            return "-"
        
        percentage = (self.marks_obtained / self.max_marks) * 100

        if percentage >= 90:
            return 'A+'
        elif percentage >= 80:
            return 'A'
        elif percentage >= 70:
            return 'B'
        elif percentage >= 60:
            return 'C'
        elif percentage >= 50:
            return 'D'
        else:
            return 'F'


class Placement(models.Model):
    PLACEMENT_TYPE_CHOICES = [
        ('placement', 'Placement'),
        ('internship', 'Internship'),
    ]

    title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=PLACEMENT_TYPE_CHOICES, default='placement')
    description = models.TextField()
    skills_required = models.TextField(help_text="Comma-separated skills")
    eligibility = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    last_date_to_apply = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ New field: Select multiple courses eligible to apply
    eligible_courses = models.ManyToManyField('Course', related_name='eligible_placements')

    def __str__(self):
        return f"{self.title} at {self.company}"


class PlacementApplication(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    placement = models.ForeignKey(Placement, on_delete=models.CASCADE, related_name='applications')
    resume = models.URLField(help_text="Enter a link to your resume")
    additional_info = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'placement')

    def __str__(self):
        return f"{self.student.roll_no} applied for {self.placement.title}"
    

class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    sender = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    recipient_role = models.CharField(max_length=20, choices=[('student', 'Student'), ('faculty', 'Faculty'), ('all', 'All')])
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)  # New field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.recipient_role}"


class Assignment(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    faculty = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'faculty'})
    title = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        return self.deadline >= timezone.now()

    def __str__(self):
        return f"{self.title} - {self.subject.name}"

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    file = models.FileField(upload_to='assignments/')
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"{self.student.roll_no} - {self.assignment.title}"
    

class CourseMaterial(models.Model):
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='course_materials/')
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'faculty'})
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title