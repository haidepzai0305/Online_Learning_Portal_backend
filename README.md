# 🎓 UniLearn - Microservices Learning Portal Backend

Vietnamese version below / Hướng dẫn tiếng Việt ở phía dưới.

---

UniLearn is a high-performance, asynchronous e-learning portal backend designed using a **decoupled Modular Monolith** architecture with Django 6.0.3. It isolates business modules into individual logical microservices, routes operations across 4 distinct MySQL databases using a custom database router, coordinates cross-service transactions asynchronously using RabbitMQ (AMQP via Pika), and provides students with a smart study assistant utilizing Retrieval-Augmented Generation (RAG) powered by Google Gemini APIs.

---

## 🚀 English Guide

### 🛠️ 1. Environment Prerequisite Setup
Make sure you have Python 3.10+, MySQL, and RabbitMQ installed locally. Alternatively, you can use Docker.

1. **Clone the project & Navigate to the backend directory**:
   ```bash
   cd Online_Learning_Portal_backend
   ```
2. **Create and Activate a virtual environment**:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/MacOS:
   source .venv/bin/activate
   ```
3. **Install all required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Environment Variables**:
   Copy `.env.example` in `myproject/auth_service/app/core/` to `.env` and fill in your database and API credentials:
   ```bash
   # Add your Google Gemini API Key for RAG functionality
   AI_API_KEY=your_gemini_api_key_here
   DB_ROOT_PASSWORD=your_mysql_password
   DB_HOST=localhost
   RABBITMQ_URL=amqp://guest:guest@localhost:5672/
   ```

### 💾 2. Multi-Database Setup & Restoration
UniLearn isolates service contexts using 4 separate databases:
* `auth_db` — Holds user accounts and security contexts.
* `course_db` — Tracks courses, materials, and student enrollments.
* `payment_db` — Stores simulated billing transactions.
* `notification_db` — Logs user notification history.

**Database Schema Restoration (Local Setup)**:
Open MySQL command prompt or terminal and restore the backup SQL templates located in `database/backups/`:
```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS auth_db; CREATE DATABASE IF NOT EXISTS course_db; CREATE DATABASE IF NOT EXISTS payment_db; CREATE DATABASE IF NOT EXISTS notification_db;"

mysql -u root -p auth_db < database/backups/auth_db_backup.sql
mysql -u root -p course_db < database/backups/course_db_backup.sql
mysql -u root -p payment_db < database/backups/payment_db_backup.sql
mysql -u root -p notification_db < database/backups/notification_db_backup.sql
```

### 🏃‍♂️ 3. Running the Application
To run the system locally, you **MUST** run the web gateway and both background subscriber workers concurrently.

1. **Start the Main Gateway Web Server** (Terminal 1):
   ```bash
   python manage.py runserver
   # Gateway launches at http://localhost:8000
   ```
2. **Start the Notification Consumer Worker** (Terminal 2):
   ```bash
   # Set PYTHONPATH so python understands app import contexts
   # Windows PowerShell:
   $env:PYTHONPATH="." ; python myproject/notification_service/app/messaging/consumer.py
   # Linux/MacOS:
   PYTHONPATH=. python myproject/notification_service/app/messaging/consumer.py
   ```
3. **Start the Course Enrollment Consumer Worker** (Terminal 3):
   ```bash
   # Windows PowerShell:
   $env:PYTHONPATH="." ; python myproject/courses_service/app/messaging/consumer.py
   # Linux/MacOS:
   PYTHONPATH=. python myproject/courses_service/app/messaging/consumer.py
   ```

### 🧠 4. AI RAG Slide Vector Indexing
To index materials (PDF, video transcripts, slide files) into the vector matrix:
1. Make sure `AI_API_KEY` is loaded.
2. Run the indexing batch script:
   ```bash
   python scripts/index_materials.py
   ```
3. Verify vector cosine search results using:
   ```bash
   python scripts/check_materials.py
   ```

---

## 🇻🇳 Hướng Dẫn Tiếng Việt

UniLearn là hệ thống Học trực tuyến hiệu năng cao, được thiết kế theo mô hình **Modular Monolith** phân rã trên nền tảng Django 6.0.3. Hệ thống cô lập 5 dịch vụ lõi, chia tách hoạt động trên 4 cơ sở dữ liệu MySQL độc lập (thông qua bộ định tuyến `db_router.py`), phối hợp xử lý thanh toán bất đồng bộ qua RabbitMQ (thông qua Pika) và tích hợp trợ lý AI học tập thông minh (RAG) sử dụng Google Gemini.

### 🛠️ 1. Cài đặt Thư viện và Môi trường
Yêu cầu máy cài sẵn Python 3.10+, MySQL Server và RabbitMQ Server.

1. **Mở Terminal tại thư mục gốc backend**:
   ```bash
   cd Online_Learning_Portal_backend
   ```
2. **Khởi tạo và Kích hoạt môi trường ảo**:
   ```bash
   python -m venv .venv
   # Windows (PowerShell):
   .venv\Scripts\activate
   # Linux/MacOS:
   source .venv/bin/activate
   ```
3. **Cài đặt các thư viện phụ thuộc**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Cấu hình biến môi trường**:
   Sao chép file mẫu `.env.example` trong thư mục `myproject/auth_service/app/core/` đổi tên thành `.env` và điền key AI của bạn cùng mật khẩu MySQL:
   ```bash
   AI_API_KEY=key_api_gemini_cua_ban
   DB_ROOT_PASSWORD=mat_khau_mysql_cua_ban
   DB_HOST=localhost
   RABBITMQ_URL=amqp://guest:guest@localhost:5672/
   ```

### 💾 2. Khởi tạo và Phục hồi Cơ sở Dữ liệu (MySQL)
Hệ thống sử dụng bộ router cô lập 4 database độc lập. Thực hiện tạo database và nạp dữ liệu mẫu từ các file backup trong `database/backups/`:

```powershell
# Tạo database mới nếu chưa có
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS auth_db; CREATE DATABASE IF NOT EXISTS course_db; CREATE DATABASE IF NOT EXISTS payment_db; CREATE DATABASE IF NOT EXISTS notification_db;"

# Nạp backup dữ liệu mẫu
mysql -u root -p auth_db < database/backups/auth_db_backup.sql
mysql -u root -p course_db < database/backups/course_db_backup.sql
mysql -u root -p payment_db < database/backups/payment_db_backup.sql
mysql -u root -p notification_db < database/backups/notification_db_backup.sql
```

### 🏃‍♂️ 3. Khởi chạy Hệ thống (Chạy Thủ Công)
Để hệ thống vận hành trọn vẹn và xử lý ghi danh/thông báo, bạn **BẮT BUỘC** phải chạy cổng API chính và 2 tiến trình worker ngầm đồng thời:

1.  **Chạy API Server chính** (Terminal 1):
    ```bash
    python manage.py runserver
    # Server chạy tại http://localhost:8000
    ```
2.  **Chạy Notification Worker** (Terminal 2):
    ```bash
    # Windows PowerShell:
    $env:PYTHONPATH="." ; python myproject/notification_service/app/messaging/consumer.py
    # Linux/MacOS:
    PYTHONPATH=. python myproject/notification_service/app/messaging/consumer.py
    ```
3.  **Chạy Course Enrollment Worker** (Terminal 3):
    ```bash
    # Windows PowerShell:
    $env:PYTHONPATH="." ; python myproject/courses_service/app/messaging/consumer.py
    # Linux/MacOS:
    PYTHONPATH=. python myproject/courses_service/app/messaging/consumer.py
    ```

---

## 🐳 Docker Quick Start (Khởi chạy bằng Docker)

Nếu đã cài đặt Docker Desktop, bạn có thể khởi chạy toàn bộ môi trường (gồm 4 Databases, RabbitMQ, Web Server và 2 Workers) chỉ bằng một lệnh duy nhất:

```bash
docker compose up --build -d
```
*   **Backend URL**: `http://localhost:8000`
*   **RabbitMQ Management Console**: `http://localhost:15672` (User: `guest`, Pass: `guest`)