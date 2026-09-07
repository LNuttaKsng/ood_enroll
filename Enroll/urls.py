from django.urls import path
from . import views

urlpatterns = [
    path('', views.enrollment_view, name='enrollment_list'),
    path('login/', views.student_login, name='student_login'),
    path('logout/', views.student_logout, name='student_logout'),
    path('enrollment/', views.available_sections, name='available_sections'),
    path('enrollment/enroll/<int:section_id>/', views.enroll_section, name='enroll_section'),
    path('enrollment/drop/<int:section_id>/', views.drop_section, name='drop_section'),
    path('enrollment/summary/', views.student_summary_view, name='student_summary'),
]