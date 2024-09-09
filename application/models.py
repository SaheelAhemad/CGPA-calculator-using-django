from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    usn = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100,default='')  # New field for user's name

    def __str__(self):  
        return self.user.username

class Student(models.Model):
    usn = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.usn})"

class Semester(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='semesters')
    number = models.IntegerField()
    sgpa = models.FloatField(default=0.0)

    def __str__(self):
        return f"Semester {self.number} for {self.student.usn}"

    def calculate_sgpa(self):
        marks = Mark.objects.filter(student=self.student, subject__semester=self)
        total_credits = sum(mark.subject.credits for mark in marks)
        total_grade_points = sum(mark.calculate_grade_point() * mark.subject.credits for mark in marks)
        if total_credits == 0:
            return 0
        return total_grade_points / total_credits

class Subject(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='subjects')
    subcode = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    credits = models.IntegerField()

    def __str__(self):
        return f"{self.name} ({self.subcode})"

class Mark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='marks')
    marks_obtained = models.FloatField()

    def __str__(self):
        return f"{self.student.usn} - {self.subject.subcode} - Semester {self.subject.semester.number}"

    def calculate_grade_point(self):
        if self.marks_obtained >= 90:
            return 10
        elif self.marks_obtained >= 80:
            return 9
        elif self.marks_obtained >= 70:
            return 8
        elif self.marks_obtained >= 60:
            return 7
        elif self.marks_obtained >= 50:
            return 6
        elif self.marks_obtained >= 40:
            return 5
        else:
            return 0