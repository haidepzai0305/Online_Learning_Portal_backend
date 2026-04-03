import functools
from django.http import JsonResponse
from jose import jwt, JWTError
from myproject.auth_service.app.core.config import settings

def jwt_required(view_func):
    @functools.wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # 1. Lấy token từ header Authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({"error": "Missing or invalid Authorization header"}, status=401)
        
        token = auth_header.split(' ')[1]
        
        try:
            # 2. Giải mã và xác thực token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            
            # 3. Gán thông tin người dùng vào request để view sử dụng
            request.user_id = payload.get('user_id')
            request.user_email = payload.get('sub')
            
            if not request.user_id:
                raise JWTError("Invalid token payload")
                
        except JWTError as e:
            return JsonResponse({"error": f"Token validation failed: {str(e)}"}, status=401)
        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
            
        return view_func(request, *args, **kwargs)
        
    return wrapped_view
