from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import Subject, Student, Mark, Semester, UserProfile
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User

@csrf_exempt
def get_data(request):
    if request.method == 'POST':
        semester_number = request.POST.get('semester_number')
        if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
            user_profile = request.user.userprofile 
            usn = user_profile.usn
            student = get_object_or_404(Student, usn=usn)
            semester = get_object_or_404(Semester, student=student, number=semester_number)

            subjects = Subject.objects.filter(semester=semester)
            marks_data = {subject.subcode: request.POST.get(subject.subcode) for subject in subjects}
            print(marks_data)

            for subcode, marks in marks_data.items():
                if marks is not None and marks.strip():  # Ensure marks is not None or empty
                    subject = get_object_or_404(Subject, subcode=subcode, semester=semester)
                    Mark.objects.update_or_create(
                        student=student,
                        subject=subject,
                        defaults={'marks_obtained': int(marks)}
                    )

            semester.sgpa = semester.calculate_sgpa()
            semester.save()

            messages.success(request, 'Marks data updated successfully.')
            return redirect(f'/display_results/?semester_number={semester_number}')
        else:
            messages.error(request, 'User is not authenticated or does not have a profile.')
            return redirect('login')
    else:
        subjects = Subject.objects.filter(semester__number=request.GET.get('semester_number'))
        context = {
            'subjects'  : subjects,
            'semester_number': request.GET.get('semester_number')
        }
        return render(request, 'form.html', context)

# def get_data(request):
#     if request.method == 'POST':
#         if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
#             user_profile = request.user.userprofile
#             usn = user_profile.usn
#             student = get_object_or_404(Student, usn=usn)
#             semester = get_object_or_404(Semester, student=student, number=5)  # Adjust semester number accordingly

#             marks_data = {
#                 '21CS51': request.POST.get('21CS51'),
#                 '21CS52': request.POST.get('21CS52'),
#                 '21CS53': request.POST.get('21CS53'),
#                 '21CS54': request.POST.get('21CS54'),
#                 '21CSL55': request.POST.get('21CSL55'),
#                 '21RMI56': request.POST.get('21RMI56'),
#                 '21CIV57': request.POST.get('21CIV57'),
#                 '21CS58x': request.POST.get('21CS58x')
#             }

#             for subcode, marks in marks_data.items():
#                 if marks is not None and marks.strip():  # Ensure marks is not None or empty
#                     subject = get_object_or_404(Subject, subcode=subcode, semester=semester)
#                     mark_obj, created = Mark.objects.update_or_create(
#                         student=student,
#                         subject=subject,
#                         defaults={'marks_obtained': int(marks)}
#                     )

#             # Recalculate and save SGPA
#             semester.sgpa = semester.calculate_sgpa()
#             semester.save()

#             messages.success(request, 'Marks data updated successfully.')
#             return redirect('display_results')
#         else:
#             messages.error(request, 'User is not authenticated or does not have a profile.')
#             return redirect('login')

#     return render(request, 'form.html') 

def display_results(request):
    if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
        semester_number = request.GET.get('semester_number')
        user_profile = request.user.userprofile
        usn = user_profile.usn
        student = get_object_or_404(Student, usn=usn)
        semester = get_object_or_404(Semester, student=student, number=semester_number)  # Adjust semester number accordingly

        enrollments = Mark.objects.filter(student=student, subject__semester=semester)
        data = {
            enrollment.subject.subcode: {
                'name': enrollment.subject.name,
                'marks_obtained': enrollment.marks_obtained,
                'grade_points': enrollment.calculate_grade_point(),
                'credits': enrollment.subject.credits,
                'resultant_grade': enrollment.calculate_grade_point() * enrollment.subject.credits
            } for enrollment in enrollments
        }

        context = {
            "data": data, 
            "sgpa": semester.sgpa,
            "student": student,
            "semester": semester
        }

        return render(request, "content.html", context)
    else:
        messages.error(request, 'User is not authenticated or does not have a profile.')
        return redirect('login')

def register_view(request):
    if request.method == 'POST':
        usn = request.POST.get('usn')
        name = request.POST.get('name')  # New field for name
        password = request.POST.get('password')
        if User.objects.filter(username=usn).exists():
            messages.error(request, 'USN already exists.')
        else:
            # Create User
            user = User.objects.create_user(username=usn, password=password)
            # Create UserProfile
            profile = UserProfile(user=user, usn=usn, name=name)
            profile.save()
            # Create Student
            student = Student(usn=usn, name=name)
            student.save()
            for semester_number in range(1, 9):  # Assuming 8 semesters
                semester = Semester.objects.create(student=student, number=semester_number)
                # Create Subjects for each semester (example subjects for semester 5)
                if semester_number == 1:
                    subjects = [
                        {'subcode': '21MAT11', 'name': 'Calculus & Differential Equations', 'credits': 3},
                        {'subcode': '21PHYx2', 'name': 'Engineering Physics', 'credits': 3},
                        {'subcode': '21ELEx3', 'name': 'Basic Electrical Engineering', 'credits': 3},
                        {'subcode': '21CIVx4', 'name': 'Elements of Civil Engineering and Mechanics', 'credits': 3},
                        {'subcode': '21EVNLx5', 'name': 'Engineering Visualization', 'credits': 3},
                        {'subcode': '21PHYLx6', 'name': 'Engineering Physics Laboratory', 'credits': 1},
                        {'subcode': '21ELEx7', 'name': 'Basic Electrical Engineering Laboratory', 'credits': 1},
                        {'subcode': '21EGH18', 'name': 'Communicative English', 'credits': 1},
                        {'subcode': '21IDT19 OR 21SFH19', 'name': 'Innovation and Design Thinking OR Scientific Foundations of Health', 'credits': 1},
                    ]

                    for subject_data in subjects:
                        subject, created = Subject.objects.get_or_create(
                            subcode=subject_data['subcode'],
                            defaults={'name': subject_data['name'], 'credits': subject_data['credits']}
                        )
                        semester.subjects.add(subject)
                        
                    # for subject_data in subjects:
                    #     Subject.objects.get_or_create(semester=semester, **subject_data)
                if semester_number == 2:
                    subjects = [
                        {'subcode': '21MAT21', 'name': 'Advanced Calculus and Numerical Methods', 'credits': 3},
                        {'subcode': '21CHEx2', 'name': 'Engineering Chemistry', 'credits': 3},
                        {'subcode': '21PSPx3', 'name': 'Problem-Solving through Programming', 'credits': 3},
                        {'subcode': '21ELNx4', 'name': 'Basic Electronics & Communication Engineering', 'credits': 3},
                        {'subcode': '21EMEx5', 'name': 'Elements of Mechanical Engineering', 'credits': 3},
                        {'subcode': '21CHELx6', 'name': 'Engineering Chemistry Laboratory', 'credits': 1},
                        {'subcode': '21CPLx7', 'name': 'Computer Programming Laboratory', 'credits': 1},
                        {'subcode': '21EGH28', 'name': 'Communicative English', 'credits': 2},
                        {'subcode': '21IDT29 OR 21SFH29', 'name': 'Innovation and Design Thinking OR Scientific Foundations of Health', 'credits': 1},
                    ]

                    for subject_data in subjects:
                        subject, created = Subject.objects.get_or_create(
                            subcode=subject_data['subcode'],
                            defaults={'name': subject_data['name'], 'credits': subject_data['credits']}
                        )
                        semester.subjects.add(subject)
                        
                    # for subject_data in subjects:
                    #     Subject.objects.get_or_create(semester=semester, **subject_data)
                if semester_number == 3:
                    subjects = [
                        {'subcode': '21MAT31', 'name': 'Transform Calculus, Fourier Series and Numerical Techniques', 'credits': 3},
                        {'subcode': '21CS32', 'name': 'Data Structures and Applications', 'credits': 4},
                        {'subcode': '21CS33', 'name': 'Analog and Digital Electronics', 'credits': 4},
                        {'subcode': '21CS34', 'name': 'Computer Organization and Architecture', 'credits': 3},
                        {'subcode': '21CSL35', 'name': 'Object Oriented Programming with JAVA Laboratory', 'credits': 1},
                        {'subcode': '21SCR36', 'name': 'Social Connect and Responsibility', 'credits': 1},
                        {'subcode': '21KSK37 OR 21KBK37 OR 21CIP37', 'name': 'Samskrutika Kannada / Balake Kannada / Constitution of India', 'credits': 1},  # choose one
                        {'subcode': '21CS38x OR 21CSL38x', 'name': 'Ability Enhancement Course – III', 'credits': 1},  # choose one
                    ]
                    for subject_data in subjects:
                        subject, created = Subject.objects.get_or_create(
                            subcode=subject_data['subcode'],
                            defaults={'name': subject_data['name'], 'credits': subject_data['credits']}
                        )
                        semester.subjects.add(subject)
                        
                    # for subject_data in subjects:
                    #     Subject.objects.get_or_create(semester=semester, **subject_data)
                
                if semester_number == 4:
                    subjects = [
                        {'subcode': '21MAT41', 'name': 'Mathematical Foundations for Computing, Probability and Statistics', 'credits': 3},
                        {'subcode': '21CS42', 'name': 'Design and Analysis of Algorithms', 'credits': 4},
                        {'subcode': '21CS43', 'name': 'Microcontroller and Embedded Systems', 'credits': 4},
                        {'subcode': '21CS44', 'name': 'Operating Systems', 'credits': 3},
                        {'subcode': '21BE45', 'name': 'Biology For Engineers', 'credits': 2},
                        {'subcode': '21CSL46', 'name': 'Python Programming Laboratory', 'credits': 1},
                        {'subcode': '21KSK47 OR 21KBK47 OR 21CIP47', 'name': 'Samskrutika Kannada / Balake Kannada / Constitution of India', 'credits': 1},  # choose one
                        {'subcode': '21CS48x OR 21CSL48x', 'name': 'Ability Enhancement Course – IV', 'credits': 1},  # choose one
                        {'subcode': '21UH49', 'name': 'Universal Human Values', 'credits': 1},
                        {'subcode': '21INT49', 'name': 'Inter/Intra Institutional Internship', 'credits': 2},
                    ]
                    for subject_data in subjects:
                        subject, created = Subject.objects.get_or_create(
                            subcode=subject_data['subcode'],
                            defaults={'name': subject_data['name'], 'credits': subject_data['credits']}
                        )
                        semester.subjects.add(subject)
                        
                    # for subject_data in subjects:
                    #     Subject.objects.get_or_create(semester=semester, **subject_data)
                    
                if semester_number == 5:
                    subjects = [
                        {'subcode': '21CS51', 'name': 'Automata Theory', 'credits': 3},
                        {'subcode': '21CS52', 'name': 'Computer Networks', 'credits': 4},
                        {'subcode': '21CS53', 'name': 'DBMS', 'credits': 3},
                        {'subcode': '21CS54', 'name': 'AI & ML', 'credits': 3},
                        {'subcode': '21CSL55', 'name': 'DBMS Lab', 'credits': 1},
                        {'subcode': '21RMI56', 'name': 'Research Methodology', 'credits': 2},
                        {'subcode': '21CIV57', 'name': 'Environmental Studies', 'credits': 1},
                        {'subcode': '21CS58x', 'name': 'Ability Enhancement', 'credits': 1},
                    ]
                    # for subject_data in subjects:
                    #     Subject.objects.get_or_create(semester=semester, **subject_data)
                    for subject_data in subjects:
                        subject, created = Subject.objects.get_or_create(
                            subcode=subject_data['subcode'],
                            defaults={'name': subject_data['name'], 'credits': subject_data['credits']}
                        )
                        semester.subjects.add(subject)
                    
                
                if semester_number == 6:
                    subjects = [
                        {'subcode': '21CS61', 'name': 'Software Engineering & Project Management', 'credits': 3},
                        {'subcode': '21CS62', 'name': 'Fullstack Development', 'credits': 4},
                        {'subcode': '21CS63', 'name': 'Computer Graphics and Fundamentals of Image Processing', 'credits': 3},
                        {'subcode': '21CS64x', 'name': 'Professional Elective Course-I', 'credits': 3},
                        {'subcode': '21CS65x', 'name': 'Open Elective Course-I', 'credits': 3},
                        {'subcode': '21CSL66', 'name': 'Computer Graphics and Image Processing Laboratory', 'credits': 1},
                        {'subcode': '21CSMP67', 'name': 'Mini Project', 'credits': 2},
                        {'subcode': '21INT68', 'name': 'Innovation/ Entrepreneurship/ Societal Internship', 'credits': 3},
                    ]

                    for subject_data in subjects:
                        subject, created = Subject.objects.get_or_create(
                            subcode=subject_data['subcode'],
                            defaults={'name': subject_data['name'], 'credits': subject_data['credits']}
                        )
                        semester.subjects.add(subject)
                        
                    # for subject_data in subjects:
                    #     Subject.objects.get_or_create(semester=semester, **subject_data)
                
                if semester_number == 7:
                    subjects = [
                        {'subcode': '21CS71', 'name': 'Big Data Analytics', 'credits': 3},
                        {'subcode': '21CS72', 'name': 'Cloud Computing', 'credits': 4},
                        {'subcode': '21CS73x', 'name': 'Professional Elective Course-II', 'credits': 3},
                        {'subcode': '21CS74x', 'name': 'Professional Elective Course-III', 'credits': 3},
                        {'subcode': '21CS75x', 'name': 'Open Elective Course-II', 'credits': 3},
                        {'subcode': '21CSP76', 'name': 'Project Work', 'credits': 10},
                    ]

                    for subject_data in subjects:
                        subject, created = Subject.objects.get_or_create(
                            subcode=subject_data['subcode'],
                            defaults={'name': subject_data['name'], 'credits': subject_data['credits']}
                        )
                        semester.subjects.add(subject)
                        
                    # for subject_data in subjects:
                    #     Subject.objects.get_or_create(semester=semester, **subject_data)

                if semester_number == 8:
                    subjects = [
                        {'subcode': '21CS81', 'name': 'Technical Seminar', 'credits': 1},
                        {'subcode': '21INT82', 'name': 'Research Internship/Industry Internship', 'credits': 15},
                        {'subcode': 'NCMC', 'name': 'NSS/PE/Yoga', 'credits': 0},  # NCMC: Non-Credit Mandatory Course
                    ]

                    for subject_data in subjects:
                        subject, created = Subject.objects.get_or_create(
                            subcode=subject_data['subcode'],
                            defaults={'name': subject_data['name'], 'credits': subject_data['credits']}
                        )
                        semester.subjects.add(subject)
                        
                    # for subject_data in subjects:
                    #     Subject.objects.get_or_create(semester=semester, **subject_data)
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
    return render(request, 'register.html')

# def register_view(request):
#     if request.method == 'POST':
#         usn = request.POST.get('usn')
#         name = request.POST.get('name')  # New field for name
#         password = request.POST.get('password')
#         if User.objects.filter(username=usn).exists():
#             messages.error(request, 'USN already exists.')
#         else:
#             # Create User
#             user = User.objects.create_user(username=usn, password=password)
#             # Create UserProfile
#             profile = UserProfile(user=user, usn=usn, name=name)
#             profile.save()
#             # Create Student
#             student = Student(usn=usn, name=name)
#             student.save()
#             for semester_number in range(1, 9):  # Assuming 8 semesters
#                 semester = Semester.objects.create(student=student, number=semester_number)
#                 # Create Subjects for each semester (example subjects for semester 5)
#                 if semester_number == 3:
#                     subjects = [
#                         {'subcode': '21MAT31', 'name': 'Transform Calculus, Fourier Series and Numerical Techniques', 'credits': 3},
#                         {'subcode': '21CS32', 'name': 'Data Structures and Applications', 'credits': 4},
#                         {'subcode': '21CS33', 'name': 'Analog and Digital Electronics', 'credits': 4},
#                         {'subcode': '21CS34', 'name': 'Computer Organization and Architecture', 'credits': 3},
#                         {'subcode': '21CSL35', 'name': 'Object Oriented Programming with JAVA Laboratory', 'credits': 1},
#                         {'subcode': '21SCR36', 'name': 'Social Connect and Responsibility', 'credits': 1},
#                         {'subcode': '21KSK37/47', 'name': 'Samskrutika Kannada / Balake Kannada / Constitution of India', 'credits': 1},  # choose one
#                         {'subcode': '21CS38x OR 21CSL38x', 'name': 'Ability Enhancement Course – III', 'credits': 1},  # choose one
#                     ]
#                     for subject_data in subjects:
#                         subject, created = Subject.objects.get_or_create(
#                             subcode=subject_data['subcode'],
#                             defaults={'name': subject_data['name'], 'credits': subject_data['credits']}
#                         )
#                         semester.subjects.add(subject)
#                 elif semester_number == 5:
#                     subjects = [
#                         {'subcode': '21CS51', 'name': 'Automata Theory', 'credits': 3},
#                         {'subcode': '21CS52', 'name': 'Computer Networks', 'credits': 4},
#                         {'subcode': '21CS53', 'name': 'DBMS', 'credits': 3},
#                         {'subcode': '21CS54', 'name': 'AI & ML', 'credits': 3},
#                         {'subcode': '21CSL55', 'name': 'DBMS Lab', 'credits': 1},
#                         {'subcode': '21RMI56', 'name': 'Research Methodology', 'credits': 2},
#                         {'subcode': '21CIV57', 'name': 'Environmental Studies', 'credits': 1},
#                         {'subcode': '21CS58x', 'name': 'Ability Enhancement', 'credits': 1},
#                     ]
#                     for subject_data in subjects:
#                         subject, created = Subject.objects.get_or_create(
#                             subcode=subject_data['subcode'],
#                             defaults={'name': subject_data['name'], 'credits': subject_data['credits']}
#                         )
#                         semester.subjects.add(subject)
#             messages.success(request, 'Registration successful. Please log in.')
#             return redirect('login')
#     return render(request, 'register.html')


# def login_view(request):
#     if request.method == 'POST':
#         usn = request.POST.get('usn')
#         password = request.POST.get('password')
#         user = authenticate(request, username=usn, password=password)
#         if user is not None:
#             login(request, user)
#             return redirect('get_data')  # Redirect to your desired page after login
#         else:
#             messages.error(request, 'Invalid USN or password.')
#     return render(request, 'login.html')

def login_view(request):
    if request.method == 'POST':
        usn = request.POST.get('usn')
        password = request.POST.get('password')
        user = authenticate(request, username=usn, password=password)
        if user is not None:
            login(request, user)
            return redirect('select_semester')  # Redirect to the semester selection page after login
        else:
            messages.error(request, 'Invalid USN or password.')
    return render(request, 'login.html')


def select_semester(request):
    if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
        user_profile = request.user.userprofile
        usn = user_profile.usn
        student = get_object_or_404(Student, usn=usn)
        semesters = Semester.objects.filter(student=student)

        context = {
            'semesters': semesters
        }
        return render(request, 'semesters.html', context)
    else:
        messages.error(request, 'User is not authenticated or does not have a profile.')
        return redirect('login')
