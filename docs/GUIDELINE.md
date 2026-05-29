# HƯỚNG DẪN CÀI ĐẶT VÀ CHẠY HỆ THỐNG (SETUP GUIDE)

Chào mừng bạn đến với hệ thống **UniLearn - Microservices Learning Portal**. Dưới đây là các bước để bạn có thể chạy dự án này trên máy tính cá nhân hoặc máy chủ khác.

---

## 🚀 CÁCH 1: SỬ DỤNG DOCKER (KHUYÊN DÙNG)

Đây là cách nhanh nhất và ổn định nhất vì Docker đã đóng gói sẵn mọi thứ (Database, RabbitMQ, Services).

### 1. Yêu cầu hệ thống:
*   Đã cài đặt **Docker Desktop** (Tải tại [docker.com](https://www.docker.com/products/docker-desktop/)).

### 2. Các bước khởi chạy:
1.  Mở Terminal tại thư mục gốc của dự án.
2.  Chạy lệnh:
    ```bash
    docker compose up --build -d
    ```
3.  Hệ thống sẽ tự động khởi động:
    *   **Backend:** http://localhost:8000
    *   **Management RabbitMQ:** http://localhost:15672 (User: guest, Pass: guest)

---

## 🛠️ CÁCH 2: CHẠY THỦ CÔNG (LOCAL SETUP)

Nếu bạn không sử dụng Docker, hãy thực hiện các bước sau:

### 1. Chuẩn bị:
*   Python 3.10+, Node.js 16+.
*   MySQL Server đã cài đặt và đang chạy.
*   RabbitMQ Server đã cài đặt và đang chạy.

### 2. Thiết lập Backend:
1.  Vào thư mục `Online_Learning_Portal_backend`.
2.  Cài đặt thư viện:
    ```bash
    pip install -r requirements.txt
    ```
3.  Đảm bảo các file `.env` trong `myproject/auth_service/app/core/` đã đúng thông tin Database.
4.  Khởi chạy Server chính:
    ```bash
    python manage.py runserver
    ```

### 3. CHẠY CÁC WORKER (QUAN TRỌNG):
Mở 2 Terminal riêng biệt và chạy các lệnh sau (nhớ thêm `PYTHONPATH=.` hoặc gán biến môi trường `PYTHONPATH` thành thư mục gốc dự án):
*   **Notification Worker:** `python myproject/notification_service/app/messaging/consumer.py`
*   **Course Worker:** `python myproject/courses_service/app/messaging/consumer.py`

---

## 💾 PHỤC HỒI DỮ LIỆU (DATABASE RESTORE)

Nếu bạn muốn nạp lại dữ liệu cũ từ máy khác sang máy mới, hãy sử dụng các file trong thư mục `database/backups/`:

Gõ lệnh trong CMD/PowerShell (thay `root` và `password` bằng tài khoản MySQL của bạn):

```powershell
# Nạp dữ liệu Auth (Tài khoản)
mysql -u root -p auth_db < database/backups/auth_db_backup.sql

# Nạp dữ liệu Course (Khóa học)
mysql -u root -p course_db < database/backups/course_db_backup.sql

# Nạp dữ liệu Payment (Thanh toán)
mysql -u root -p payment_db < database/backups/payment_db_backup.sql

# Nạp dữ liệu Notification (Thông báo)
mysql -u root -p notification_db < database/backups/notification_db_backup.sql
```

---

## 🌐 THIẾT LẬP FRONTEND (REACT)

1.  Vào thư mục `Online_Learning_Portal_frontend`.
2.  Cài đặt thư viện: `npm install`.
3.  Chạy dự án: `npm run dev`.
4.  Truy cập: http://localhost:5173

---

## 💡 CÁC LƯU Ý KHI TEST:
*   **Đăng nhập:** Sử dụng tài khoản `student@example.com` / `password123`.
*   **Thanh toán:** Khi nhấn "Xác nhận đã thanh toán", hệ thống sẽ tự động gọi Webhook để mở khóa học và bắn thông báo.
*   **Kiểm tra:** Nếu không thấy thông báo, hãy kiểm tra lại xem **Notification Worker** đã chạy chưa.

---
*Chúc bạn có trải nghiệm tuyệt vời với UniLearn!*
