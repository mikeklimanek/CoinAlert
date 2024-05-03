# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
import dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
dotenv.load_dotenv()
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

message = Mail(
    from_email='mike.klimanek@gmail.com',
    to_emails='mike.klimanek@gmail.com',
    subject='CoinAlert Setup',
    html_content='<strong>CoinAlert setup under construction</strong>')
try:
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e.message)