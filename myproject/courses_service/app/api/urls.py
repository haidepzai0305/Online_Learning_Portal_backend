from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_courses_view, name='list_courses'),
    path('create/', views.create_course_view, name='create_course'),
    path('<int:course_id>/', views.get_course_detail_view, name='get_course_detail'),
    path('<int:course_id>/update/', views.update_course_view, name='update_course'),
    path('<int:course_id>/delete/', views.delete_course_view, name='delete_course'),
    
    path('<int:course_id>/materials/upload/', views.upload_material_view, name='upload_material'),
    path('<int:course_id>/announcements/post/', views.post_announcement_view, name='post_announcement'),
    
    path('<int:course_id>/students/', views.list_enrolled_students_view, name='list_enrolled_students'),
    path('<int:course_id>/enroll/', views.enroll_course_view, name='enroll_course'),
    path('<int:course_id>/progress/', views.update_progress_view, name='update_progress'),
]
