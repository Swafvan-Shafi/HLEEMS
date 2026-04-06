import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def send_late_warning_email(student_email, student_name, late_count):
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT', 587)
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')
    
    if not smtp_server or not smtp_user or not smtp_pass:
        print("[Mailer] SMTP credentials not fully configured in .env. Skipping email dispatch.")
        return False

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = student_email
    msg['Subject'] = "Warning: Multiple Late Entries Detected"
    
    body = f"""Hello {student_name},

This is an automated administrative notification from the Hostel Late Entry and Exit Management System.

Our records indicate that you have accumulated {late_count} Late Entries against your hostel log. 
Registering multiple late entries beyond the threshold is highly discouraged and violates standard operational policies.

Please ensure you adhere strictly to expected entry parameters moving forward. Continued violations may result in escalated administrative action.

Regards,
Systems Administration
HLEEMS
"""
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(smtp_server, int(smtp_port))
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        print(f"[Mailer] Successfully dispatched Late Warning email to {student_email}!")
        return True
    except Exception as e:
        print(f"[Mailer] Failed to send email to {student_email}: {str(e)}")
        return False
