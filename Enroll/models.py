from django.db import models
from django.contrib.auth.models import User


# =========================================================
# 1. มหาวิทยาลัย
# =========================================================
class University(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


# =========================================================
# 2. คณะ
# =========================================================
class Faculty(models.Model):
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name='faculties'
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


# =========================================================
# 3. ภาควิชา
# =========================================================
class Department(models.Model):
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name='departments'
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


# =========================================================
# 4. หลักสูตร
# =========================================================
class Curriculum(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='curriculums'
    )
    name = models.CharField(max_length=255)
    year = models.IntegerField()  # เช่น 2569

    def __str__(self):
        return f"{self.name} ({self.year})"


# =========================================================
# 5. นักศึกษา
# =========================================================
class Student(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    student_id = models.CharField(
        max_length=15,
        unique=True
    )
    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.PROTECT,
        related_name='students'
    )

    def __str__(self):
        return (
            f"{self.student_id} - "
            f"{self.user.first_name} {self.user.last_name}"
        )


# =========================================================
# 6. รายวิชา (Master Data)
#
# Course ไม่เก็บว่าเป็น CORE / SPECIFIC / GENERAL
# เพราะประเภทของวิชาขึ้นอยู่กับ "หลักสูตร"
# =========================================================
class Course(models.Model):
    code = models.CharField(
        max_length=10,
        unique=True
    )
    name = models.CharField(
        max_length=255
    )
    credits = models.IntegerField(
        default=3
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses'
    )

    def __str__(self):
        return f"{self.code} {self.name}"


# =========================================================
# 7. Requirement ของหลักสูตร
#
# ตอบคำถาม:
# "หลักสูตรนี้ต้องการหน่วยกิตของแต่ละกลุ่มเท่าไร?"
#
# ตัวอย่าง:
# CORE      min 30 / max 30
# SPECIFIC  min 16 / max 24
# GENERAL   หมวด 1 min 6
# GENERAL   หมวด 2 min 6
# GENERAL   หมวด 3 min 6
# =========================================================
class CurriculumRequirement(models.Model):

    CLASS_CHOICES = [
        ('CORE', 'วิชาแกน'),
        ('SPECIFIC', 'วิชาเฉพาะ'),
        ('GENERAL', 'วิชาทั่วไป'),
    ]

    GENERAL_CATEGORY_CHOICES = [
        ('1', 'หมวด 1'),
        ('2', 'หมวด 2'),
        ('3', 'หมวด 3'),
    ]

    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.CASCADE,
        related_name='requirements'
    )

    course_class = models.CharField(
        max_length=10,
        choices=CLASS_CHOICES
    )

    general_category = models.CharField(
        max_length=1,
        choices=GENERAL_CATEGORY_CHOICES,
        null=True,
        blank=True
    )

    min_credits = models.IntegerField(
        default=0
    )

    max_credits = models.IntegerField(
        null=True,
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'curriculum',
                    'course_class',
                    'general_category'
                ],
                name='unique_curriculum_requirement'
            )
        ]

    def __str__(self):
        category = ""

        if self.course_class == 'GENERAL':
            category = f" - หมวด {self.general_category}"

        return (
            f"{self.curriculum} - "
            f"{self.get_course_class_display()}"
            f"{category}"
        )


# =========================================================
# 8. รายวิชาที่อยู่ในหลักสูตร
#
# ตอบคำถาม:
# "หลักสูตรนี้มีวิชาอะไร และวิชานั้นอยู่กลุ่มไหน?"
#
# CORE
#   -> นักศึกษาต้องเรียนทุกวิชาในกลุ่มนี้
#
# SPECIFIC
#   -> เป็น Pool ให้นักศึกษาเลือก
#
# GENERAL
#   -> เป็น Pool และแบ่งเป็นหมวด 1/2/3
# =========================================================
class CurriculumCourse(models.Model):

    CLASS_CHOICES = [
        ('CORE', 'วิชาแกน'),
        ('SPECIFIC', 'วิชาเฉพาะ'),
        ('GENERAL', 'วิชาทั่วไป'),
    ]

    GENERAL_CATEGORY_CHOICES = [
        ('1', 'หมวด 1'),
        ('2', 'หมวด 2'),
        ('3', 'หมวด 3'),
    ]

    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.CASCADE,
        related_name='curriculum_courses'
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='curriculum_courses'
    )

    course_class = models.CharField(
        max_length=10,
        choices=CLASS_CHOICES
    )

    # ใช้เฉพาะ GENERAL
    general_category = models.CharField(
        max_length=1,
        choices=GENERAL_CATEGORY_CHOICES,
        null=True,
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['curriculum', 'course'],
                name='unique_curriculum_course'
            )
        ]

    def __str__(self):
        category = ""

        if self.course_class == 'GENERAL':
            category = f" - หมวด {self.general_category}"

        return (
            f"{self.curriculum} - "
            f"{self.course.code} - "
            f"{self.get_course_class_display()}"
            f"{category}"
        )


# =========================================================
# 9. รายวิชาที่เปิดในแต่ละภาคการศึกษา
# =========================================================
class OfferedCourse(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='offered_courses'
    )

    responsible_faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name='managed_offered_courses'
    )

    academic_year = models.IntegerField()  # เช่น 2569
    semester = models.IntegerField()       # 1, 2, 3

    def __str__(self):
        return (
            f"{self.course.code} -> "
            f"เปิดโดยคณะ {self.responsible_faculty.name} "
            f"({self.semester}/{self.academic_year})"
        )


# =========================================================
# 10. Section (หมู่เรียน)
# =========================================================
class Section(models.Model):
    offered_course = models.ForeignKey(
        OfferedCourse,
        on_delete=models.CASCADE,
        related_name='sections'
    )

    section_number = models.IntegerField()

    max_seats = models.IntegerField(
        default=30
    )

    room = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['offered_course', 'section_number'],
                name='unique_offered_course_section'
            )
        ]

    def __str__(self):
        return (
            f"{self.offered_course.course.code} "
            f"Sec {self.section_number}"
        )


# =========================================================
# 11. การลงทะเบียน
# =========================================================
class Enrollment(models.Model):

    STATUS_CHOICES = [
        ('ENROLLED', 'ลงทะเบียนสำเร็จ'),
        ('DROPPED', 'ถอนรายวิชา'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    enrolled_at = models.DateTimeField(
        auto_now_add=True
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ENROLLED'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'section'],
                name='unique_student_section_enrollment'
            )
        ]

    def __str__(self):
        return (
            f"{self.student.student_id} -> "
            f"{self.section}"
        )