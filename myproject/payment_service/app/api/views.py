import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from myproject.auth_service.app.utils.auth_middleware import jwt_required
from myproject.payment_service.app.services.payment_service import PaymentService
from myproject.payment_service.app.models.payments import Transaction

@csrf_exempt
@jwt_required
def create_checkout_session_view(request):
    """
    Tạo một phiên thanh toán mới (tương tự như Stripe Checkout hoặc VNPay Redirect)
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        course_id = data.get("course_id")
        payment_method = data.get("payment_method", "VNPay")

        if not course_id:
            return JsonResponse({"error": "course_id is required"}, status=400)

        # Look up course amount from Course model (Course DB)
        from myproject.courses_service.app.models.courses import Course
        try:
            course = Course.objects.get(id=course_id)
            amount = course.price
        except Course.DoesNotExist:
            return JsonResponse({"error": "Course not found"}, status=404)

        # Check if user is already enrolled
        from myproject.courses_service.app.models.enrollments import Enrollment
        if Enrollment.objects.filter(student_id=request.user_id, course_id=course_id).exists():
            return JsonResponse({
                "error": "Bạn đã sở hữu khóa học này rồi. Vui lòng kiểm tra trong 'Khóa học của tôi'."
            }, status=400)

        transaction = PaymentService.create_transaction(
            user_id=request.user_id,
            course_id=course_id,
            amount=amount,
            payment_method=payment_method
        )

        # Simulation URL
        payment_url = f"https://sandbox.vnpayment.vn/payment?order_id={transaction.id}&amount={amount}"

        return JsonResponse({
            "message": "Transaction created",
            "transaction_id": transaction.id,
            "payment_url": payment_url
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
def payment_webhook_view(request):
    """
    Giả lập Callback/Webhook từ cổng thanh toán sau khi người dùng trả tiền xong
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        print(f"DEBUG Webhook: Received data: {data}")
        
        # Accept both transaction_id and order_id for compatibility
        transaction_id = data.get("transaction_id") or data.get("order_id")
        external_id = data.get("vnp_transaction_no", "SIMULATION_12345")
        status = data.get("status")

        if not transaction_id:
            print(f"DEBUG Webhook: Missing transaction_id in {data}")
            return JsonResponse({"error": "transaction_id is required"}, status=400)

        if str(status).upper() == "SUCCESS":
            print(f"DEBUG Webhook: Processing success for transaction {transaction_id}")
            transaction = PaymentService.complete_payment(transaction_id, external_id)
            return JsonResponse({
                "message": "Payment verified and enrollment triggered",
                "status": transaction.status
            })
        else:
            print(f"DEBUG Webhook: Processing failure for transaction {transaction_id}")
            transaction = PaymentService.fail_payment(transaction_id, reason=status or "Cancelled")
            return JsonResponse({
                "message": "Payment failed or cancelled",
                "status": transaction.status
            }, status=400)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
@jwt_required
def list_my_transactions_view(request):
    """
    Lấy lịch sử giao dịch của người dùng hiện tại
    """
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    transactions = Transaction.objects.filter(user_id=request.user_id)
    data = [{
        "id": t.id,
        "course_id": t.course_id,
        "amount": float(t.amount),
        "status": t.status,
        "method": t.payment_method,
        "date": t.created_at.strftime("%Y-%m-%d %H:%M:%S")
    } for t in transactions]
    
    return JsonResponse({"transactions": data})
