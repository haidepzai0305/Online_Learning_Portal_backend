from django.urls import path
from . import views

urlpatterns = [
    path('explain/', views.explain_concept_view, name='ai_explain'),
    path('summarize/', views.summarize_doc_view, name='ai_summarize'),
    path('generate-questions/', views.generate_questions_view, name='ai_generate_questions'),
    path('course/<int:course_id>/ask/', views.rag_qa_view, name='ai_rag_qa'),
    path('course/<int:course_id>/history/', views.chat_history_view, name='ai_chat_history'),
    path('course/<int:course_id>/history/clear/', views.clear_chat_history_view, name='ai_chat_history_clear'),
]
