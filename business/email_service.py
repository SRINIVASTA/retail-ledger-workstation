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
    """Handles production-grade secure email dispatch with dynamic binary attachments."""
    
    @staticmethod
    def send_audit_report(recipient_email: str, customer_name: str, loan_no: str, pdf_bytes: bytes) -> bool:
        """
        Packages and dispatches a compliance PDF report to a specified customer.
        Fetches credentials safely from Streamlit's enterprise secrets engine.
        """
        try:
            # 1. Fetch encrypted pipeline configurations from st.secrets
            SMTP_SERVER = st.secrets.get("SMTP_SERVER", "://gmail.com")
            SMTP_PORT = int(st.secrets.get("SMTP_PORT", 587))
            SENDER_EMAIL = st.secrets.get("SENDER_EMAIL", "alerts@yourbank.com")
            SENDER_PASSWORD = st.secrets.get("SENDER_PASSWORD", "")

            if not SENDER_PASSWORD:
                raise ValueError("SMTP authentication credentials missing in workspace secrets.")

            # 2. Build the structural multi-part container
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = recipient_email
            msg['Subject'] = f"Secure Compliance Audit Report — Account: {loan_no}"

            # 3. Construct professional cover message
            body = (
                f"Dear {customer_name},\n\n"
                f"Please find attached your secure CreditPulse Master Compliance Audit Report "
                f"corresponding to Loan Account Number {loan_no}.\n\n"
                f"This is an automated operational system update. Please do not reply directly to this thread.\n\n"
                f"Sincerely,\n"
                f"CreditPulse Operations Hub"
            )
            msg.attach(MIMEText(body, 'plain'))

            # 4. Stream and encode the PDF binary payload into standard base64 attachment block
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(pdf_bytes)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="Audit_Report_{loan_no}.pdf"')
            msg.attach(part)

            # 5. Connect via secure TLS encryption pipeline and deliver
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
            server.quit()

            logger.info(f"Successfully dispatched compliance asset to {recipient_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to execute enterprise email broadcast to {recipient_email}: {e}")
            raise e
