from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from Enroll.models import (
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


class Command(BaseCommand):
    help = "Seed database with sample enrollment data"

    def handle(self, *args, **options):

        # =====================================================
        # 1. University
        # =====================================================
        university, _ = University.objects.get_or_create(
            code="KU",
            defaults={
                "name": "มหาวิทยาลัยเกษตรศาสตร์"
            }
        )

        # =====================================================
        # 2. Faculty
        # =====================================================
        faculty, _ = Faculty.objects.get_or_create(
            code="SCI",
            defaults={
                "university": university,
                "name": "คณะวิทยาศาสตร์"
            }
        )

        # =====================================================
        # 3. Department
        # =====================================================
        department, _ = Department.objects.get_or_create(
            code="CS",
            defaults={
                "faculty": faculty,
                "name": "ภาควิชาวิทยาการคอมพิวเตอร์"
            }
        )

        # =====================================================
        # 4. Curriculum
        # =====================================================
        curriculum, _ = Curriculum.objects.get_or_create(
            department=department,
            year=2569,
            defaults={
                "name": "วิทยาการคอมพิวเตอร์"
            }
        )

        # =====================================================
        # 5. Curriculum Requirements
        # =====================================================

        # CORE
        CurriculumRequirement.objects.get_or_create(
            curriculum=curriculum,
            course_class="CORE",
            general_category=None,
            defaults={
                "min_credits": 30,
                "max_credits": 30,
            }
        )

        # SPECIFIC
        CurriculumRequirement.objects.get_or_create(
            curriculum=curriculum,
            course_class="SPECIFIC",
            general_category=None,
            defaults={
                "min_credits": 16,
                "max_credits": 24,
            }
        )

        # GENERAL - Category 1
        CurriculumRequirement.objects.get_or_create(
            curriculum=curriculum,
            course_class="GENERAL",
            general_category="1",
            defaults={
                "min_credits": 6,
                "max_credits": None,
            }
        )

        # GENERAL - Category 2
        CurriculumRequirement.objects.get_or_create(
            curriculum=curriculum,
            course_class="GENERAL",
            general_category="2",
            defaults={
                "min_credits": 6,
                "max_credits": None,
            }
        )

        # GENERAL - Category 3
        CurriculumRequirement.objects.get_or_create(
            curriculum=curriculum,
            course_class="GENERAL",
            general_category="3",
            defaults={
                "min_credits": 6,
                "max_credits": None,
            }
        )

        # =====================================================
        # 6. Users
        # =====================================================

        user1, _ = User.objects.get_or_create(
            username="65010001",
            defaults={
                "first_name": "สมชาย",
                "last_name": "ใจดี",
            }
        )

        user1.set_password("123456")
        user1.save()

        user2, _ = User.objects.get_or_create(
            username="65010002",
            defaults={
                "first_name": "สมหญิง",
                "last_name": "รักเรียน",
            }
        )

        user2.set_password("123456")
        user2.save()

        # =====================================================
        # 7. Students
        # =====================================================

        student1, _ = Student.objects.get_or_create(
            student_id="65010001",
            defaults={
                "user": user1,
                "curriculum": curriculum,
            }
        )

        student2, _ = Student.objects.get_or_create(
            student_id="65010002",
            defaults={
                "user": user2,
                "curriculum": curriculum,
            }
        )

        # =====================================================
        # 8. Courses
        # =====================================================

        database, _ = Course.objects.get_or_create(
            code="01418211",
            defaults={
                "name": "Database Systems",
                "credits": 3,
                "department": department,
            }
        )

        datacom, _ = Course.objects.get_or_create(
            code="01418213",
            defaults={
                "name": "Data Communication",
                "credits": 3,
                "department": department,
            }
        )

        ai, _ = Course.objects.get_or_create(
            code="01418231",
            defaults={
                "name": "Artificial Intelligence",
                "credits": 3,
                "department": department,
            }
        )

        ml, _ = Course.objects.get_or_create(
            code="01418232",
            defaults={
                "name": "Machine Learning",
                "credits": 3,
                "department": department,
            }
        )

        english, _ = Course.objects.get_or_create(
            code="01371111",
            defaults={
                "name": "English for Communication",
                "credits": 3,
                "department": None,
            }
        )

        thai_society, _ = Course.objects.get_or_create(
            code="01371101",
            defaults={
                "name": "Thai Society",
                "credits": 3,
                "department": None,
            }
        )

        math, _ = Course.objects.get_or_create(
            code="01417101",
            defaults={
                "name": "Fundamental Mathematics",
                "credits": 3,
                "department": None,
            }
        )

        # =====================================================
        # 9. Curriculum Courses
        # =====================================================

        # ---------- CORE ----------
        CurriculumCourse.objects.get_or_create(
            curriculum=curriculum,
            course=database,
            defaults={
                "course_class": "CORE",
                "general_category": None,
            }
        )

        CurriculumCourse.objects.get_or_create(
            curriculum=curriculum,
            course=datacom,
            defaults={
                "course_class": "CORE",
                "general_category": None,
            }
        )

        # ---------- SPECIFIC POOL ----------
        CurriculumCourse.objects.get_or_create(
            curriculum=curriculum,
            course=ai,
            defaults={
                "course_class": "SPECIFIC",
                "general_category": None,
            }
        )

        CurriculumCourse.objects.get_or_create(
            curriculum=curriculum,
            course=ml,
            defaults={
                "course_class": "SPECIFIC",
                "general_category": None,
            }
        )

        # ---------- GENERAL ----------
        CurriculumCourse.objects.get_or_create(
            curriculum=curriculum,
            course=english,
            defaults={
                "course_class": "GENERAL",
                "general_category": "1",
            }
        )

        CurriculumCourse.objects.get_or_create(
            curriculum=curriculum,
            course=thai_society,
            defaults={
                "course_class": "GENERAL",
                "general_category": "2",
            }
        )

        CurriculumCourse.objects.get_or_create(
            curriculum=curriculum,
            course=math,
            defaults={
                "course_class": "GENERAL",
                "general_category": "3",
            }
        )

        # =====================================================
        # 10. Offered Course
        # =====================================================

        database_offered, _ = OfferedCourse.objects.get_or_create(
            course=database,
            responsible_faculty=faculty,
            academic_year=2569,
            semester=1,
        )

        datacom_offered, _ = OfferedCourse.objects.get_or_create(
            course=datacom,
            responsible_faculty=faculty,
            academic_year=2569,
            semester=1,
        )

        # =====================================================
        # 11. Sections
        # =====================================================

        database_section, _ = Section.objects.get_or_create(
            offered_course=database_offered,
            section_number=1,
            defaults={
                "max_seats": 30,
                "room": "SCB-401",
            }
        )

        datacom_section, _ = Section.objects.get_or_create(
            offered_course=datacom_offered,
            section_number=1,
            defaults={
                "max_seats": 30,
                "room": "SCB-402",
            }
        )

        # =====================================================
        # 12. Enrollment
        # =====================================================

        Enrollment.objects.get_or_create(
            student=student1,
            section=database_section,
            defaults={
                "status": "ENROLLED",
            }
        )

        Enrollment.objects.get_or_create(
            student=student2,
            section=database_section,
            defaults={
                "status": "ENROLLED",
            }
        )

        # =====================================================
        # DONE
        # =====================================================

        self.stdout.write(
            self.style.SUCCESS(
                "Database seeding completed successfully!"
            )
        )