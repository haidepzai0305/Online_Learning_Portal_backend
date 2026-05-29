from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_courses_view, name='list_courses'),
    path('enrolled/', views.list_student_enrollments_view, name='list_student_enrollments'),
    path('my-courses/', views.list_my_courses_view, name='list_my_courses'),
    path('create/', views.create_course_view, name='create_course'),
    path('<int:course_id>/', views.get_course_detail_view, name='get_course_detail'),
    path('<int:course_id>/update/', views.update_course_view, name='update_course'),
    path('<int:course_id>/delete/', views.delete_course_view, name='delete_course'),
    
    path('<int:course_id>/materials/upload/', views.upload_material_view, name='upload_material'),
    path('<int:course_id>/announcements/post/', views.post_announcement_view, name='post_announcement'),
    
    path('<int:course_id>/students/', views.list_enrolled_students_view, name='list_enrolled_students'),
    path('<int:course_id>/enroll/', views.enroll_course_view, name='enroll_course'),
    path('<int:course_id>/progress/', views.update_progress_view, name='update_progress'),
    
    path('<int:course_id>/assignments/', views.list_assignments_view, name='list_assignments'),
    path('<int:course_id>/assignments/create/', views.create_assignment_view, name='create_assignment'),
    path('assignments/<int:assignment_id>/submit/', views.submit_assignment_view, name='submit_assignment'),
    path('submissions/<int:submission_id>/grade/', views.grade_submission_view, name='grade_submission'),
    
    # Video Streaming
    path('materials/<int:material_id>/stream/', views.stream_video_view, name='stream_video'),
    
    # Interactions
    path('<int:course_id>/qa/', views.get_course_qa_view, name='get_course_qa'),
    path('<int:course_id>/qa/post/', views.post_course_qa_view, name='post_course_qa'),
    path('<int:course_id>/notes/', views.get_student_note_view, name='get_student_note'),
    path('<int:course_id>/notes/save/', views.save_student_note_view, name='save_student_note'),
]
