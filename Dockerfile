# Sử dụng Python image chính thức, bản slim để nhẹ và nhanh
FROM python:3.11-slim

# Thiết lập các biến môi trường để Python không tạo file .pyc và không buffer log
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Cài đặt các thư viện hệ thống cần thiết cho MySQL (pymysql/mysqlclient) và RabbitMQ
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements và cài đặt thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Copy toàn bộ mã nguồn vào thư mục làm việc
COPY . .

# Phân quyền cho script khởi chạy (nếu có)
# RUN chmod +x /app/entrypoint.sh

# Mở cổng 8000 cho Django server
EXPOSE 8000

# Lệnh khởi chạy mặc định (có thể bị ghi đè bởi docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
