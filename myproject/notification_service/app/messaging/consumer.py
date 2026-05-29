import json
import pika
import os
import django
from dotenv import load_dotenv

# Setup Django environment before importing models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from myproject.notification_service.app.services.notification_service import NotificationService
from myproject.courses_service.app.models.enrollments import Enrollment

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        routing_key = method.routing_key
        payload = data.get("payload", data) # Fallback to data itself if payload not present
        
        print(f" [x] Notification Service received {routing_key}")

        if routing_key == "assignment.posted":
            course_id = payload.get("course_id")
            title = payload.get("title")
            # Notify all students in this course
            student_ids = Enrollment.objects.filter(course_id=course_id).values_list('student_id', flat=True)
            for s_id in student_ids:
                NotificationService.create_notification(
                    user_id=s_id,
                    title="New Assignment",
                    message=f"A new assignment '{title}' has been posted in your course."
                )

        elif routing_key == "submission.graded":
            student_id = payload.get("student_id")
            score = payload.get("score")
            NotificationService.create_notification(
                user_id=student_id,
                title="Assignment Graded",
                message=f"Your assignment has been graded. Your score is {score}."
            )

        elif routing_key == "announcement.posted":
            course_id = payload.get("course_id")
            title = payload.get("title")
            student_ids = Enrollment.objects.filter(course_id=course_id).values_list('student_id', flat=True)
            for s_id in student_ids:
                NotificationService.create_notification(
                    user_id=s_id,
                    title="New Announcement",
                    message=f"Important announcement: {title}"
                )

        elif routing_key == "payment.success":
            user_id = payload.get("user_id")
            course_id = payload.get("course_id")
            
            # Fetch course title from Course service
            from myproject.courses_service.app.models.courses import Course
            try:
                course = Course.objects.get(id=course_id)
                course_title = course.title
            except Course.DoesNotExist:
                course_title = "Course"

            NotificationService.create_notification(
                user_id=user_id,
                title="Thanh toán thành công 💳",
                message=f"Chúc mừng! Bạn đã đăng ký thành công khóa học '{course_title}'."
            )

        elif routing_key == "payment.failed":
            user_id = payload.get("user_id")
            course_id = payload.get("course_id")
            reason = payload.get("reason", "Unknown error")
            
            from myproject.courses_service.app.models.courses import Course
            try:
                course = Course.objects.get(id=course_id)
                course_title = course.title
            except Course.DoesNotExist:
                course_title = "Course"

            NotificationService.create_notification(
                user_id=user_id,
                title="Thanh toán thất bại ❌",
                message=f"Rất tiếc! Giao dịch cho khóa học '{course_title}' không thành công. Lý do: {reason}."
            )

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f" [!] Notification processing error: {e}")

def main():
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    # Declare the exchange (topic for flexible routing)
    channel.exchange_declare(exchange='unilearn_events', exchange_type='topic', durable=True)
    
    # Create a temporary queue for this service
    result = channel.queue_declare(queue='notification_service_queue', durable=True)
    queue_name = result.method.queue
    
    # Bind the queue to the exchange - Receive all events
    channel.queue_bind(exchange='unilearn_events', queue=queue_name, routing_key='#')

    print(' [*] Notification Service waiting for events. To exit press CTRL+C')
    channel.basic_consume(queue=queue_name, on_message_callback=callback)

    channel.start_consuming()

if __name__ == '__main__':
    main()
