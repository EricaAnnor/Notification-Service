import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from .config import Settings

settings = Settings()

grid_key = settings.sendgridapikey

sg = sendgrid.SendGridAPIClient(api_key=grid_key)

def emailservice(sender, receiver, title, body):
    message = Mail(
        from_email=Email(sender),
        to_emails=To(receiver),
        subject=title,
        plain_text_content=Content("text/plain", body)
    )

    try:
        response = sg.client.mail.send.post(request_body=message.get())
        return response.status_code
    except Exception as e:
        print(f"SendGrid Error: {e}")
        return 500  
