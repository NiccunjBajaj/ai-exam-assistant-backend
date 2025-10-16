# utils/email_utils.py
import mailchimp_transactional as MailchimpTransactional
import os

MAILCHIMP_API_KEY = os.getenv("MAILCHIMP_API_KEY")
FROM_EMAIL = os.getenv("MAILCHIMP_FROM_EMAIL", "no-reply@learnee.space")
REPLY_TO_EMAIL = os.getenv("REPLY_TO_EMAIL", "support@learnee.space")
FROM_NAME = os.getenv("MAILCHIMP_FROM_NAME", "Learnee")

client = MailchimpTransactional.Client(MAILCHIMP_API_KEY)


def send_verification_email(to_email: str, username: str, verify_link: str):
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #161616;">
        <h2>Welcome to Learnee, {username}!</h2>
        <p>Click the button below to verify your email address:</p>
        <a href="{verify_link}" 
           style="background-color:#ffe243;color:#161616;padding:10px 20px;
                  text-decoration:none;border-radius:8px;font-weight:bold;">
          Verify Email
        </a>
        <p style="margin-top:20px;">If that doesn't work, copy-paste this link:</p>
        <p>{verify_link}</p>
        <br>
        <p>— The Learnee Team 🐝</p>
      </body>
    </html>
    """

    message = {
        "from_email": FROM_EMAIL,
        "from_name": "Learnee",
        "to": [{"email": to_email}],
        "subject": "Verify your email",
        "html": html_content,
        "headers": {"Reply-To": REPLY_TO_EMAIL}
    }

    try:
        client.messages.send({"message": message})
    except Exception as e:
        print("Mailchimp send error:", e)

def send_reset_password_email(to_email: str, username: str, reset_link: str):
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #161616;">
        <h2>Hello {username},</h2>
        <p>Click below to reset your password:</p>
        <a href="{reset_link}" 
           style="background-color:#ffe243;color:#161616;padding:10px 20px;
                  text-decoration:none;border-radius:8px;font-weight:bold;">
          Reset Password
        </a>
        <p>If the button doesn't work, copy this link:</p>
        <p>{reset_link}</p>
        <br>
        <p>— Learnee Team 🐝</p>
      </body>
    </html>
    """
    message = {
        "from_email": FROM_EMAIL,
        "from_name": FROM_NAME,
        "to": [{"email": to_email}],
        "subject": "Reset your password",
        "html": html_content,
        "headers": {"Reply-To": REPLY_TO_EMAIL}
    }
    try:
        client.messages.send({"message": message})
    except Exception as e:
        print("Mailchimp send error:", e)

