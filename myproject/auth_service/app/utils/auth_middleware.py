import functools
from django.http import JsonResponse
from jose import jwt, JWTError
from myproject.auth_service.app.core.config import settings

def jwt_required(view_func):
    @functools.wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # 1. Lấy token từ header Authorization hoặc query param
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            token = request.GET.get('token')

        if not token:
            return JsonResponse({"error": "Missing token. Provide 'Authorization: Bearer <token>' or '?token=<token>'"}, status=401)
        
        try:
            # 2. Giải mã và xác thực token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            
            # 3. Gán thông tin người dùng vào request để view sử dụng
            request.user_id = payload.get('user_id')
            request.user_email = payload.get('sub')
            request.user_roles = payload.get('roles', [])
            
            if not request.user_id:
                print(f"DEBUG JWT: Token valid but mission user_id. Payload: {payload}")
                raise JWTError("Invalid token payload")
                
        except JWTError as e:
            print(f"DEBUG JWT: Validation failed for token {token[:10]}... Error: {str(e)}")
            print(f"DEBUG JWT: Using SECRET_KEY: {settings.SECRET_KEY[:10]}...")
            return JsonResponse({"error": f"Token validation failed: {str(e)}"}, status=401)
        except Exception as e:
            print(f"DEBUG JWT: Unexpected error: {str(e)}")
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
            
        return view_func(request, *args, **kwargs)
        
    return wrapped_view

def role_required(*allowed_roles):
    def decorator(view_func):
        @jwt_required
        @functools.wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            # Check if any of the user's roles are in the allowed_roles list
            user_roles = getattr(request, 'user_roles', [])
            if not any(role in allowed_roles for role in user_roles):
                return JsonResponse({
                    "error": f"Permission denied. Required roles: {', '.join(allowed_roles)}"
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator
