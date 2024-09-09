from django.contrib import admin
from .models import Subject, Student, Semester, Mark

# Register your models here.
class MarksAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'marks_obtained')

class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subcode', 'name', 'credits')

class StudentAdmin(admin.ModelAdmin):
    list_display = ('usn', 'name')

class SemesterAdmin(admin.ModelAdmin):
    list_display = ('student', 'number', 'sgpa')

admin.site.register(Subject, SubjectAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Mark, MarksAdmin)
admin.site.register(Semester, SemesterAdmin)