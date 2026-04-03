from datetime import timedelta
from django.db import transaction
from myproject.auth_service.app.models.users import User
from myproject.auth_service.app.models.user_social_auth import UserSocialAuth
from myproject.auth_service.app.models.user_credentials import UserCredentials
from myproject.auth_service.app.utils.security import get_password_hash, verify_password, create_access_token
from myproject.auth_service.app.messaging.publisher import publisher
from myproject.auth_service.app.core.config import settings

class AuthService:
    @staticmethod
    def register_user(email, username, password):
        # 1. Kiểm tra Email/Username đã tồn tại hay chưa
        if User.objects.filter(email=email).exists():
            raise Exception("Email already registered")
        
        if User.objects.filter(username=username).exists():
            raise Exception("Username already registered")

        try:
            # 2. Bắt đầu transaction để lưu dữ liệu an toàn
            with transaction.atomic():
                # Lưu User thông tin cơ bản
                user = User.objects.create(
                    email=email,
                    username=username
                )

                # Lưu Credential (Mật khẩu đã băm)
                UserCredentials.objects.create(
                    user=user,
                    password_hash=get_password_hash(password)
                )

            # 3. PHÁT EVENT SANG RABBITMQ SAU KHI LƯU DB THÀNH CÔNG
            event_data = {
                "user_id": user.id,
                "email": user.email,
                "username": user.username,
                "action": "registration"
            }
            publisher.publish_user_registered(event_data)

            return user

        except Exception as e:
            # Nếu lưu DB lỗi, transaction sẽ tự rollback
            print(f"Registration Error: {e}")
            raise e

    @staticmethod
    def authenticate_user(email, password):
        try:
            print(f"DEBUG: Attempting login for email: {email}")
            user = User.objects.get(email=email)
            credentials = UserCredentials.objects.get(user=user)

            if not verify_password(password, credentials.password_hash):
                print(f"DEBUG: Password verification failed for user: {email}")
                return None

            print(f"DEBUG: Login successful for user: {email}")
            # Tạo Access Token
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.email, "user_id": user.id}, 
                expires_delta=access_token_expires
            )

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username
                }
            }

        except (User.DoesNotExist, UserCredentials.DoesNotExist):
            return None

    @staticmethod
    def social_login(email, username, provider, provider_id, extra_data=None):
        try:
            # 1. Tìm UserSocialAuth record
            social_auth = UserSocialAuth.objects.filter(provider=provider, provider_id=provider_id).first()
            
            if social_auth:
                user = social_auth.user
            else:
                # 2. Nếu chưa có Social record, xem email đã tồn tại chưa
                user = User.objects.filter(email=email).first()
                
                if not user:
                    # 3. Chứa có user -> Đăng ký mới
                    with transaction.atomic():
                        user = User.objects.create(
                            email=email,
                            username=username if username else email.split('@')[0],
                            email_verified=True # Social login normally verified email
                        )
                
                # 4. Tạo Social mapping
                UserSocialAuth.objects.create(
                    user=user,
                    provider=provider,
                    provider_id=provider_id,
                    extra_data=str(extra_data) if extra_data else None
                )

                # 5. Phát event
                event_data = {
                    "user_id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "action": f"{provider}_login"
                }
                publisher.publish_user_registered(event_data)

            # 6. Tạo JWT
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.email, "user_id": user.id}, 
                expires_delta=access_token_expires
            )

            return {
                "access_token": access_token,
                "token_type": "bearer",
"user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username
                }
            }
        except Exception as e:
            print(f"Social Login Error: {e}")
            raise e
