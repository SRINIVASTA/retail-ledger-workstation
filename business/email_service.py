# business/email_service.py
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import streamlit as st

logger = logging.getLogger("CREDITPULSE_WORKSTATION.EMAIL_SERVICE")

class EnterpriseEmailDispatcher:
    """Handles secure email dispatch with attachments matching your exact secrets format."""
    
    @staticmethod
    def send_audit_report(recipient_email: str, customer_name: str, loan_no: str, pdf_bytes: bytes) -> bool:
        try:
            # 1. Fetch credentials using your nested secret structure
            try:
                email_sender = st.secrets["gmail"]["username"]
                app_password = st.secrets["gmail"]["app_password"]
            except KeyError:
                raise KeyError("Missing Gmail credentials! Ensure [gmail] structure is set in Secrets.")

            # 2. Build structural multi-part container for handling the file attachment
            msg = MIMEMultipart()
            msg['From'] = email_sender
            msg['To'] = recipient_email
            msg['Subject'] = f"Secure Compliance Audit Report — Account: {loan_no}"

            # 3. Construct the dynamic cover body
            body = (
                f"Dear {customer_name},\n\n"
                f"Please find attached your secure CreditPulse Master Compliance Audit Report "
                f"corresponding to Loan Account Number {loan_no}.\n\n"
                f"Sincerely,\n"
                f"CreditPulse Operations Hub"
            )
            msg.attach(MIMEText(body, 'plain'))

            # 4. Stream and encode the PDF binary report payload into standard base64
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(pdf_bytes)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="Audit_Report_{loan_no}.pdf"')
            msg.attach(part)

            # 5. Connect to mail host and deliver the package 
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(email_sender, app_password)
            server.sendmail(email_sender, recipient_email, msg.as_string())
            server.quit()

            logger.info(f"Successfully dispatched asset report to {recipient_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to execute email broadcast to {recipient_email}: {e}")
            raise e
