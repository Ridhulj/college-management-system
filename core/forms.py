from django import forms
from users.models import CustomUser
from .models import StudentProfile, Course, FacultyProfile, Subject, SEMESTER_CHOICES, AttendanceRecord,Placement, PlacementApplication,Notification,Assignment,AssignmentSubmission,CourseMaterial
from django import forms
from django.contrib.auth import authenticate
from django.utils import timezone

class CustomPasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Old password is incorrect.")
        return old_password

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if not password.isalnum():
            raise forms.ValidationError("Password must be alphanumeric.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("New passwords do not match.")
        return cleaned_data

class StudentFullForm(forms.ModelForm):
    first_name = forms.CharField(label="First Name")
    last_name = forms.CharField(label="Last Name")
    username = forms.CharField(label="Username")
    email = forms.EmailField(label="Email")
    semester = forms.ChoiceField(choices=SEMESTER_CHOICES, label="Semester")

    class Meta:
        model = StudentProfile
        fields = ['dob', 'course', 'semester', 'phone']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)

        if self.user_instance:
            self.fields['first_name'].initial = self.user_instance.first_name
            self.fields['last_name'].initial = self.user_instance.last_name
            self.fields['username'].initial = self.user_instance.username
            self.fields['email'].initial = self.user_instance.email

        field_order = ['first_name', 'last_name', 'username', 'email', 'dob', 'course', 'semester', 'phone']
        self.order_fields(field_order)

    def clean_username(self):
        username = self.cleaned_data['username']
        qs = CustomUser.objects.filter(username=username)

        if self.user_instance:
            qs = qs.exclude(id=self.user_instance.id)

        if qs.exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def save(self, commit=True):
        user = self.user_instance or CustomUser()
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.role = 'student'

        if not self.user_instance:
            user.set_password('12345678')  # default password

        if commit:
            user.save()

        profile = super().save(commit=False)
        profile.user = user

        if not profile.roll_no and profile.course:
            count = StudentProfile.objects.filter(course=profile.course).count() + 1
            profile.roll_no = f"{profile.course.name}-{count}"

        if commit:
            profile.save()

        return profile



class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name']


class FacultyFullForm(forms.ModelForm):
    department = forms.ChoiceField(choices=FacultyProfile.DEPARTMENT_CHOICES, label="Department")
    phone = forms.CharField(max_length=15, label="Phone Number")

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email']

    def save(self, commit=True, user_instance=None):
        user = user_instance if user_instance else super().save(commit=False)
        user.role = 'faculty'
        if not user_instance:
            user.set_password('12345678')  # default password

        if commit:
            user.save()

            profile, _ = FacultyProfile.objects.get_or_create(user=user)
            profile.department = self.cleaned_data['department']
            profile.phone = self.cleaned_data['phone']
            profile.save()

        return user


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'course', 'semester', 'faculty']


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['phone']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

class FacultyProfileForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = FacultyProfile
        fields = ['phone']

        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['email'].initial = user.email
            self.user = user

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            self.user.email = self.cleaned_data['email']
            self.user.save()
        return profile



class PlacementForm(forms.ModelForm):
    eligible_courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Eligible Courses"
    )

    class Meta:
        model = Placement
        fields = [
            'title',
            'company',
            'position',
            'type',
            'description',
            'skills_required',
            'eligibility',
            'location',
            'last_date_to_apply',
            'eligible_courses',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'skills_required': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'eligibility': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'last_date_to_apply': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': timezone.now().date().isoformat()
            }),
        }

    def clean_last_date_to_apply(self):
        date = self.cleaned_data['last_date_to_apply']
        if date < timezone.now().date():
            raise forms.ValidationError("Deadline must be a future date.")
        return date
    
class PlacementApplicationForm(forms.ModelForm):
    class Meta:
        model = PlacementApplication
        fields = ['resume', 'additional_info']
        widgets = {
            'resume': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the URL to your resume (Google Drive)'
            }),
            'additional_info': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Any additional information you want to include...'
            }),
        }
        labels = {
            'resume': 'Resume URL',
            'additional_info': 'Additional Information (optional)'
        }

    def clean_resume(self):
        url = self.cleaned_data['resume'].strip()
        if "drive.google.com/file/d/" in url:
            try:
                file_id = url.split("/d/")[1].split("/")[0]
                return f"https://drive.google.com/uc?export=view&id={file_id}"
            except IndexError:
                raise forms.ValidationError("Invalid Google Drive URL format.")
        return url
    
class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['title', 'message']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter title'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Enter message'
            }),
        }


class FacultyNotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['subject', 'title', 'message']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Enter message'}),
        }

    def __init__(self, *args, **kwargs):
        faculty = kwargs.pop('faculty', None)
        super().__init__(*args, **kwargs)

        if faculty:
            self.fields['subject'] = forms.ModelChoiceField(
                queryset=Subject.objects.filter(faculty=faculty),
                widget=forms.Select(attrs={'class': 'form-control'}),
                required=True,
                label='Subject'
            )

class AssignmentForm(forms.ModelForm):
    deadline = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': timezone.now().date().isoformat()  # ✅ disables past dates
        })
    )

    class Meta:
        model = Assignment
        fields = ['subject', 'title', 'description', 'deadline']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter assignment title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter description'}),
        }
        labels = {
            'subject': 'Subject',
            'title': 'Assignment Title',
            'description': 'Assignment Description',
            'deadline': 'Submission Deadline',
        }

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        today = timezone.now().date()
        if deadline < today:
            raise forms.ValidationError("Deadline cannot be in the past.")
        return deadline
    
class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'file': 'Upload Assignment File'
        }

class CourseMaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ['title', 'file']