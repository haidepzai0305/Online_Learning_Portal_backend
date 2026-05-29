import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from myproject.auth_service.app.utils.auth_middleware import jwt_required
from myproject.ai_service.app.services.ai_service import AIService

CHAT_HISTORY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..", "chat_history")

def _history_path(user_id, course_id):
    os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)
    return os.path.join(CHAT_HISTORY_DIR, f"user_{user_id}_course_{course_id}.json")

@csrf_exempt
@jwt_required
def explain_concept_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        concept = data.get("concept")
        level = data.get("level", "intermediate")
        
        if not concept:
            return JsonResponse({"error": "Concept is required"}, status=400)
            
        explanation = AIService.explain_concept(concept, level)
        return JsonResponse({"explanation": explanation})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
@jwt_required
def summarize_doc_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        content = data.get("content")
        
        if not content:
            return JsonResponse({"error": "Content is required"}, status=400)
            
        summary = AIService.summarize_document(content)
        return JsonResponse({"summary": summary})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
@jwt_required
def generate_questions_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        topic = data.get("topic")
        difficulty = data.get("difficulty", "medium")
        count = data.get("count", 5)
        
        if not topic:
            return JsonResponse({"error": "Topic is required"}, status=400)
            
        questions = AIService.generate_practice_questions(topic, difficulty, count)
        return JsonResponse({"questions": questions})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

from myproject.ai_service.app.services.rag_service import RAGService

@csrf_exempt
@jwt_required
def rag_qa_view(request, course_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        question = data.get("question")
        
        if not question:
            return JsonResponse({"error": "Question is required"}, status=400)
            
        answer = RAGService.answer_with_rag(str(course_id), question)
        return JsonResponse({"answer": answer})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@jwt_required
def chat_history_view(request, course_id):
    """GET: load history | POST: save history for current user + course"""
    user_id = getattr(request, "user_id", None) or getattr(request, "user", {}).get("id", "anon")
    path = _history_path(user_id, course_id)

    if request.method == "GET":
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    history = json.load(f)
            else:
                history = []
            return JsonResponse({"history": history})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            history = data.get("history", [])
            # Keep last 200 messages max
            history = history[-200:]
            with open(path, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            return JsonResponse({"status": "saved", "count": len(history)})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
@jwt_required
def clear_chat_history_view(request, course_id):
    """DELETE: clear history for current user + course"""
    user_id = getattr(request, "user_id", None) or getattr(request, "user", {}).get("id", "anon")
    path = _history_path(user_id, course_id)
    try:
        if os.path.exists(path):
            os.remove(path)
        return JsonResponse({"status": "cleared"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
