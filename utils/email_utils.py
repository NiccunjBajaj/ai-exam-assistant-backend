# utils/email_utils.py
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

# Environment variables (configure in your .env)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")  # e.g., no-reply@learnee.space or your Gmail
SMTP_PASS = os.getenv("SMTP_PASS")  # app password or normal password
FROM_NAME = os.getenv("SMTP_FROM_NAME", "Learnee")
FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USER)
REPLY_TO_EMAIL = os.getenv("SMTP_REPLY_TO", "support@learnee.space")


def _send_email(to_email: str, subject: str, html_content: str):
    """Low-level helper that sends email via SMTP."""
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = formataddr((FROM_NAME, FROM_EMAIL))
        msg["To"] = to_email
        msg["Subject"] = subject
        msg["Reply-To"] = REPLY_TO_EMAIL

        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(FROM_EMAIL, to_email, msg.as_string())
            print(f"✅ Email sent successfully to {to_email}")

    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")


def send_verification_email(to_email: str, username: str, verify_link: str):
    """Send email verification link."""
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #00141b;">
        <h2>Welcome to Learnee, {username}!</h2>
        <p>Click the button below to verify your email address:</p>
        <a href="{verify_link}"
           style="background-color:#ffe655;color:#00141b;padding:10px 20px;
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
    _send_email(to_email, "Verify your Learnee email", html_content)


def send_reset_password_email(to_email: str, username: str, reset_link: str):
    """Send password reset link."""
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #00141b;">
        <h2>Hello {username},</h2>
        <p>Click below to reset your password:</p>
        <a href="{reset_link}"
           style="background-color:#fefe655;color:#00141b;padding:10px 20px;
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
    _send_email(to_email, "Reset your Learnee password", html_content)