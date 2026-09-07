from functools import wraps

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.shortcuts import render, redirect, get_object_or_404
from .models import Section, Enrollment, Student, CurriculumCourse, CurriculumRequirement


def student_required(view_func):
    """Allow only authenticated users linked to a Student profile."""
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'student'):
            messages.error(request, 'บัญชีนี้ยังไม่มีข้อมูลนักศึกษา')
            return redirect('student_login')
        return view_func(request, *args, **kwargs)

    return wrapped_view


def student_login(request):
    if request.user.is_authenticated and hasattr(request.user, 'student'):
        return redirect('enrollment_list')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        if not hasattr(user, 'student'):
            form.add_error(None, 'บัญชีนี้ไม่มีสิทธิ์เข้าใช้งานระบบนักศึกษา')
        else:
            login(request, user)
            return redirect(request.GET.get('next') or 'enrollment_list')

    return render(request, 'Enroll/student_login.html', {'form': form})


@login_required
def student_logout(request):
    if request.method == 'POST':
        logout(request)
    return redirect('enrollment_list')


def enrollment_view(request):
    """Show the enrollment home page and link to the main workflows."""
    student = getattr(request.user, 'student', None)
    return render(request, 'Enroll/enrollment_home.html', {'student': student})


@student_required
def available_sections(request):
    """
    1. ดูรายวิชาและกลุ่มเรียนที่เปิดให้ลงทะเบียนได้ พร้อมตรวจสอบรายวิชาในหลักสูตร
    """
    student = request.user.student

    sections = Section.objects.annotate(
        current_enrolled=Count('enrollments', filter=Q(enrollments__status='ENROLLED'))
    ).select_related(
        'offered_course__course', 
        'offered_course__responsible_faculty'
    )

    enrolled_section_ids = []
    student_curriculum_course_ids = []
    
    # รายชื่อ section_id ที่นักเรียนลงทะเบียนสำเร็จไว้แล้ว
    enrolled_section_ids = list(
        Enrollment.objects.filter(student=student, status='ENROLLED')
        .values_list('section_id', flat=True)
    )
    # รายชื่อ course_id ที่อยู่ในหลักสูตรของนักเรียน
    student_curriculum_course_ids = list(
        CurriculumCourse.objects.filter(curriculum=student.curriculum)
        .values_list('course_id', flat=True)
    )

    context = {
        'sections': sections,
        'student': student,
        'enrolled_section_ids': enrolled_section_ids,
        'student_curriculum_course_ids': student_curriculum_course_ids,
    }
    return render(request, 'Enroll/enrollment_list.html', context)


@student_required
def enroll_section(request, section_id):
    """
    2. จัดการการลงทะเบียนรายวิชา พร้อมตรวจสอบเงื่อนไขหลักสูตรและหน่วยกิตสูงสุด
    """
    if request.method == 'POST':
        student = request.user.student

        section = get_object_or_404(Section, id=section_id)
        course = section.offered_course.course

        curriculum_course = CurriculumCourse.objects.filter(
            curriculum=student.curriculum,
            course=course
        ).first()

        if not curriculum_course:
            messages.error(
                request, 
                f"วิชา {course.code} {course.name} ไม่ได้อยู่ในหลักสูตรของคุณ ({student.curriculum.name})"
            )
            return redirect('available_sections')

        already_enrolled = Enrollment.objects.filter(
            student=student, 
            section__offered_course__course=course,
            status='ENROLLED'
        ).exists()
        
        if already_enrolled:
            messages.warning(request, f"คุณได้ลงทะเบียนวิชา {course.code} ไปเรียบร้อยแล้ว")
            return redirect('available_sections')

        current_count = Enrollment.objects.filter(section=section, status='ENROLLED').count()
        if current_count >= section.max_seats:
            messages.error(request, "กลุ่มเรียนนี้เต็มแล้ว ไม่สามารถลงทะเบียนได้")
            return redirect('available_sections')

        requirement = CurriculumRequirement.objects.filter(
            curriculum=student.curriculum,
            course_class=curriculum_course.course_class,
            general_category=curriculum_course.general_category
        ).first()

        if requirement and requirement.max_credits is not None:
            
            enrolled_category_credits = Enrollment.objects.filter(
                student=student,
                status='ENROLLED',
                section__offered_course__course__curriculum_courses__curriculum=student.curriculum,
                section__offered_course__course__curriculum_courses__course_class=curriculum_course.course_class,
                section__offered_course__course__curriculum_courses__general_category=curriculum_course.general_category
            ).aggregate(
                total=Sum('section__offered_course__course__credits')
            )['total'] or 0

            if enrolled_category_credits + course.credits > requirement.max_credits:
                messages.error(
                    request, 
                    f"ไม่สามารถลงทะเบียนได้ เนื่องจากหน่วยกิตรวมในกลุ่มวิชา {curriculum_course.get_course_class_display()} "
                    f"จะเกินจำนวนสูงสุดที่หลักสูตรกำหนด ({requirement.max_credits} หน่วยกิต)"
                )
                return redirect('available_sections')

        enrollment, created = Enrollment.objects.get_or_create(
            student=student,
            section=section,
            defaults={'status': 'ENROLLED'}
        )
        
        if not created and enrollment.status != 'ENROLLED':
            enrollment.status = 'ENROLLED'
            enrollment.save()

        messages.success(
            request, 
            f"ลงทะเบียนวิชา {course.code} {course.name} สำเร็จ"
        )

    return redirect('available_sections')


@student_required
def drop_section(request, section_id):
    """Drop the current student's enrollment in a section."""
    if request.method != 'POST':
        return redirect('available_sections')

    student = request.user.student

    enrollment = get_object_or_404(
        Enrollment,
        student=student,
        section_id=section_id,
        status='ENROLLED',
    )
    enrollment.status = 'DROPPED'
    enrollment.save(update_fields=['status'])
    messages.success(request, "ถอนรายวิชาเรียบร้อยแล้ว")
    return redirect('available_sections')


@student_required
def student_summary_view(request):
    """Show the student's enrolled courses and credit total."""
    student = request.user.student
    enrollments = Enrollment.objects.none()
    total_credits = 0

    enrollments = Enrollment.objects.filter(
        student=student,
        status='ENROLLED',
    ).select_related(
        'section__offered_course__course',
        'section__offered_course__responsible_faculty',
    ).order_by(
        'section__offered_course__course__code',
    )
    total_credits = enrollments.aggregate(
        total=Sum('section__offered_course__course__credits')
    )['total'] or 0

    return render(request, 'Enroll/student_summary.html', {
        'student': student,
        'enrollments': enrollments,
        'total_credits': total_credits,
    })