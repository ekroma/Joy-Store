from email.mime.text import MIMEText
import smtplib
import asyncio
from config.settings import settings
from apps.task_management.celery_app import celery


@celery.task
def send_email_to_activate_task(email, subject, activation_code, html=False):
    subject = "Перейдите по ссылке для активации аккаунта"
    html_content = f"<html><body><p> Ваш код для верификации аккаyнта {activation_code}"

    asyncio.run(send_email(email, subject, html_content, html))

@celery.task
def send_email_to_restore_task(email, subject, activation_code, html=False):
    subject = "Ссылка для восстановления пароля"
    html_content = f"<html><body><p>Для восстановления пароля перейдите по <a href='{settings.BASE_URL}/auth/restore_password/{email}/{activation_code}'>ссылке</a>.</p></body></html>"

    asyncio.run(send_email(email, subject, html_content, html=True))


async def send_email(email, subject, body, html=False):
    sender_email = "evelbrus55@gmail.com"
    sender_password = "gtpmdktmcdrxhudt"
    recipient_email = email

    message = MIMEText(body, 'html' if html else 'plain')
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())

    except smtplib.SMTPAuthenticationError:
        print("Ошибка аутентификации. Проверьте свой пароль для приложений.")
    except Exception as e:
        print(f"Произошла ошибка при отправке электронной почты: {e}")
    finally:
        server.quit()
