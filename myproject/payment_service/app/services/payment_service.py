from myproject.payment_service.app.models.payments import Transaction, PaymentStatus
from myproject.payment_service.app.messaging.publisher import publisher
import logging

logger = logging.getLogger(__name__)

class PaymentService:
    @staticmethod
    def create_transaction(user_id, course_id, amount, payment_method):
        transaction = Transaction.objects.create(
            user_id=user_id,
            course_id=course_id,
            amount=amount,
            payment_method=payment_method,
            status=PaymentStatus.PENDING
        )
        return transaction

    @staticmethod
    def complete_payment(transaction_id, external_id):
        try:
            logger.info(f"Completing payment for transaction ID: {transaction_id}")
            transaction = Transaction.objects.get(pk=transaction_id)
            transaction.status = PaymentStatus.SUCCESS
            
            # Đảm bảo transaction_id là duy nhất (đặc biệt khi giả lập nhiều lần)
            if Transaction.objects.filter(transaction_id=external_id).exclude(pk=transaction_id).exists():
                external_id = f"{external_id}_{transaction_id}"
                
            transaction.transaction_id = external_id
            transaction.save()
            logger.info(f"Transaction {transaction_id} saved successfully as SUCCESS")

            # Publish event to RabbitMQ
            try:
                logger.info("Publishing payment.success event to RabbitMQ...")
                publisher.publish_payment_success(
                    transaction_id=transaction.id,
                    user_id=transaction.user_id,
                    course_id=transaction.course_id,
                    amount=transaction.amount
                )
                logger.info("Event payment.success published successfully")
            except Exception as mq_err:
                logger.error(f"RabbitMQ publishing error (transaction saved): {mq_err}")
                # We don't raise here so the user still gets a success response
            
            return transaction
        except Exception as e:
            logger.critical(f"Critical error in complete_payment: {e}")
            raise e

    @staticmethod
    def fail_payment(transaction_id, reason="Payment cancelled or failed"):
        try:
            logger.info(f"Failing payment for transaction ID: {transaction_id}")
            transaction = Transaction.objects.get(pk=transaction_id)
            transaction.status = PaymentStatus.FAILED
            transaction.save()
            
            # Publish failure event
            try:
                publisher.publish_payment_failed(
                    transaction_id=transaction.id,
                    user_id=transaction.user_id,
                    course_id=transaction.course_id,
                    reason=reason
                )
                logger.info("Event payment.failed published successfully")
            except Exception as mq_err:
                logger.error(f"RabbitMQ error on publishing failure event: {mq_err}")

            return transaction
        except Exception as e:
            logger.error(f"Error in fail_payment: {e}")
            raise e

