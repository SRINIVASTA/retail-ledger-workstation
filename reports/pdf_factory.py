import os
import smtplib
import csv
from io import StringIO
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Import your custom PDF factory class (assuming it's in reports/pdf_factory.py)
from reports.pdf_factory import DocumentAuditFactory

# --- SMTP SERVER CONFIGURATION ---
SMTP_SERVER = "://gmail.com"          # Replace with your company SMTP host
SMTP_PORT = 587                         # Use 465 for SSL or 587 for TLS
SENDER_EMAIL = "alerts@yourbank.com"    # Your service account outbound email
SENDER_PASSWORD = "your_app_password"   # System App-Specific Password

# Raw data containing the updated structure with the EMAIL column injected
RAW_DATA = """UCIC,CUSTOMERNAME,EMAIL,LOAN_NO,LAN_PDT,DISB_DATE,LAN_DISB_AMT,LOAN_EMI,LAN_BKT,LAN_DPD,REPAY_MODE,BRANCH_DESC,SOLID,STATE,RCLG_ZONE
CUST_PL_0,Aarav Sharma,aarav.sharma@example.com,LN-PL-101,PERSONAL_LOAN,12-04-2024,300000,12500,0,0,ACH,MUMBAI_FORT,4001,MAHARASHTRA,WEST_ZONE
CUST_PL_1,Diya Iyer,diya.iyer@example.com,LN-PL-102,PERSONAL_LOAN,18-09-2024,250000,10200,1,15,AUTO_DEBIT,CHENNAI_PARRYS,6001,TAMIL_NADU,SOUTH_ZONE
CUST_PL_2,Kabir Mehta,kabir.meeta@example.com,LN-PL-103,PERSONAL_LOAN,05-01-2024,500000,18500,2,42,SI,DELHI_CONNAUGHT,1101,DELHI,NORTH_ZONE
CUST_PL_3,Ananya Desai,ananya.desai@example.com,LN-PL-104,PERSONAL_LOAN,22-11-2023,150000,7200,3,75,ACH,KOLKATA_SALT_LAKE,7001,WEST_BENGAL,EAST_ZONE
CUST_PL_4,Vivaan Joshi,vivaan.joshi@example.com,LN-PL-105,PERSONAL_LOAN,14-06-2023,400000,14800,4,110,CASH,BANGALORE_MG_ROAD,5601,KARNATAKA,SOUTH_ZONE
CUST_VL_0,Rohan Verma,rohan.verma@example.com,LN-VL-201,VEHICLE_LOAN,09-10-2024,800000,22000,0,0,SI,MUMBAI_BANDRA,4002,MAHARASHTRA,WEST_ZONE
CUST_VL_1,Isha Malhotra,isha.malhotra@example.com,LN-VL-202,VEHICLE_LOAN,14-05-2024,650000,17800,1,22,ACH,HYDERABAD_HITEC,5001,TELANGANA,SOUTH_ZONE
CUST_VL_2,Arjun Nair,arjun.nair@example.com,LN-VL-203,VEHICLE_LOAN,30-12-2023,950000,26500,2,55,AUTO_DEBIT,PUNE_CAMP,4111,MAHARASHTRA,WEST_ZONE
CUST_VL_3,Meera Reddy,meera.reddy@example.com,LN-VL-204,VEHICLE_LOAN,17-07-2023,550000,15400,3,81,SI,AHMEDABAD_ASHRAM,3801,GUJARAT,WEST_ZONE
CUST_VL_4,Sai Patil,sai.patil@example.com,LN-VL-205,VEHICLE_LOAN,02-02-2023,1200000,31000,4,125,ACH,NAGPUR_SADAR,4401,MAHARASHTRA,WEST_ZONE
CUST_HL_0,Aditya Rao,aditya.rao@example.com,LN-HL-301,HOME_LOAN,11-01-2022,4500000,39500,0,0,AUTO_DEBIT,BANGALORE_WHITEFIELD,5602,KARNATAKA,SOUTH_ZONE
CUST_HL_1,Sanya Gupta,sanya.gupta@example.com,LN-HL-302,HOME_LOAN,25-06-2022,6000000,52000,1,8,ACH,CHANDIGARH_SEC_17,1601,PUNJAB,NORTH_ZONE
CUST_HL_2,Dev Choudhury,dev.choudhury@example.com,LN-HL-303,HOME_LOAN,14-03-2021,3500000,31000,2,38,SI,JAIPUR_C_SCHEME,3021,RAJASTHAN,NORTH_ZONE
CUST_HL_3,Riya Saxena,riya.saxena@example.com,LN-HL-304,HOME_LOAN,08-11-2021,5000000,44000,3,67,AUTO_DEBIT,LUCKNOW_HAZRATGANJ,2261,UTTAR_PRADESH,NORTH_ZONE
CUST_HL_4,Yash Mishr,yash.mishr@example.com,LN-HL-305,HOME_LOAN,19-08-2020,7500000,68000,4,95,ACH,PATNA_FRASER,8001,BIHAR,EAST_ZONE
CUST_LP_0,Pranav Shah,pranav.shah@example.com,LN-LP-401,LAP,05-12-2023,2000000,24000,0,0,SI,MUMBAI_BORIVALI,4003,MAHARASHTRA,WEST_ZONE
CUST_LP_1,Tanvi Kapoor,tanvi.kapoor@example.com,LN-LP-402,LAP,28-04-2024,1800000,21500,1,19,ACH,COCHIN_MG_ROAD,6821,KERALA,SOUTH_ZONE
CUST_LP_2,Karan Johar,karan.johar@example.com,LN-LP-403,LAP,10-09-2023,3000000,35000,2,48,AUTO_DEBIT,INDORE_PALASIA,4521,MADHYA_PRADESH,WEST_ZONE
CUST_LP_3,Neha Singhal,neha.singhal@example.com,LN-LP-404,LAP,15-05-2023,2200000,26000,3,89,SI,BHUBANESWAR_JANPATH,7511,ODISHA,EAST_ZONE
CUST_LP_4,Rahul Dravid,rahul.dravid@example.com,LN-LP-405,LAP,01-11-2022,4000000,47000,4,140,ACH,CHENNAI_ADYAR,6002,TAMIL_NADU,SOUTH_ZONE"""

def send_audit_emails():
    # 1. Initialize secure network connection to the mail server
    print("Connecting to secure corporate SMTP gateway...")
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()  # Upgrade connection to secure TLS encryption
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    
    # 2. Parse the customer raw layout matrix
    csv_file = StringIO(RAW_DATA.strip())
    reader = csv.DictReader(csv_file)
    
    for row in reader:
        target_id = row['UCIC']
        account_no = row['LOAN_NO']
        customer_email = row['EMAIL']
        customer_name = row['CUSTOMERNAME']
        
        # Define dynamic playbook strategies depending on performance buckets
        dpd = int(row['LAN_DPD'])
        if dpd > 0:
            strategy = f"CRITICAL NOTICE: Account is currently in an active breach window with {dpd} Days Past Due. Initiate emergency collection recovery playbook workflows immediately."
        else:
            strategy = "STANDARD ROUTINE: Account parameters are fully within normal operational compliance parameters. Maintain regular automated monthly billing cycle protocols."
        
        print(f"Generating system compliance PDF for Account: {account_no}...")
        
        # 3. Generate PDF content dynamically into pure memory bytes
        pdf_bytes = DocumentAuditFactory.generate_audit_pdf(
            target_id=target_id,
            row_dict=row,
            allocation_strategy=strategy
        )
        
        # 4. Assemble the Multi-part MIMEMessage structure
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = customer_email
        msg['Subject'] = f"Official Compliance Audit Report — Account No: {account_no}"
        
        # Craft email body text
        body = f"""Dear {customer_name},
        
Please find attached your official, secure CreditPulse Master Compliance Audit Report corresponding to Loan Account Number {account_no}.

This transmission is secure. Please review the attached breakdown file for all registered payment statuses, risk regulatory categorization codes, and portfolio matrices.

Sincerely,
CreditPulse automated Operations
{row['BRANCH_DESC'].replace('_', ' ').title()} Hub"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # 5. Pack the PDF byte data as a physical application attachment streams
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(pdf_bytes)
        encoders.encode_base64(part)  # Safely encode payload stream into standard Base64 representation
        
        # Assign meaningful file titles to the attached asset matching the current account
        part.add_header(
            'Content-Disposition',
            f'attachment; filename="Audit_Report_{account_no}.pdf"'
        )
        msg.attach(part)
        
        # 6. Execute dispatch command across server channel
        print(f"Delivering secure package safely to: {customer_email}")
        server.sendmail(SENDER_EMAIL, customer_email, msg.as_string())
        
    # Close socket channel safely once the execution completes
    server.quit()
    print("All security audits pushed out successfully to target email networks.")

if __name__ == "__main__":
    send_audit_emails()
