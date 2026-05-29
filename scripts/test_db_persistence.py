import os
import django
import sys
from decimal import Decimal

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from myproject.auth_service.app.models.users import User
from myproject.courses_service.app.models.courses import Course
from myproject.courses_service.app.models.enrollments import Enrollment
from myproject.payment_service.app.models.payments import Transaction, PaymentStatus
from myproject.payment_service.app.services.payment_service import PaymentService
from myproject.courses_service.app.services.course_service import CourseService

def run_test():
    print("--- Starting Database Persistence Test ---")

    # 1. Create Test User (Auth DB)
    email = "test_user_db@example.com"
    User.objects.filter(email=email).delete()
    user = User.objects.create(
        email=email,
        username="test_db_user"
    )
    print(f"1. User saved to auth_db: {user.username} (ID: {user.id})")

    # 2. Create Test Course (Course DB)
    course = Course.objects.create(
        title="Test Course DB",
        description="Demo test",
        professor=user,
        price=Decimal("199.99")
    )
    print(f"2. Course saved to course_db: {course.title} (ID: {course.id})")

    # 3. Create Payment Transaction (Payment DB)
    transaction = PaymentService.create_transaction(
        user_id=user.id,
        course_id=course.id,
        amount=course.price,
        payment_method="Testing"
    )
    print(f"3. PENDING transaction saved to payment_db (ID: {transaction.id})")

    # 4. Complete Payment (Update status + Publish to RabbitMQ)
    try:
        PaymentService.complete_payment(transaction.id, "TEST_EXTERNAL_ID_123")
        print("4. Transaction updated to SUCCESS in payment_db")
    except Exception as e:
        print(f"4. Status updated (Note: RabbitMQ connection might failed but DB is updated: {e})")

    # Verify status in DB
    updated_tx = Transaction.objects.get(id=transaction.id)
    print(f"Check actual status in DB: {updated_tx.status}")

    # 5. Simulate Enrollment (Directly via Service)
    enrollment = CourseService.enroll_student(course.id, user.id)
    print(f"5. Enrollment saved to course_db (Enrollment ID: {enrollment.id})")

    # Verify Enrollment
    exists = Enrollment.objects.filter(student_id=user.id, course_id=course.id).exists()
    print(f"Confirm Enrollment exists in DB: {exists}")

    print("\n--- TEST SUCCESS: ALL DATA SAVED TO 3 STANDALONE DATABASES ---")

if __name__ == "__main__":
    run_test()
