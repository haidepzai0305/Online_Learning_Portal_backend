# Hướng Dẫn Sử Dụng Backend & Cấu Hình RabbitMQ

Tài liệu này hướng dẫn cách cài đặt, cấu hình và giải thích luồng hoạt động của hệ thống Online Learning Portal Backend (Auth Service).

---

## 1. Hướng Cẫn Cài Đặt Hệ Thống

### Yêu cầu tiên quyết
- Python 3.10+
- MySQL (hoặc SQLite)
- RabbitMQ Server
- Git

### Các bước cài đặt
1. **Clone project và tạo môi trường ảo**:
   ```bash
   git clone <repository_url>
   cd Online_Learning_Portal_backend
   python -m venv .venv
   source .venv/bin/activate  # Trên Windows: .venv\Scripts\activate
   ```

2. **Cài đặt các thư viện**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Cấu hình môi trường (`.env`)**:
   Tạo file `.env` tại đường dẫn `myproject/auth_service/app/core/.env` với nội dung tương tự mẫu sau:
   ```env
   DB_ENGINE=django.db.backends.mysql
   DB_NAME=auth_db
   DB_USER=root
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=3306

   RABBITMQ_URL=amqp://guest:guest@localhost:5672/
   SECRET_KEY=your_secret_key_here

   # Social Auth (Cần thiết cho đăng nhập Google/Microsoft)
   GOOGLE_CLIENT_ID=your_id
   GOOGLE_CLIENT_SECRET=your_secret
   GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback/google
   ```

4. **Chạy Migration để tạo bảng Database**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Chạy Server**:
   ```bash
   python manage.py runserver
   ```

---

## 2. Thiết Lập RabbitMQ Server

RabbitMQ được sử dụng để xử lý các tác vụ bất đồng bộ (ví dụ: Gửi email chào mừng khi user đăng ký thành công).

### Cách 1: Sử dụng Docker (Khuyên dùng)
```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```
- Port `5672`: Dành cho kết nối ứng dụng (AMQP).
- Port `15672`: Dành cho giao diện quản lý (RabbitMQ Management UI).

### Cách 2: Cài đặt trực tiếp trên Windows
1. Tải và cài đặt **Erlang/OTP** (RabbitMQ chạy trên Erlang).
2. Tải và cài đặt **RabbitMQ Server**.
3. Kích hoạt Management UI qua Command Prompt:
   ```bash
   rabbitmq-plugins enable rabbitmq_management
   ```
4. Truy cập `http://localhost:15672` (Username/Password mặc định: `guest`/`guest`).

### Cách chạy Worker (Consumer)
Để xử lý các tin nhắn từ RabbitMQ, bạn cần chạy worker trong một terminal riêng:
```bash
python myproject/auth_service/app/worker/consumer.py
```

---

## 3. Giải Thích Luồng Hoạt Động (Flow)

### A. Luồng Đăng ký & Đăng nhập truyền thống
1. **Frontend** gửi `email/username/password` tới `/api/auth/register/`.
2. **Backend (AuthService)**:
   - Lưu user vào Database.
   - **RabbitMQ**: Phát một event `user_registered` vào queue.
   - Trả về thông báo thành công cho Frontend.
3. **Worker (Consumer)**: Lắng nghe queue, khi thấy có tin mới sẽ tiến hành xử lý (ví dụ: giả lập gửi email chào mừng).
4. **Login**: Frontend gửi thông tin đăng nhập, Backend kiểm tra và trả về **JWT Access Token**.

### B. Luồng Đăng nhập Social (Google/Microsoft)
1. **Frontend** mở cửa sổ đăng nhập Google/Microsoft. User chọn tài khoản.
2. Google trả về một mã `code` cho Frontend.
3. **Frontend** gửi mã `code` này tới `/api/auth/google-login/` (hoặc microsoft).
4. **Backend**:
   - Gửi `code` tới server Google cấp Access Token của Google.
   - Dùng token Google để lấy thông tin cá nhân (Email, Name).
   - Kiểm tra Database:
     - Nếu user đã tồn tại: Tiến hành login.
     - Nếu chưa: Tạo user mới và gán link social ID.
   - Trả về **JWT Access Token** của hệ thống cho Frontend.

---

## 4. Danh Sách Các Endpoint Chính

| Endpoint | Method | Chức năng | Body chính |
|----------|--------|-----------|------------|
| `/api/auth/register/` | POST | Đăng ký tài khoản mới | `email`, `username`, `password` |
| `/api/auth/login/` | POST | Đăng nhập lấy token | `email`, `password` |
| `/api/auth/me/` | GET | Lấy thông tin user hiện tại | Header: `Authorization: Bearer <token>` |
| `/api/auth/google-login/` | POST | Đăng nhập qua Google | `code` |
| `/api/auth/microsoft-login/` | POST | Đăng nhập qua Microsoft | `code` |

---
*Ghi chú: Luôn đảm bảo RabbitMQ Server đang chạy trước khi thực hiện đăng ký user.*
