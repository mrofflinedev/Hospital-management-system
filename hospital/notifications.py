from django.core.mail import send_mail
from django.conf import settings


def send_patient_notification(patient_profile, subject, message_body):
    user = patient_profile.user
    recipient_email = user.email
    phone = user.phone_number

    full_message = (
        f"Dear {user.get_full_name() or user.username},\n\n"
        f"{message_body}\n\n"
        f"Warm regards,\n"
        f"AYUNDA HEALTH CENTER\n"
        f"Homa Bay Town, Kenya | Emergency Desk: +254796943289"
    )

    # 1. Send Email Notification
    if recipient_email:
        try:
            send_mail(
                subject=f"[AYUNDA HEALTH CENTER] {subject}",
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=True,
            )
        except Exception:
            pass

    # 2. SMS Hook (Logs to console; ready for Africa's Talking / Twilio API)
    if phone:
        print(f"[SMS TO {phone}]: {subject} - {message_body}")
