# payments/services.py
import uuid
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from .models import Payment as PaymentModel, Invoice, Refund
from accounts.models import User
from courses.models import Course, Group
import logging

logger = logging.getLogger(__name__)

# Проверка наличия настроек YooKassa
try:
    import yookassa
    from yookassa import Configuration, Payment
    from yookassa.domain.models import Amount, Receipt, ReceiptItem
    from yookassa.domain.request import PaymentRequest
    
    # Настройка YooKassa если есть настройки
    if hasattr(settings, 'YOOKASSA_SHOP_ID') and hasattr(settings, 'YOOKASSA_SECRET_KEY'):
        Configuration.account_id = settings.YOOKASSA_SHOP_ID
        Configuration.secret_key = settings.YOOKASSA_SECRET_KEY
        YOOKASSA_CONFIGURED = True
    else:
        YOOKASSA_CONFIGURED = False
        logger.warning("YooKassa не настроена - отсутствуют настройки")
        
except ImportError:
    YOOKASSA_CONFIGURED = False
    logger.warning("YooKassa не установлена - pip install yookassa")
    yookassa = None
    Configuration = None
    Payment = None
    Amount = None
    Receipt = None
    ReceiptItem = None
    PaymentRequest = None

class PaymentService:
    """Сервис для обработки платежей"""
    
    @staticmethod
    def create_payment(student, course, amount, currency='RUB', description='', return_url=None):
        """Создание платежа через YooKassa"""
        try:
            # Генерируем уникальный ID для платежа
            payment_id = str(uuid.uuid4())
            
            # Если YooKassa настроена, создаем платеж через нее
            if YOOKASSA_CONFIGURED and yookassa:
                # Создаем платеж в YooKassa
                payment_data = PaymentRequest({
                    "amount": {
                        "value": str(amount),
                        "currency": currency
                    },
                    "confirmation": {
                        "type": "redirect",
                        "return_url": return_url or settings.YOOKASSA_RETURN_URL
                    },
                    "capture": True,
                    "description": description or f"Оплата курса: {course.title}",
                    "metadata": {
                        "payment_id": payment_id,
                        "student_id": student.id,
                        "course_id": course.id if course else "",
                    },
                    "receipt": {
                        "customer": {
                            "email": student.email
                        },
                        "items": [
                            {
                                "description": course.title if course else "Оплата обучения",
                                "quantity": "1.00",
                                "amount": {
                                    "value": str(amount),
                                    "currency": currency
                                },
                                "vat_code": "1"  # Без НДС
                            }
                        ]
                    }
                })
                
                # Отправляем запрос в YooKassa
                yookassa_payment = Payment.create(payment_data)
                
                # Создаем платеж в нашей системе
                payment = PaymentModel.objects.create(
                    student=student,
                    course=course,
                    amount=amount,
                    currency=currency,
                    status='pending',
                    transaction_id=yookassa_payment.id,
                    description=description,
                    payment_method='yookassa',
                    external_payment_id=payment_id
                )
                
                return {
                    'success': True,
                    'payment_url': yookassa_payment.confirmation.confirmation_url,
                    'payment_id': payment.id,
                    'external_payment_id': payment_id,
                    'yookassa_payment_id': yookassa_payment.id
                }
            else:
                # Если YooKassa не настроена, создаем тестовый платеж
                payment = PaymentModel.objects.create(
                    student=student,
                    course=course,
                    amount=amount,
                    currency=currency,
                    status='pending',
                    transaction_id=f"test_{payment_id}",
                    description=description,
                    payment_method='test',
                    external_payment_id=payment_id
                )
                
                # Для тестирования возвращаем URL на локальный сервер
                test_payment_url = f"http://localhost:8000/api/payments/test-payment/{payment.id}/"
                
                return {
                    'success': True,
                    'payment_url': test_payment_url,
                    'payment_id': payment.id,
                    'external_payment_id': payment_id,
                    'message': 'Тестовый платеж (YooKassa не настроена)'
                }
                
        except Exception as e:
            logger.error(f"Ошибка создания платежа: {str(e)}")
            return {
                'success': False,
                'error': f"Ошибка создания платежа: {str(e)}"
            }
    
    @staticmethod
    def confirm_payment(payment_id):
        """Подтверждение платежа через webhook от YooKassa"""
        try:
            payment = PaymentModel.objects.get(id=payment_id)
            
            # Если это тестовый платеж, подтверждаем сразу
            if payment.payment_method == 'test':
                payment.status = 'paid'
                payment.paid_at = timezone.now()
                payment.save()
                
                # Создаем подписку/запись на курс
                PaymentService._enroll_student_in_course(payment)
                
                # Создаем счет
                PaymentService._create_invoice(payment)
                
                return {'success': True, 'message': 'Тестовый платеж подтвержден'}
            
            # Если YooKassa настроена, проверяем статус платежа
            elif YOOKASSA_CONFIGURED and yookassa:
                # Получаем информацию о платеже из YooKassa
                yookassa_payment = Payment.find_one(payment.transaction_id)
                
                if yookassa_payment.status == 'succeeded':
                    payment.status = 'paid'
                    payment.paid_at = timezone.now()
                    payment.transaction_id = yookassa_payment.id
                    payment.save()
                    
                    # Создаем подписку/запись на курс
                    PaymentService._enroll_student_in_course(payment)
                    
                    # Создаем счет
                    PaymentService._create_invoice(payment)
                    
                    return {'success': True}
                elif yookassa_payment.status == 'canceled':
                    payment.status = 'failed'
                    payment.save()
                    return {
                        'success': True,
                        'message': 'Платеж отменен'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Платеж не был успешно обработан. Статус: {yookassa_payment.status}'
                    }
            else:
                return {
                    'success': False,
                    'error': 'Платежная система не настроена'
                }
                
        except PaymentModel.DoesNotExist:
            return {
                'success': False,
                'error': 'Платеж не найден'
            }
        except Exception as e:
            logger.error(f"Ошибка подтверждения платежа: {str(e)}")
            return {
                'success': False,
                'error': f"Ошибка подтверждения платежа: {str(e)}"
            }
    
    @staticmethod
    def _enroll_student_in_course(payment):
        """Зачисление студента на курс после оплаты"""
        try:
            if payment.course and payment.student:
                # Получаем группу по умолчанию для курса
                group = Group.objects.filter(
                    course=payment.course,
                    is_active=True
                ).first()
                
                if group:
                    # Добавляем студента в группу
                    group.students.add(payment.student)
                    logger.info(f"Студент {payment.student.username} зачислен в группу {group.title}")
                
                # Создаем подписку (если нужна)
                # Здесь можно добавить логику подписки
                
            return True
            
        except Exception as e:
            logger.error(f"Ошибка зачисления студента на курс: {str(e)}")
            return False
    
    @staticmethod
    def _create_invoice(payment):
        """Создание счета для платежа"""
        try:
            invoice_number = f"INV-{timezone.now().strftime('%Y%m%d')}-{payment.id}"
            
            invoice = Invoice.objects.create(
                student=payment.student,
                payment=payment,
                amount=payment.amount,
                currency=payment.currency,
                due_date=timezone.now().date(),
                status='paid',
                invoice_number=invoice_number,
                description=payment.description,
                paid_at=payment.paid_at
            )
            
            logger.info(f"Создан счет: {invoice.invoice_number}")
            return invoice
            
        except Exception as e:
            logger.error(f"Ошибка создания счета: {str(e)}")
            return None

# === ТЕСТОВЫЕ ФУНКЦИИ ===

def format_amount_for_payment(amount):
    """Форматирование суммы для платежной системы"""
    return f"{amount:.2f}"

def validate_payment_data(student, course, amount):
    """Валидация данных платежа"""
    errors = []
    
    if not student:
        errors.append("Студент обязателен")
    
    if not course:
        errors.append("Курс обязателен")
    
    if amount <= 0:
        errors.append("Сумма должна быть больше 0")
    
    if amount > 100000:  # Ограничение на максимальную сумму
        errors.append("Сумма слишком велика")
    
    return errors

def send_payment_confirmation_email(payment):
    """Отправка email подтверждения оплаты"""
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        if payment.student.email:
            subject = f"Подтверждение оплаты курса: {payment.course.title}"
            message = f"""
            Здравствуйте, {payment.student.get_full_name() or payment.student.username}!
            
            Спасибо за оплату курса "{payment.course.title}".
            
            Детали платежа:
            - Сумма: {payment.amount} {payment.currency}
            - Дата оплаты: {payment.paid_at.strftime('%d.%m.%Y %H:%M')}
            - Номер платежа: {payment.transaction_id}
            
            Вы успешно зачислены на курс. Доступ к занятиям открыт.
            
            С уважением,
            Онлайн-школа
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [payment.student.email],
                fail_silently=True,
            )
            
            logger.info(f"Отправлено email подтверждения оплаты: {payment.student.email}")
            
    except Exception as e:
        logger.error(f"Ошибка отправки email подтверждения оплаты: {str(e)}")

def send_payment_failure_email(payment, error_message):
    """Отправка email о неудачной оплате"""
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        if payment.student.email:
            subject = f"Ошибка оплаты курса: {payment.course.title}"
            message = f"""
            Здравствуйте, {payment.student.get_full_name() or payment.student.username}!
            
            К сожалению, произошла ошибка при оплате курса "{payment.course.title}".
            
            Ошибка: {error_message}
            
            Пожалуйста, попробуйте повторить оплату или свяжитесь с поддержкой.
            
            С уважением,
            Онлайн-школа
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [payment.student.email],
                fail_silently=True,
            )
            
            logger.info(f"Отправлено email об ошибке оплаты: {payment.student.email}")
            
    except Exception as e:
        logger.error(f"Ошибка отправки email об ошибке оплаты: {str(e)}")