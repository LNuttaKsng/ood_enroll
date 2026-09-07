from django.contrib import admin

from .models import (
    University,
    Faculty,
    Department,
    Curriculum,
    Student,
    Course,
    CurriculumRequirement,
    CurriculumCourse,
    OfferedCourse,
    Section,
    Enrollment,
)


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'university')
    list_filter = ('university',)
    search_fields = ('code', 'name')
    autocomplete_fields = ('university',)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'faculty')
    list_filter = ('faculty',)
    search_fields = ('code', 'name')
    autocomplete_fields = ('faculty',)


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'department')
    list_filter = ('year', 'department')
    search_fields = ('name',)
    autocomplete_fields = ('department',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'user', 'curriculum')
    list_filter = ('curriculum',)
    search_fields = (
        'student_id',
        'user__username',
        'user__first_name',
        'user__last_name',
    )
    autocomplete_fields = ('user', 'curriculum')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name',
        'credits',
        'department',
    )
    list_filter = ('department',)
    search_fields = ('code', 'name')
    autocomplete_fields = ('department',)


@admin.register(CurriculumRequirement)
class CurriculumRequirementAdmin(admin.ModelAdmin):
    list_display = (
        'curriculum',
        'course_class',
        'general_category',
        'min_credits',
        'max_credits',
    )
    list_filter = (
        'curriculum',
        'course_class',
        'general_category',
    )
    autocomplete_fields = ('curriculum',)


@admin.register(CurriculumCourse)
class CurriculumCourseAdmin(admin.ModelAdmin):
    list_display = (
        'curriculum',
        'course',
        'course_class',
        'general_category',
    )
    list_filter = (
        'curriculum',
        'course_class',
        'general_category',
    )
    search_fields = (
        'course__code',
        'course__name',
    )
    autocomplete_fields = ('curriculum', 'course')


@admin.register(OfferedCourse)
class OfferedCourseAdmin(admin.ModelAdmin):
    list_display = (
        'course',
        'responsible_faculty',
        'academic_year',
        'semester',
    )
    list_filter = (
        'academic_year',
        'semester',
        'responsible_faculty',
    )
    search_fields = ('course__code', 'course__name')
    autocomplete_fields = ('course', 'responsible_faculty')


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = (
        'offered_course',
        'section_number',
        'max_seats',
        'room',
    )
    list_filter = ('offered_course',)
    search_fields = (
        'offered_course__course__code',
        'offered_course__course__name',
    )
    autocomplete_fields = ('offered_course',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'section',
        'status',
        'enrolled_at',
    )
    list_filter = (
        'status',
    )
    search_fields = (
        'student__student_id',
        'section__offered_course__course__code',
    )
    autocomplete_fields = ('student', 'section')
    readonly_fields = ('enrolled_at',)