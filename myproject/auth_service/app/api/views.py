import json
import re
import logging
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from myproject.auth_service.app.core.config import settings
from myproject.auth_service.app.services.auth_service import AuthService
from myproject.auth_service.app.utils.auth_middleware import jwt_required

logger = logging.getLogger(__name__)

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

@csrf_exempt
def register_view(request):
    if request.method == "POST":
        try:
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON format"}, status=400)

            email = data.get("email", "").strip()
            username = data.get("username", "").strip()
            password = data.get("password")

            missing_fields = []
            if not email: missing_fields.append("email")
            if not username: missing_fields.append("username")
            if not password: missing_fields.append("password")

            if missing_fields:
                return JsonResponse({
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                }, status=400)

            if not is_valid_email(email):
                return JsonResponse({"error": "Invalid email format"}, status=400)

            if len(password) < 6:
                return JsonResponse({"error": "Password must be at least 6 characters long"}, status=400)

            user = AuthService.register_user(email, username, password)

            return JsonResponse({
                "message": "User registered successfully",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username
                }
            }, status=201)

        except Exception as e:
            logger.error(f"Registration View Error: {str(e)}", exc_info=True)
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def login_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email", "").strip()
            password = data.get("password")

            if not email or not password:
                return JsonResponse({"error": "Email and password are required"}, status=400)

            auth_result = AuthService.authenticate_user(email, password)

            if not auth_result:
                return JsonResponse({"error": "Invalid credentials"}, status=401)

            return JsonResponse(auth_result)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
@jwt_required
def me_view(request):
    """
    Endpoint protected by JWT token to get current user info.
    Access it with header: Authorization: Bearer <token>
    """
    if request.method == "GET":
        return JsonResponse({
            "user_id": request.user_id,
            "email": request.user_email,
            "message": "Authenticated user retrieved successfully"
        })
    

    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def google_login(request):
    """
    Endpoint for Google Login.
    Expected POST body: {"code": "..."}
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            code = data.get("code")
            
            if not code:
                return JsonResponse({"error": "Code is required"}, status=400)
            
            # Exchange code for access token
            token_url = "https://oauth2.googleapis.com/token"
            token_payload = {
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            }
            response = requests.post(token_url, data=token_payload)
            token_data = response.json()
            
            if "error" in token_data:
                return JsonResponse({"error": token_data.get("error_description", token_data.get("error"))}, status=400)
                
            access_token = token_data.get("access_token")
            
            # Get user info
            user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
            user_info_res = requests.get(user_info_url, headers={"Authorization": f"Bearer {access_token}"})
            user_info = user_info_res.json()
            
            email = user_info.get("email")
            name = user_info.get("name")
            google_id = user_info.get("sub")
            
            if not email:
                return JsonResponse({"error": "Email not provided by Google"}, status=400)
            
            auth_result = AuthService.social_login(
                email=email,
                username=name,
                provider="google",
                provider_id=google_id,
                extra_data=user_info
            )
            
            return JsonResponse(auth_result)
            
        except Exception as e:
            logger.error(f"Google Login Error: {str(e)}", exc_info=True)
            return JsonResponse({"error": str(e)}, status=400)
            
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def microsoft_login(request):
    """
    Endpoint for Microsoft Login.
    Expected POST body: {"code": "..."}
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            code = data.get("code")
            
            if not code:
                return JsonResponse({"error": "Code is required"}, status=400)

            # Exchange code for access token
            token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
            token_payload = {
                "client_id": settings.MICROSOFT_CLIENT_ID,
                "client_secret": settings.MICROSOFT_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.MICROSOFT_REDIRECT_URI,
                "grant_type": "authorization_code",
            }
            response = requests.post(token_url, data=token_payload)
            token_data = response.json()
            
            if "error" in token_data:
                 return JsonResponse({"error": token_data.get("error_description", token_data.get("error"))}, status=400)
                 
            access_token = token_data.get("access_token")
            
            # Get user info from Microsoft Graph
            user_info_url = "https://graph.microsoft.com/v1.0/me"
            user_info_res = requests.get(user_info_url, headers={"Authorization": f"Bearer {access_token}"})
            user_info = user_info_res.json()
            
            email = user_info.get("mail") or user_info.get("userPrincipalName")
            name = user_info.get("displayName")
            microsoft_id = user_info.get("id")
            
            if not email:
                return JsonResponse({"error": "Email not provided by Microsoft"}, status=400)

            auth_result = AuthService.social_login(
                email=email,
                username=name,
                provider="microsoft",
                provider_id=microsoft_id,
                extra_data=user_info
            )
            
            return JsonResponse(auth_result)
        except Exception as e:
            logger.error(f"Microsoft Login Error: {str(e)}", exc_info=True)
            return JsonResponse({"error": str(e)}, status=400)
            
    return JsonResponse({"error": "Method not allowed"}, status=405)
