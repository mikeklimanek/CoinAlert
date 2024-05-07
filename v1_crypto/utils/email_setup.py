import os
import dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

dotenv.load_dotenv('CoinAlert/v1_crypto/.env')
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

def send_email(subject, html_content, to_emails='mike.klimanek@gmail.com', from_email='mike.klimanek@gmail.com'):
    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        html_content=html_content
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print("Email sent successfully!")
        print("Status Code:", response.status_code)
        print("Response Body:", response.body)
        print("Response Headers:", response.headers)
    except Exception as e:
        print("Error sending email:", str(e))
