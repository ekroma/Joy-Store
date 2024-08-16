from fastapi import UploadFile
import os
from email.mime.text import MIMEText
import smtplib, asyncio
from config.settings import settings
from backend.src.apps.task_management.celery_app import celery




async def save_user_upload_file(upload_file: UploadFile, user):
    file_name = upload_file.filename
    user_directory = os.path.join("/var/www/user_files/", user.email)
    file_path = os.path.join(user_directory, file_name) # type: ignore

    os.makedirs(user_directory, exist_ok=True)

    with open(file_path, "wb") as buffer:
        data = await upload_file.read()
        buffer.write(data)
    await upload_file.close()
    if settings.BASE_URL:
        file_path = file_name
    return file_path



@celery.task
def send_email_task(email, subject, activation_code, html=False):
    subject = "Перейдите по ссылке для активации аккаунта"
    html_content = f"<html><body><p>Для активации аккаунта перейдите по <a href='{settings.BASE_URL}/auth/activate_account/{email}/{activation_code}'>ссылке</a>.</p></body></html>"

    asyncio.run(send_email(email, subject, html_content, html=True))

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

    server = None
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())
        print("Email успешно отправлен!")

    except smtplib.SMTPAuthenticationError:
        print("Ошибка аутентификации. Проверьте свой пароль для приложений.")
    except Exception as e:
        print(f"Произошла ошибка при отправке электронной почты: {e}")
    finally:
        if server:
            server.quit()
