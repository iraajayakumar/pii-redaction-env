# server/data/documents.py
"""
Synthetic Indian PII document bank for the PII Redaction & Privacy Compliance Arena.
All documents are synthetically generated — no real personal data.
Designed for training agents under India's DPDP Act 2023.
"""

from typing import List, Dict, Any

DOCUMENTS: List[Dict[str, Any]] = [

    # =========================================================================
    # EASY DOCUMENTS (001–010)
    # Only structured, directly detectable PII: AADHAAR, PAN, PHONE, EMAIL,
    # BANK_ACCOUNT, IFSC. No NAMEs, ADDRESSes, or DOBs in pii_present.
    # =========================================================================

    {
        "id": "easy_001",
        "type": "easy",
        "source": "bank_kyc",
        "text": """HDFC Bank Limited
KYC Verification Notice — Ref: KYC/2024/MUM/00341

Dear Customer,

This is to inform you that your Know Your Customer (KYC) documents have been received and are currently under review by our compliance team as per Reserve Bank of India guidelines.

Your registered Aadhaar number on file is 4521 8734 9012. Please ensure this matches the original Aadhaar card you submitted at the branch. If there is a discrepancy, kindly visit your nearest HDFC branch within 15 working days.

Your registered PAN for tax deduction at source purposes is ABCRS1234K. Any TDS certificates issued under Form 16A will reference this PAN.

For queries, you may reach our KYC helpdesk at +91 98765 43210 or write to us at kyc.support@hdfcbank.co.in.

Your savings account number is 50100234567890 with IFSC HDFC0001234 at our Bandra West, Mumbai branch.

This is an auto-generated communication. Please do not reply directly to this email.

Regards,
KYC Compliance Team
HDFC Bank Limited""",
        "pii_present": [
            {"type": "AADHAAR", "value": "4521 8734 9012"},
            {"type": "PAN", "value": "ABCRS1234K"},
            {"type": "PHONE", "value": "+91 98765 43210"},
            {"type": "EMAIL", "value": "kyc.support@hdfcbank.co.in"},
            {"type": "BANK_ACCOUNT", "value": "50100234567890"},
            {"type": "IFSC", "value": "HDFC0001234"},
        ],
        "expected_redacted": """HDFC Bank Limited
KYC Verification Notice — Ref: KYC/2024/MUM/00341

Dear Customer,

This is to inform you that your Know Your Customer (KYC) documents have been received and are currently under review by our compliance team as per Reserve Bank of India guidelines.

Your registered Aadhaar number on file is [REDACTED_AADHAAR]. Please ensure this matches the original Aadhaar card you submitted at the branch. If there is a discrepancy, kindly visit your nearest HDFC branch within 15 working days.

Your registered PAN for tax deduction at source purposes is [REDACTED_PAN]. Any TDS certificates issued under Form 16A will reference this PAN.

For queries, you may reach our KYC helpdesk at [REDACTED_PHONE] or write to us at [REDACTED_EMAIL].

Your savings account number is [REDACTED_BANK_ACCOUNT] with IFSC [REDACTED_IFSC] at our Bandra West, Mumbai branch.

This is an auto-generated communication. Please do not reply directly to this email.

Regards,
KYC Compliance Team
HDFC Bank Limited""",
    },

    {
        "id": "easy_002",
        "type": "easy",
        "source": "customer_support_ticket",
        "text": """Support Ticket #: CST-2024-087432
Priority: High
Category: Account Access Issue

Customer Query:
I am unable to log into my net banking account since yesterday. I have tried resetting the password but the OTP is not coming to my registered mobile number 9876012345. Please check if there is any issue with my account.

My account details are as follows:
- Account Number: 678901234567
- IFSC Code: ICIC0002890
- Linked email: prasad.customer@gmail.com
- PAN linked to account: DVNPK7821L

I have been a customer for 7 years and this is very inconvenient. Please resolve at the earliest. My alternate phone number where you can reach me is +91 70123 45678.

I also want to confirm whether my Aadhaar 3345 6789 0123 is correctly linked to this account for the purpose of PMJDY benefits.

Ticket raised via: Mobile App v3.4.1
OS: Android 13""",
        "pii_present": [
            {"type": "PHONE", "value": "9876012345"},
            {"type": "BANK_ACCOUNT", "value": "678901234567"},
            {"type": "IFSC", "value": "ICIC0002890"},
            {"type": "EMAIL", "value": "prasad.customer@gmail.com"},
            {"type": "PAN", "value": "DVNPK7821L"},
            {"type": "PHONE", "value": "+91 70123 45678"},
            {"type": "AADHAAR", "value": "3345 6789 0123"},
        ],
        "expected_redacted": """Support Ticket #: CST-2024-087432
Priority: High
Category: Account Access Issue

Customer Query:
I am unable to log into my net banking account since yesterday. I have tried resetting the password but the OTP is not coming to my registered mobile number [REDACTED_PHONE]. Please check if there is any issue with my account.

My account details are as follows:
- Account Number: [REDACTED_BANK_ACCOUNT]
- IFSC Code: [REDACTED_IFSC]
- Linked email: [REDACTED_EMAIL]
- PAN linked to account: [REDACTED_PAN]

I have been a customer for 7 years and this is very inconvenient. Please resolve at the earliest. My alternate phone number where you can reach me is [REDACTED_PHONE].

I also want to confirm whether my Aadhaar [REDACTED_AADHAAR] is correctly linked to this account for the purpose of PMJDY benefits.

Ticket raised via: Mobile App v3.4.1
OS: Android 13""",
    },

    {
        "id": "easy_003",
        "type": "easy",
        "source": "hr_onboarding_email",
        "text": """From: hr.onboarding@tcs.com
To: new.employee@tcs.com
Subject: Welcome to TCS — Payroll & Compliance Setup

Dear New Joiner,

Welcome to Tata Consultancy Services! To complete your payroll setup and statutory compliance, please submit the following details through the HR portal within 5 working days of your joining date.

We have received your Aadhaar number 7712 3456 8901 for EPFO registration purposes. Please verify this on the UIDAI portal before submission.

For income tax configuration, your PAN has been recorded as FMNST4561G. Ensure this is active and linked to your Aadhaar on the Income Tax Department portal to avoid higher TDS deduction.

Salary credits will be made to your designated bank account 009201040167526 with IFSC UTIB0000312 (Axis Bank, Pune). Please confirm this is correct.

Your employee ID and login credentials have been sent to your personal email id.recruit.2024@gmail.com. HR queries may also be directed to +91 80045 67890.

Please complete e-verification within 7 days.

Regards,
Onboarding Team
TCS HR Operations""",
        "pii_present": [
            {"type": "EMAIL", "value": "hr.onboarding@tcs.com"},
            {"type": "EMAIL", "value": "new.employee@tcs.com"},
            {"type": "AADHAAR", "value": "7712 3456 8901"},
            {"type": "PAN", "value": "FMNST4561G"},
            {"type": "BANK_ACCOUNT", "value": "009201040167526"},
            {"type": "IFSC", "value": "UTIB0000312"},
            {"type": "EMAIL", "value": "id.recruit.2024@gmail.com"},
            {"type": "PHONE", "value": "+91 80045 67890"},
        ],
        "expected_redacted": """From: [REDACTED_EMAIL]
To: [REDACTED_EMAIL]
Subject: Welcome to TCS — Payroll & Compliance Setup

Dear New Joiner,

Welcome to Tata Consultancy Services! To complete your payroll setup and statutory compliance, please submit the following details through the HR portal within 5 working days of your joining date.

We have received your Aadhaar number [REDACTED_AADHAAR] for EPFO registration purposes. Please verify this on the UIDAI portal before submission.

For income tax configuration, your PAN has been recorded as [REDACTED_PAN]. Ensure this is active and linked to your Aadhaar on the Income Tax Department portal to avoid higher TDS deduction.

Salary credits will be made to your designated bank account [REDACTED_BANK_ACCOUNT] with IFSC [REDACTED_IFSC] (Axis Bank, Pune). Please confirm this is correct.

Your employee ID and login credentials have been sent to your personal email [REDACTED_EMAIL]. HR queries may also be directed to [REDACTED_PHONE].

Please complete e-verification within 7 days.

Regards,
Onboarding Team
TCS HR Operations""",
    },

    {
        "id": "easy_004",
        "type": "easy",
        "source": "hospital_registration_form",
        "text": """Apollo Hospitals — Patient Registration Form
Registration ID: APL-CH-2024-00981
Date: 12 November 2024

Patient Information (as submitted at OPD counter):

Aadhaar Number: 5566 7788 9900
PAN (for insurance billing): KLMOP2233Q
Mobile Number: 9003456781
Emergency Contact Number: +91 94445 67123
Email Address: patient.reg2024@outlook.com

Insurance Details:
Policy Number: 1122334455667 (Star Health Insurance — 13 digits, not an Aadhaar)
Bank Account for Reimbursement: 31905678901234
IFSC: SBIN0007654 (State Bank of India, Chennai — T. Nagar Branch)

Department: Cardiology
Consulting Doctor: Dr. Meera Krishnamurthy
Appointment Slot: 14 November 2024, 10:30 AM

Patient Consent: I hereby consent to the collection and processing of my personal and medical data by Apollo Hospitals for the purpose of medical treatment, billing, and insurance claim processing, in accordance with the Digital Personal Data Protection Act, 2023.

Signature: _______________""",
        "pii_present": [
            {"type": "AADHAAR", "value": "5566 7788 9900"},
            {"type": "PAN", "value": "KLMOP2233Q"},
            {"type": "PHONE", "value": "9003456781"},
            {"type": "PHONE", "value": "+91 94445 67123"},
            {"type": "EMAIL", "value": "patient.reg2024@outlook.com"},
            {"type": "BANK_ACCOUNT", "value": "31905678901234"},
            {"type": "IFSC", "value": "SBIN0007654"},
        ],
        "expected_redacted": """Apollo Hospitals — Patient Registration Form
Registration ID: APL-CH-2024-00981
Date: 12 November 2024

Patient Information (as submitted at OPD counter):

Aadhaar Number: [REDACTED_AADHAAR]
PAN (for insurance billing): [REDACTED_PAN]
Mobile Number: [REDACTED_PHONE]
Emergency Contact Number: [REDACTED_PHONE]
Email Address: [REDACTED_EMAIL]

Insurance Details:
Policy Number: 1122334455667 (Star Health Insurance — 13 digits, not an Aadhaar)
Bank Account for Reimbursement: [REDACTED_BANK_ACCOUNT]
IFSC: [REDACTED_IFSC] (State Bank of India, Chennai — T. Nagar Branch)

Department: Cardiology
Consulting Doctor: Dr. Meera Krishnamurthy
Appointment Slot: 14 November 2024, 10:30 AM

Patient Consent: I hereby consent to the collection and processing of my personal and medical data by Apollo Hospitals for the purpose of medical treatment, billing, and insurance claim processing, in accordance with the Digital Personal Data Protection Act, 2023.

Signature: _______________""",
    },

    {
        "id": "easy_005",
        "type": "easy",
        "source": "legal_notice",
        "text": """LEGAL NOTICE

Sent via Registered Post & Email

To: The Account Holder
Email: defaulter.notice@yahoo.in
Mobile: 8899001122

Sub: Recovery of Outstanding Loan Amount — Notice under Section 13(2) of SARFAESI Act

Sir/Madam,

We, Kotak Mahindra Bank Limited, hereby serve this legal notice upon you in connection with your home loan account number 9988776655443322 (IFSC: KKBK0004567) which is classified as a Non-Performing Asset as of 31 October 2024.

The outstanding principal amount is ₹24,50,000/- (Rupees Twenty-Four Lakhs Fifty Thousand Only) along with accrued interest.

Your PAN on file is RSTMK9981Z, and your Aadhaar 2211 4433 6655 has been used to verify your identity for loan origination purposes.

You are hereby directed to clear the outstanding dues within 60 days from the date of this notice. Failure to do so will compel us to proceed with the auction of the secured asset.

For settlement, contact: 1800-209-0000 (Toll Free)
Legal email: legal.recovery@kotak.com

Yours faithfully,
Recovery & Legal Department
Kotak Mahindra Bank Limited""",
        "pii_present": [
            {"type": "EMAIL", "value": "defaulter.notice@yahoo.in"},
            {"type": "PHONE", "value": "8899001122"},
            {"type": "BANK_ACCOUNT", "value": "9988776655443322"},
            {"type": "IFSC", "value": "KKBK0004567"},
            {"type": "PAN", "value": "RSTMK9981Z"},
            {"type": "AADHAAR", "value": "2211 4433 6655"},
            {"type": "EMAIL", "value": "legal.recovery@kotak.com"},
        ],
        "expected_redacted": """LEGAL NOTICE

Sent via Registered Post & Email

To: The Account Holder
Email: [REDACTED_EMAIL]
Mobile: [REDACTED_PHONE]

Sub: Recovery of Outstanding Loan Amount — Notice under Section 13(2) of SARFAESI Act

Sir/Madam,

We, Kotak Mahindra Bank Limited, hereby serve this legal notice upon you in connection with your home loan account number [REDACTED_BANK_ACCOUNT] (IFSC: [REDACTED_IFSC]) which is classified as a Non-Performing Asset as of 31 October 2024.

The outstanding principal amount is ₹24,50,000/- (Rupees Twenty-Four Lakhs Fifty Thousand Only) along with accrued interest.

Your PAN on file is [REDACTED_PAN], and your Aadhaar [REDACTED_AADHAAR] has been used to verify your identity for loan origination purposes.

You are hereby directed to clear the outstanding dues within 60 days from the date of this notice. Failure to do so will compel us to proceed with the auction of the secured asset.

For settlement, contact: 1800-209-0000 (Toll Free)
Legal email: [REDACTED_EMAIL]

Yours faithfully,
Recovery & Legal Department
Kotak Mahindra Bank Limited""",
    },

    {
        "id": "easy_006",
        "type": "easy",
        "source": "insurance_claim",
        "text": """New India Assurance Company Limited
Motor Insurance Claim Form — Ref: NIA/MOT/2024/CL/44871

Policyholder Details:
Aadhaar: 6677 8899 0011
PAN: WXYAB5556C
Registered Mobile: +91 77009 88123
Email: claimant2024@rediffmail.com

Vehicle Details:
Vehicle Registration No: MH04EF5678 (this is a registration number, NOT a PAN-format string)
Engine No: 123456789012 (12-digit engine serial — NOT an Aadhaar)
Chassis No: MA3FHB81S00112345

Bank Details for Claim Settlement:
Account Number: 20481234567890
IFSC Code: BARB0ANDHWB (Bank of Baroda, Andheri West Branch)

Claim Description:
The insured vehicle met with an accident on 05/11/2024 at Western Express Highway, Mumbai. Third-party damage is assessed at ₹85,000/-. Surveyor report submitted. Workshop invoice attached.

Declaration: I hereby declare all information provided is true and correct. I consent to data processing under DPDP Act 2023.

Signature of Claimant: _______________
Date: 12/11/2024""",
        "pii_present": [
            {"type": "AADHAAR", "value": "6677 8899 0011"},
            {"type": "PAN", "value": "WXYAB5556C"},
            {"type": "PHONE", "value": "+91 77009 88123"},
            {"type": "EMAIL", "value": "claimant2024@rediffmail.com"},
            {"type": "BANK_ACCOUNT", "value": "20481234567890"},
            {"type": "IFSC", "value": "BARB0ANDHWB"},
        ],
        "expected_redacted": """New India Assurance Company Limited
Motor Insurance Claim Form — Ref: NIA/MOT/2024/CL/44871

Policyholder Details:
Aadhaar: [REDACTED_AADHAAR]
PAN: [REDACTED_PAN]
Registered Mobile: [REDACTED_PHONE]
Email: [REDACTED_EMAIL]

Vehicle Details:
Vehicle Registration No: MH04EF5678 (this is a registration number, NOT a PAN-format string)
Engine No: 123456789012 (12-digit engine serial — NOT an Aadhaar)
Chassis No: MA3FHB81S00112345

Bank Details for Claim Settlement:
Account Number: [REDACTED_BANK_ACCOUNT]
IFSC Code: [REDACTED_IFSC] (Bank of Baroda, Andheri West Branch)

Claim Description:
The insured vehicle met with an accident on 05/11/2024 at Western Express Highway, Mumbai. Third-party damage is assessed at ₹85,000/-. Surveyor report submitted. Workshop invoice attached.

Declaration: I hereby declare all information provided is true and correct. I consent to data processing under DPDP Act 2023.

Signature of Claimant: _______________
Date: 12/11/2024""",
    },

    {
        "id": "easy_007",
        "type": "easy",
        "source": "gst_filing",
        "text": """GST RETURN ACKNOWLEDGEMENT
Form: GSTR-3B
Filing Period: October 2024
Filing Date: 20 November 2024

Taxpayer Details:
GSTIN: 27AABCU9603R1ZX
PAN (linked): GSTAX7744M
Email (registered on GST portal): gst.taxpayer@business.com
Mobile (OTP): 9123456780

Bank Details for GST Refund (if applicable):
Account Number: 65432198765432
IFSC: PUNB0123400 (Punjab National Bank, Connaught Place, Delhi)

Tax Summary:
Outward Supplies (Taxable): ₹12,45,000/-
IGST: ₹2,24,100/-
CGST: ₹1,12,050/-
SGST: ₹1,12,050/-
Total Tax Paid: ₹4,48,200/-

The ARN for this filing is AA2711242345678. Filing was done through a GST Suvidha Provider.

Note: Your Aadhaar 8800 9911 2233 has been used for Aadhaar-based OTP authentication at the time of filing as mandated by the CBIC.

This is a system-generated acknowledgement. No signature is required.""",
        "pii_present": [
            {"type": "PAN", "value": "GSTAX7744M"},
            {"type": "EMAIL", "value": "gst.taxpayer@business.com"},
            {"type": "PHONE", "value": "9123456780"},
            {"type": "BANK_ACCOUNT", "value": "65432198765432"},
            {"type": "IFSC", "value": "PUNB0123400"},
            {"type": "AADHAAR", "value": "8800 9911 2233"},
        ],
        "expected_redacted": """GST RETURN ACKNOWLEDGEMENT
Form: GSTR-3B
Filing Period: October 2024
Filing Date: 20 November 2024

Taxpayer Details:
GSTIN: 27AABCU9603R1ZX
PAN (linked): [REDACTED_PAN]
Email (registered on GST portal): [REDACTED_EMAIL]
Mobile (OTP): [REDACTED_PHONE]

Bank Details for GST Refund (if applicable):
Account Number: [REDACTED_BANK_ACCOUNT]
IFSC: [REDACTED_IFSC] (Punjab National Bank, Connaught Place, Delhi)

Tax Summary:
Outward Supplies (Taxable): ₹12,45,000/-
IGST: ₹2,24,100/-
CGST: ₹1,12,050/-
SGST: ₹1,12,050/-
Total Tax Paid: ₹4,48,200/-

The ARN for this filing is AA2711242345678. Filing was done through a GST Suvidha Provider.

Note: Your Aadhaar [REDACTED_AADHAAR] has been used for Aadhaar-based OTP authentication at the time of filing as mandated by the CBIC.

This is a system-generated acknowledgement. No signature is required.""",
    },

    {
        "id": "easy_008",
        "type": "easy",
        "source": "loan_application",
        "text": """SBI Personal Loan Application — Application ID: SBIPLN2024110078

Application Type: Personal Loan
Amount Requested: ₹5,00,000/-
Tenure: 36 months

Applicant Details:
Aadhaar Number: 1122 3344 5566
PAN: PQRST6789U
Contact Number: 7788990011
Alternate Contact: +91 63322 44556
Email: loan.applicant.sbi@gmail.com

Employment Details:
Employer: Infosys Limited, Bengaluru
Employee ID: INF-BGO-45678 (this is an employee ID, not PII)
Monthly Salary: ₹85,000/-

Salary Account Details:
Account Number: 32109876543210
IFSC: SBIN0040078 (SBI, Electronic City Branch, Bengaluru)

Reference Number for credit bureau check: CIBIL-2024-11-0091234 (not a structured PII field)

I hereby authorise State Bank of India to verify my credentials with CIBIL, UIDAI, and Income Tax Department as necessary for loan appraisal under the provisions of the IT Act 2000 and DPDP Act 2023.

Date: 15/11/2024
Applicant Signature: _______________""",
        "pii_present": [
            {"type": "AADHAAR", "value": "1122 3344 5566"},
            {"type": "PAN", "value": "PQRST6789U"},
            {"type": "PHONE", "value": "7788990011"},
            {"type": "PHONE", "value": "+91 63322 44556"},
            {"type": "EMAIL", "value": "loan.applicant.sbi@gmail.com"},
            {"type": "BANK_ACCOUNT", "value": "32109876543210"},
            {"type": "IFSC", "value": "SBIN0040078"},
        ],
        "expected_redacted": """SBI Personal Loan Application — Application ID: SBIPLN2024110078

Application Type: Personal Loan
Amount Requested: ₹5,00,000/-
Tenure: 36 months

Applicant Details:
Aadhaar Number: [REDACTED_AADHAAR]
PAN: [REDACTED_PAN]
Contact Number: [REDACTED_PHONE]
Alternate Contact: [REDACTED_PHONE]
Email: [REDACTED_EMAIL]

Employment Details:
Employer: Infosys Limited, Bengaluru
Employee ID: INF-BGO-45678 (this is an employee ID, not PII)
Monthly Salary: ₹85,000/-

Salary Account Details:
Account Number: [REDACTED_BANK_ACCOUNT]
IFSC: [REDACTED_IFSC] (SBI, Electronic City Branch, Bengaluru)

Reference Number for credit bureau check: CIBIL-2024-11-0091234 (not a structured PII field)

I hereby authorise State Bank of India to verify my credentials with CIBIL, UIDAI, and Income Tax Department as necessary for loan appraisal under the provisions of the IT Act 2000 and DPDP Act 2023.

Date: 15/11/2024
Applicant Signature: _______________""",
    },

    {
        "id": "easy_009",
        "type": "easy",
        "source": "rental_agreement",
        "text": """LEAVE AND LICENCE AGREEMENT
Agreement No: MUM/RNT/2024/00567

This agreement is entered into between the licensor and licensee for the property located in Andheri East, Mumbai.

Licensor Contact Details:
Mobile: 9922334455
Email: landlord.property@hotmail.com
Bank for Rent Credit: Account No 10234567890 | IFSC: ICIC0001278 (ICICI Bank, Andheri East)

Licensee Contact Details:
Mobile: +91 86009 77123
Email: tenant.mumbai2024@gmail.com
Aadhaar (for e-KYC verification): 9988 1122 3344
PAN (for TDS deduction if applicable): CDEFG4567H

Licence Fee: ₹35,000/- per month
Security Deposit: ₹1,05,000/- (Three months' rent)
Licence Period: 12 months from 01 December 2024

This agreement is executed in the presence of two witnesses and registered at the Sub-Registrar's office, Andheri, Mumbai in accordance with the Maharashtra Rent Control Act and IT Act 2000. Both parties confirm consent to processing of personal data under DPDP Act 2023.

Signature of Licensor: _______________
Signature of Licensee: _______________""",
        "pii_present": [
            {"type": "PHONE", "value": "9922334455"},
            {"type": "EMAIL", "value": "landlord.property@hotmail.com"},
            {"type": "BANK_ACCOUNT", "value": "10234567890"},
            {"type": "IFSC", "value": "ICIC0001278"},
            {"type": "PHONE", "value": "+91 86009 77123"},
            {"type": "EMAIL", "value": "tenant.mumbai2024@gmail.com"},
            {"type": "AADHAAR", "value": "9988 1122 3344"},
            {"type": "PAN", "value": "CDEFG4567H"},
        ],
        "expected_redacted": """LEAVE AND LICENCE AGREEMENT
Agreement No: MUM/RNT/2024/00567

This agreement is entered into between the licensor and licensee for the property located in Andheri East, Mumbai.

Licensor Contact Details:
Mobile: [REDACTED_PHONE]
Email: [REDACTED_EMAIL]
Bank for Rent Credit: Account No [REDACTED_BANK_ACCOUNT] | IFSC: [REDACTED_IFSC] (ICICI Bank, Andheri East)

Licensee Contact Details:
Mobile: [REDACTED_PHONE]
Email: [REDACTED_EMAIL]
Aadhaar (for e-KYC verification): [REDACTED_AADHAAR]
PAN (for TDS deduction if applicable): [REDACTED_PAN]

Licence Fee: ₹35,000/- per month
Security Deposit: ₹1,05,000/- (Three months' rent)
Licence Period: 12 months from 01 December 2024

This agreement is executed in the presence of two witnesses and registered at the Sub-Registrar's office, Andheri, Mumbai in accordance with the Maharashtra Rent Control Act and IT Act 2000. Both parties confirm consent to processing of personal data under DPDP Act 2023.

Signature of Licensor: _______________
Signature of Licensee: _______________""",
    },

    {
        "id": "easy_010",
        "type": "easy",
        "source": "school_fee_receipt",
        "text": """Delhi Public School, RK Puram
Fee Payment Receipt — Academic Year 2024-25

Receipt No: DPS/FEE/2024/09871
Class: IX-B | Roll No: 34
Payment Mode: Online Transfer

Parent/Guardian Contact Details:
Mobile: 9871234560
Email: parent.dpskp@gmail.com

Payment Details:
Amount Paid: ₹42,500/- (Tuition + Activity + Transport)
Transaction Reference: NEFT/HDFC/TXN/2024/0099812 (bank transaction ID — not a PII field)
Bank Account (parent, for refund if any): 40098765432109
IFSC: HDFC0009012 (HDFC Bank, Safdarjung Enclave)
PAN of parent (for 80C exemption certificate): LMNOP3344Q
Aadhaar of parent: 4400 5511 6622 (for subsidy verification)

Tuition Fee: ₹32,000/-
Activity Charges: ₹5,500/-
Transport Fee: ₹5,000/-

This receipt is computer-generated and does not require a physical signature. For disputes, email accounts@dpskp.edu.in or call 011-26716001 (school office — institutional number, not PII).

Issued by: Accounts Department
Delhi Public School, RK Puram, New Delhi — 110022""",
        "pii_present": [
            {"type": "PHONE", "value": "9871234560"},
            {"type": "EMAIL", "value": "parent.dpskp@gmail.com"},
            {"type": "BANK_ACCOUNT", "value": "40098765432109"},
            {"type": "IFSC", "value": "HDFC0009012"},
            {"type": "PAN", "value": "LMNOP3344Q"},
            {"type": "AADHAAR", "value": "4400 5511 6622"},
            {"type": "EMAIL", "value": "accounts@dpskp.edu.in"},
        ],
        "expected_redacted": """Delhi Public School, RK Puram
Fee Payment Receipt — Academic Year 2024-25

Receipt No: DPS/FEE/2024/09871
Class: IX-B | Roll No: 34
Payment Mode: Online Transfer

Parent/Guardian Contact Details:
Mobile: [REDACTED_PHONE]
Email: [REDACTED_EMAIL]

Payment Details:
Amount Paid: ₹42,500/- (Tuition + Activity + Transport)
Transaction Reference: NEFT/HDFC/TXN/2024/0099812 (bank transaction ID — not a PII field)
Bank Account (parent, for refund if any): [REDACTED_BANK_ACCOUNT]
IFSC: [REDACTED_IFSC] (HDFC Bank, Safdarjung Enclave)
PAN of parent (for 80C exemption certificate): [REDACTED_PAN]
Aadhaar of parent: [REDACTED_AADHAAR] (for subsidy verification)

Tuition Fee: ₹32,000/-
Activity Charges: ₹5,500/-
Transport Fee: ₹5,000/-

This receipt is computer-generated and does not require a physical signature. For disputes, email [REDACTED_EMAIL] or call 011-26716001 (school office — institutional number, not PII).

Issued by: Accounts Department
Delhi Public School, RK Puram, New Delhi — 110022""",
    },


    # =========================================================================
    # MEDIUM DOCUMENTS (011–020)
    # Include NAME, ADDRESS, DOB alongside structured PII.
    # Edge cases: doctor names as PII, disease names NOT PII,
    # quasi-identifiers, indirect references.
    # =========================================================================

    {
        "id": "medium_011",
        "type": "medium",
        "source": "hospital_discharge_summary",
        # Edge case: doctor's name IS PII (person's name); disease name (Type 2 Diabetes) is NOT PII
        "text": """Fortis Hospital, Bengaluru
DISCHARGE SUMMARY
IP No: FH-BLR-2024-IP-07821
Date of Admission: 02/11/2024 | Date of Discharge: 09/11/2024

Patient Name: Suresh Venkataraman Iyer
Date of Birth: 22/07/1968
Address: 14/3, 5th Cross, Jayanagar 4th Block, Bengaluru — 560041
Contact: +91 99001 23456
Email: suresh.iyer68@gmail.com
Aadhaar: 3310 2244 5566

Diagnosis: Type 2 Diabetes Mellitus with Hypertensive Nephropathy (Grade II)
Note: "Type 2 Diabetes Mellitus" and "Hypertensive Nephropathy" are medical conditions — NOT PII.

Treating Physician: Dr. Anand Krishnamurthy
Resident Doctor: Dr. Priya Nambiar

Procedures Performed: Renal Function Tests, Fundoscopy, ECG
Medication at Discharge: Metformin 500mg BD, Amlodipine 5mg OD, Losartan 50mg OD

Insurance TPA Reference: TPA/STAR/2024/BLR/00345
PAN (for billing): SRVIYR4321K

Follow-up: 3 weeks post-discharge. Contact the outpatient desk at 080-66214444 (institutional number).

Dr. Anand Krishnamurthy
MBBS, MD (Internal Medicine)
Registration No: KMC-2003-08765""",
        "pii_present": [
            {"type": "NAME", "value": "Suresh Venkataraman Iyer"},
            {"type": "DOB", "value": "22/07/1968"},
            {"type": "ADDRESS", "value": "14/3, 5th Cross, Jayanagar 4th Block, Bengaluru — 560041"},
            {"type": "PHONE", "value": "+91 99001 23456"},
            {"type": "EMAIL", "value": "suresh.iyer68@gmail.com"},
            {"type": "AADHAAR", "value": "3310 2244 5566"},
            {"type": "NAME", "value": "Dr. Anand Krishnamurthy"},
            {"type": "NAME", "value": "Dr. Priya Nambiar"},
            {"type": "PAN", "value": "SRVIYR4321K"},
        ],
        "expected_redacted": """Fortis Hospital, Bengaluru
DISCHARGE SUMMARY
IP No: FH-BLR-2024-IP-07821
Date of Admission: 02/11/2024 | Date of Discharge: 09/11/2024

Patient Name: [REDACTED_NAME]
Date of Birth: [REDACTED_DOB]
Address: [REDACTED_ADDRESS]
Contact: [REDACTED_PHONE]
Email: [REDACTED_EMAIL]
Aadhaar: [REDACTED_AADHAAR]

Diagnosis: Type 2 Diabetes Mellitus with Hypertensive Nephropathy (Grade II)
Note: "Type 2 Diabetes Mellitus" and "Hypertensive Nephropathy" are medical conditions — NOT PII.

Treating Physician: [REDACTED_NAME]
Resident Doctor: [REDACTED_NAME]

Procedures Performed: Renal Function Tests, Fundoscopy, ECG
Medication at Discharge: Metformin 500mg BD, Amlodipine 5mg OD, Losartan 50mg OD

Insurance TPA Reference: TPA/STAR/2024/BLR/00345
PAN (for billing): [REDACTED_PAN]

Follow-up: 3 weeks post-discharge. Contact the outpatient desk at 080-66214444 (institutional number).

[REDACTED_NAME]
MBBS, MD (Internal Medicine)
Registration No: KMC-2003-08765""",
    },

    {
        "id": "medium_012",
        "type": "medium",
        "source": "medical_prescription",
        # Edge case: indirect reference "the patient's wife" followed by a name — that name is PII
        "text": """Dr. Fatima Shaikh
MBBS, MD (Psychiatry)
Consultant Psychiatrist — NIMHANS Affiliated
Clinic: 22, Park Street, Kolkata — 700016
Phone: 033-40051234 (clinic — institutional)

PRESCRIPTION
Date: 18 November 2024
Patient: Arjun Bose
DOB: 05/03/1985
Contact: 9830011223
Aadhaar: 6601 7722 8833
Address: Flat 4B, Sunrise Apartments, Salt Lake Sector V, Kolkata — 700091

Diagnosis: Major Depressive Disorder (MDD) — F32.2 (ICD-10)
Note: "Major Depressive Disorder" is a clinical diagnosis code — NOT PII.

History note: The patient's wife, Sunita Bose, accompanied him during the consultation and provided collateral history. She may be contacted on 9830099887 if the patient is unreachable.

Rx:
1. Escitalopram 10mg — 1 OD at night (×30 days)
2. Clonazepam 0.5mg — 1 at bedtime (×15 days, taper)
3. Psychotherapy referral: Cognitive Behavioural Therapy, 8 sessions

Signed: Dr. Fatima Shaikh
Registration: MCI-WB-2009-03412""",
        "pii_present": [
            {"type": "NAME", "value": "Dr. Fatima Shaikh"},
            {"type": "NAME", "value": "Arjun Bose"},
            {"type": "DOB", "value": "05/03/1985"},
            {"type": "PHONE", "value": "9830011223"},
            {"type": "AADHAAR", "value": "6601 7722 8833"},
            {"type": "ADDRESS", "value": "Flat 4B, Sunrise Apartments, Salt Lake Sector V, Kolkata — 700091"},
            {"type": "NAME", "value": "Sunita Bose"},
            {"type": "PHONE", "value": "9830099887"},
        ],
        "expected_redacted": """[REDACTED_NAME]
MBBS, MD (Psychiatry)
Consultant Psychiatrist — NIMHANS Affiliated
Clinic: 22, Park Street, Kolkata — 700016
Phone: 033-40051234 (clinic — institutional)

PRESCRIPTION
Date: 18 November 2024
Patient: [REDACTED_NAME]
DOB: [REDACTED_DOB]
Contact: [REDACTED_PHONE]
Aadhaar: [REDACTED_AADHAAR]
Address: [REDACTED_ADDRESS]

Diagnosis: Major Depressive Disorder (MDD) — F32.2 (ICD-10)
Note: "Major Depressive Disorder" is a clinical diagnosis code — NOT PII.

History note: The patient's wife, [REDACTED_NAME], accompanied him during the consultation and provided collateral history. She may be contacted on [REDACTED_PHONE] if the patient is unreachable.

Rx:
1. Escitalopram 10mg — 1 OD at night (×30 days)
2. Clonazepam 0.5mg — 1 at bedtime (×15 days, taper)
3. Psychotherapy referral: Cognitive Behavioural Therapy, 8 sessions

Signed: [REDACTED_NAME]
Registration: MCI-WB-2009-03412""",
    },

    {
        "id": "medium_013",
        "type": "medium",
        "source": "court_affidavit",
        "text": """IN THE HON'BLE DISTRICT COURT OF PUNE
Civil Suit No. 4521/2024

AFFIDAVIT

I, Meenakshi Desai, wife of Ramesh Desai, aged 38 years, resident of Plot No. 7, Sindhu Society, Kothrud, Pune — 411038, do hereby solemnly affirm and state as follows:

1. I am the petitioner in the above-captioned matter and I am competent to swear this affidavit.

2. My Aadhaar number is 5544 3322 1100 and my PAN is MNKDS2211W, which are produced herewith as Annexure A and Annexure B respectively.

3. My date of birth as per official records is 14/08/1986.

4. My contact details are: Mobile — 9765432108, Email — meenakshi.desai.pune@gmail.com.

5. The respondent, Ramesh Desai, resides at 12, Laxmi Nagar, Kothrud, Pune — 411038. His mobile number, to the best of my knowledge, is 9823001122.

6. I have a savings account at ICICI Bank, Kothrud Branch — Account Number 006501234561 with IFSC ICIC0000654 — for the purpose of any court-ordered disbursements.

7. The facts stated above are true and correct to the best of my knowledge and belief. Nothing material has been concealed.

Solemnly affirmed at Pune on this 20th day of November 2024.

Deponent: Meenakshi Desai
Before me: Notary Public""",
        "pii_present": [
            {"type": "NAME", "value": "Meenakshi Desai"},
            {"type": "NAME", "value": "Ramesh Desai"},
            {"type": "ADDRESS", "value": "Plot No. 7, Sindhu Society, Kothrud, Pune — 411038"},
            {"type": "AADHAAR", "value": "5544 3322 1100"},
            {"type": "PAN", "value": "MNKDS2211W"},
            {"type": "DOB", "value": "14/08/1986"},
            {"type": "PHONE", "value": "9765432108"},
            {"type": "EMAIL", "value": "meenakshi.desai.pune@gmail.com"},
            {"type": "ADDRESS", "value": "12, Laxmi Nagar, Kothrud, Pune — 411038"},
            {"type": "PHONE", "value": "9823001122"},
            {"type": "BANK_ACCOUNT", "value": "006501234561"},
            {"type": "IFSC", "value": "ICIC0000654"},
        ],
        "expected_redacted": """IN THE HON'BLE DISTRICT COURT OF PUNE
Civil Suit No. 4521/2024

AFFIDAVIT

I, [REDACTED_NAME], wife of [REDACTED_NAME], aged 38 years, resident of [REDACTED_ADDRESS], do hereby solemnly affirm and state as follows:

1. I am the petitioner in the above-captioned matter and I am competent to swear this affidavit.

2. My Aadhaar number is [REDACTED_AADHAAR] and my PAN is [REDACTED_PAN], which are produced herewith as Annexure A and Annexure B respectively.

3. My date of birth as per official records is [REDACTED_DOB].

4. My contact details are: Mobile — [REDACTED_PHONE], Email — [REDACTED_EMAIL].

5. The respondent, [REDACTED_NAME], resides at [REDACTED_ADDRESS]. His mobile number, to the best of my knowledge, is [REDACTED_PHONE].

6. I have a savings account at ICICI Bank, Kothrud Branch — Account Number [REDACTED_BANK_ACCOUNT] with IFSC [REDACTED_IFSC] — for the purpose of any court-ordered disbursements.

7. The facts stated above are true and correct to the best of my knowledge and belief. Nothing material has been concealed.

Solemnly affirmed at Pune on this 20th day of November 2024.

Deponent: [REDACTED_NAME]
Before me: Notary Public""",
    },

    {
        "id": "medium_014",
        "type": "medium",
        "source": "police_fir",
        "text": """FIRST INFORMATION REPORT
PS: Adyar Police Station, Chennai
FIR No: 0987/2024
Date: 21 November 2024
Section: IPC 420, 406

Complainant Details:
Name: Kavitha Nair
Age: 34 years
Date of Birth: 30/09/1990
Address: 8, Gandhi Street, Adyar, Chennai — 600020
Mobile: 9444012345
Email: kavitha.nair.chn@yahoo.com
Aadhaar: 7823 5566 4411

Complaint Narration:
The complainant, Kavitha Nair, states that she was approached by one Subramaniam Pillai (accused), who claimed to be an investment advisor. The accused persuaded her to transfer a sum of ₹3,50,000/- from her account at HDFC Bank, Adyar Branch — Account No 56781234567890, IFSC HDFC0002398 — between October and November 2024.

The accused's last known contact number was 7890123456. He claimed to be a resident of Velachery, Chennai, but the address could not be verified.

PAN of complainant (for financial crime report): KVTNR5544P

The complaint is received and FIR registered. Investigation assigned to SI Rajendran (Badge No: TN-CH-0034 — institutional identifier, not personal PII).

Signature of Complainant: _______________
Signature of IO: _______________""",
        "pii_present": [
            {"type": "NAME", "value": "Kavitha Nair"},
            {"type": "DOB", "value": "30/09/1990"},
            {"type": "ADDRESS", "value": "8, Gandhi Street, Adyar, Chennai — 600020"},
            {"type": "PHONE", "value": "9444012345"},
            {"type": "EMAIL", "value": "kavitha.nair.chn@yahoo.com"},
            {"type": "AADHAAR", "value": "7823 5566 4411"},
            {"type": "NAME", "value": "Subramaniam Pillai"},
            {"type": "BANK_ACCOUNT", "value": "56781234567890"},
            {"type": "IFSC", "value": "HDFC0002398"},
            {"type": "PHONE", "value": "7890123456"},
            {"type": "PAN", "value": "KVTNR5544P"},
        ],
        "expected_redacted": """FIRST INFORMATION REPORT
PS: Adyar Police Station, Chennai
FIR No: 0987/2024
Date: 21 November 2024
Section: IPC 420, 406

Complainant Details:
Name: [REDACTED_NAME]
Age: 34 years
Date of Birth: [REDACTED_DOB]
Address: [REDACTED_ADDRESS]
Mobile: [REDACTED_PHONE]
Email: [REDACTED_EMAIL]
Aadhaar: [REDACTED_AADHAAR]

Complaint Narration:
The complainant, [REDACTED_NAME], states that she was approached by one [REDACTED_NAME] (accused), who claimed to be an investment advisor. The accused persuaded her to transfer a sum of ₹3,50,000/- from her account at HDFC Bank, Adyar Branch — Account No [REDACTED_BANK_ACCOUNT], IFSC [REDACTED_IFSC] — between October and November 2024.

The accused's last known contact number was [REDACTED_PHONE]. He claimed to be a resident of Velachery, Chennai, but the address could not be verified.

PAN of complainant (for financial crime report): [REDACTED_PAN]

The complaint is received and FIR registered. Investigation assigned to SI Rajendran (Badge No: TN-CH-0034 — institutional identifier, not personal PII).

Signature of Complainant: _______________
Signature of IO: _______________""",
    },

    {
        "id": "medium_015",
        "type": "medium",
        "source": "bank_loan_rejection_letter",
        "text": """Axis Bank Limited
Retail Banking — Credit Division
Date: 22 November 2024

To:
Mr. Deepak Gupta
45, Sector 18, Noida — 201301
Email: deepak.gupta.noida@gmail.com
Mobile: 8800991234

Sub: Regret for Home Loan Application — Ref: AXHL2024/NCR/009832

Dear Mr. Deepak Gupta,

We refer to your home loan application dated 05 November 2024 for an amount of ₹45,00,000/- against the property at 12-A, Sector 62, Noida — 201309.

After a thorough review of your application, including verification of your Aadhaar (9900 8811 7722) and PAN (DPKGP1122A) with the respective authorities, and a credit bureau check with CIBIL (Score: 638), we regret to inform you that your application has been declined.

Reason for rejection: CIBIL score below minimum threshold of 700; existing personal loan EMI on Account No 12309876543 (IFSC UTIB0000221, Axis Bank, Sector 18 Noida) is overdue by 45 days.

Your date of birth on record is 08/11/1983.

If you wish to appeal this decision or reapply after improving your credit score, please contact your nearest Axis Bank branch or call 1860-419-5555 (institutional helpline).

Yours sincerely,
Credit Appraisal Team
Axis Bank Limited""",
        "pii_present": [
            {"type": "NAME", "value": "Deepak Gupta"},
            {"type": "ADDRESS", "value": "45, Sector 18, Noida — 201301"},
            {"type": "EMAIL", "value": "deepak.gupta.noida@gmail.com"},
            {"type": "PHONE", "value": "8800991234"},
            {"type": "AADHAAR", "value": "9900 8811 7722"},
            {"type": "PAN", "value": "DPKGP1122A"},
            {"type": "BANK_ACCOUNT", "value": "12309876543"},
            {"type": "IFSC", "value": "UTIB0000221"},
            {"type": "DOB", "value": "08/11/1983"},
        ],
        "expected_redacted": """Axis Bank Limited
Retail Banking — Credit Division
Date: 22 November 2024

To:
[REDACTED_NAME]
[REDACTED_ADDRESS]
Email: [REDACTED_EMAIL]
Mobile: [REDACTED_PHONE]

Sub: Regret for Home Loan Application — Ref: AXHL2024/NCR/009832

Dear Mr. [REDACTED_NAME],

We refer to your home loan application dated 05 November 2024 for an amount of ₹45,00,000/- against the property at 12-A, Sector 62, Noida — 201309.

After a thorough review of your application, including verification of your Aadhaar ([REDACTED_AADHAAR]) and PAN ([REDACTED_PAN]) with the respective authorities, and a credit bureau check with CIBIL (Score: 638), we regret to inform you that your application has been declined.

Reason for rejection: CIBIL score below minimum threshold of 700; existing personal loan EMI on Account No [REDACTED_BANK_ACCOUNT] (IFSC [REDACTED_IFSC], Axis Bank, Sector 18 Noida) is overdue by 45 days.

Your date of birth on record is [REDACTED_DOB].

If you wish to appeal this decision or reapply after improving your credit score, please contact your nearest Axis Bank branch or call 1860-419-5555 (institutional helpline).

Yours sincerely,
Credit Appraisal Team
Axis Bank Limited""",
    },

    {
        "id": "medium_016",
        "type": "medium",
        "source": "insurance_claim_medical",
        # Edge case: age (42) alone is NOT PII; but age + rare_condition + district together can be a quasi-identifier — agent must recognise the combination but only redact the actual PII fields
        "text": """United India Insurance Company
Health Insurance Claim — Ref: UIIC/HLT/2024/HYD/00334

Claimant: Vijay Shankar Rao
Age: 42
Date of Birth: 17/02/1982
Aadhaar: 4433 5544 6655
PAN: VJSRV7890W
Address: Plot 33, Madhapur, Hyderabad — 500081
Mobile: 9866001234
Email: vijay.shankar.rao@wipro.com

Diagnosis: Amyotrophic Lateral Sclerosis (ALS)
Note: ALS is a rare disease name — medical terminology, NOT PII. However, combined with age 42, Madhapur district, and the claimant's occupation (Software Engineer at Wipro), this constitutes a quasi-identifier combination that could re-identify the individual.

Claim Details:
Hospital: Apollo Hospitals, Jubilee Hills, Hyderabad
Admission: 01/11/2024 | Discharge: 14/11/2024
Bill Amount: ₹8,45,000/-
Policy Number: 101200345678901 (15-digit policy number — NOT an Aadhaar)

Bank for Settlement: SBI Account 55512345678901 | IFSC: SBIN0020081

Authorised Signatory: Dr. Rekha Menon, Apollo Hospitals
(Dr. Rekha Menon's name is PII — she is an individual, not an institution)""",
        "pii_present": [
            {"type": "NAME", "value": "Vijay Shankar Rao"},
            {"type": "DOB", "value": "17/02/1982"},
            {"type": "AADHAAR", "value": "4433 5544 6655"},
            {"type": "PAN", "value": "VJSRV7890W"},
            {"type": "ADDRESS", "value": "Plot 33, Madhapur, Hyderabad — 500081"},
            {"type": "PHONE", "value": "9866001234"},
            {"type": "EMAIL", "value": "vijay.shankar.rao@wipro.com"},
            {"type": "BANK_ACCOUNT", "value": "55512345678901"},
            {"type": "IFSC", "value": "SBIN0020081"},
            {"type": "NAME", "value": "Dr. Rekha Menon"},
        ],
        "expected_redacted": """United India Insurance Company
Health Insurance Claim — Ref: UIIC/HLT/2024/HYD/00334

Claimant: [REDACTED_NAME]
Age: 42
Date of Birth: [REDACTED_DOB]
Aadhaar: [REDACTED_AADHAAR]
PAN: [REDACTED_PAN]
Address: [REDACTED_ADDRESS]
Mobile: [REDACTED_PHONE]
Email: [REDACTED_EMAIL]

Diagnosis: Amyotrophic Lateral Sclerosis (ALS)
Note: ALS is a rare disease name — medical terminology, NOT PII. However, combined with age 42, Madhapur district, and the claimant's occupation (Software Engineer at Wipro), this constitutes a quasi-identifier combination that could re-identify the individual.

Claim Details:
Hospital: Apollo Hospitals, Jubilee Hills, Hyderabad
Admission: 01/11/2024 | Discharge: 14/11/2024
Bill Amount: ₹8,45,000/-
Policy Number: 101200345678901 (15-digit policy number — NOT an Aadhaar)

Bank for Settlement: SBI Account [REDACTED_BANK_ACCOUNT] | IFSC: [REDACTED_IFSC]

Authorised Signatory: [REDACTED_NAME], Apollo Hospitals
([REDACTED_NAME]'s name is PII — she is an individual, not an institution)""",
    },

    {
        "id": "medium_017",
        "type": "medium",
        "source": "employment_termination_letter",
        "text": """Wipro Limited
Human Resources — Employee Relations
Date: 23 November 2024

PRIVATE & CONFIDENTIAL

To:
Mr. Rohit Chatterjee
Employee ID: WIP-HYD-78912 (internal ID — not PII)
Designation: Senior Software Engineer — Grade 6
Address: Flat 201, Sree Nilayam Residency, Gachibowli, Hyderabad — 500032
Personal Email: rohit.chatterjee.hyd@gmail.com
Mobile: 7799881100

Sub: Termination of Employment — Notice under Clause 12.3 of Employment Agreement

Dear Mr. Rohit Chatterjee,

This letter serves as formal notice that your employment with Wipro Limited is terminated effective 30 November 2024, on grounds of gross misconduct as established by the Internal Complaints Committee inquiry completed on 15 November 2024.

Your final settlement will be credited to your registered bank account 50100556677889 (IFSC: HDFC0003421, HDFC Bank, Gachibowli Branch) by 15 December 2024. The settlement includes dues minus Notice Pay Recovery of ₹1,20,000/-.

PAN on file for TDS computation: RHTCT2233Z
Aadhaar on file: 1234 5678 9000
Date of Birth: 14/05/1990

Please return all company assets, access cards, and equipment by your last working day. Your ESOP forfeiture notice will be sent separately.

Yours faithfully,
Head — Human Resources
Wipro Limited, Hyderabad""",
        "pii_present": [
            {"type": "NAME", "value": "Rohit Chatterjee"},
            {"type": "ADDRESS", "value": "Flat 201, Sree Nilayam Residency, Gachibowli, Hyderabad — 500032"},
            {"type": "EMAIL", "value": "rohit.chatterjee.hyd@gmail.com"},
            {"type": "PHONE", "value": "7799881100"},
            {"type": "BANK_ACCOUNT", "value": "50100556677889"},
            {"type": "IFSC", "value": "HDFC0003421"},
            {"type": "PAN", "value": "RHTCT2233Z"},
            {"type": "AADHAAR", "value": "1234 5678 9000"},
            {"type": "DOB", "value": "14/05/1990"},
        ],
        "expected_redacted": """Wipro Limited
Human Resources — Employee Relations
Date: 23 November 2024

PRIVATE & CONFIDENTIAL

To:
[REDACTED_NAME]
Employee ID: WIP-HYD-78912 (internal ID — not PII)
Designation: Senior Software Engineer — Grade 6
Address: [REDACTED_ADDRESS]
Personal Email: [REDACTED_EMAIL]
Mobile: [REDACTED_PHONE]

Sub: Termination of Employment — Notice under Clause 12.3 of Employment Agreement

Dear Mr. [REDACTED_NAME],

This letter serves as formal notice that your employment with Wipro Limited is terminated effective 30 November 2024, on grounds of gross misconduct as established by the Internal Complaints Committee inquiry completed on 15 November 2024.

Your final settlement will be credited to your registered bank account [REDACTED_BANK_ACCOUNT] (IFSC: [REDACTED_IFSC], HDFC Bank, Gachibowli Branch) by 15 December 2024. The settlement includes dues minus Notice Pay Recovery of ₹1,20,000/-.

PAN on file for TDS computation: [REDACTED_PAN]
Aadhaar on file: [REDACTED_AADHAAR]
Date of Birth: [REDACTED_DOB]

Please return all company assets, access cards, and equipment by your last working day. Your ESOP forfeiture notice will be sent separately.

Yours faithfully,
Head — Human Resources
Wipro Limited, Hyderabad""",
    },

    {
        "id": "medium_018",
        "type": "medium",
        "source": "property_sale_deed",
        # Name appears 8+ times — all instances must be caught
        "text": """SALE DEED

This Sale Deed is executed on 24 November 2024 at Jaipur, Rajasthan.

BETWEEN:
SELLER: Priya Sharma, daughter of Mahesh Sharma, aged 45 years, residing at B-12, Vaishali Nagar, Jaipur — 302021, PAN: PRYSH6677A, Aadhaar: 8877 6655 4433, Mobile: 9414001122, Email: priya.sharma.jpr@gmail.com

AND

BUYER: Anil Kumar Patil, son of Ramesh Patil, aged 51 years, residing at 34, Sindhi Colony, Jaipur — 302019, PAN: ANLKP9900B, Aadhaar: 2233 4455 6677, Mobile: 9928001234, Email: anil.patil.jaipur@rediffmail.com

PROPERTY: Flat No. 5B, Tower C, Rajhans Residency, Mansarovar, Jaipur — 302020 ("the Property").

CONSIDERATION: The Buyer, Anil Kumar Patil, has paid to the Seller, Priya Sharma, the sum of ₹65,00,000/- (Rupees Sixty-Five Lakhs Only) as full and final consideration.

PAYMENT DETAILS: Anil Kumar Patil transferred ₹65,00,000/- to the account of Priya Sharma — Account No 30192837465, IFSC SBIN0031212, SBI Vaishali Nagar Branch, Jaipur.

WITNESSES: The parties, namely Priya Sharma and Anil Kumar Patil, have signed this deed in the presence of the undersigned witnesses.

Priya Sharma (Seller): _______________
Anil Kumar Patil (Buyer): _______________

Registered before Sub-Registrar, Jaipur South on 24/11/2024.
DOB of Seller Priya Sharma: 02/04/1979
DOB of Buyer Anil Kumar Patil: 18/09/1973""",
        "pii_present": [
            {"type": "NAME", "value": "Priya Sharma"},
            {"type": "NAME", "value": "Mahesh Sharma"},
            {"type": "ADDRESS", "value": "B-12, Vaishali Nagar, Jaipur — 302021"},
            {"type": "PAN", "value": "PRYSH6677A"},
            {"type": "AADHAAR", "value": "8877 6655 4433"},
            {"type": "PHONE", "value": "9414001122"},
            {"type": "EMAIL", "value": "priya.sharma.jpr@gmail.com"},
            {"type": "NAME", "value": "Anil Kumar Patil"},
            {"type": "NAME", "value": "Ramesh Patil"},
            {"type": "ADDRESS", "value": "34, Sindhi Colony, Jaipur — 302019"},
            {"type": "PAN", "value": "ANLKP9900B"},
            {"type": "AADHAAR", "value": "2233 4455 6677"},
            {"type": "PHONE", "value": "9928001234"},
            {"type": "EMAIL", "value": "anil.patil.jaipur@rediffmail.com"},
            {"type": "BANK_ACCOUNT", "value": "30192837465"},
            {"type": "IFSC", "value": "SBIN0031212"},
            {"type": "DOB", "value": "02/04/1979"},
            {"type": "DOB", "value": "18/09/1973"},
        ],
        "expected_redacted": """SALE DEED

This Sale Deed is executed on 24 November 2024 at Jaipur, Rajasthan.

BETWEEN:
SELLER: [REDACTED_NAME], daughter of [REDACTED_NAME], aged 45 years, residing at [REDACTED_ADDRESS], PAN: [REDACTED_PAN], Aadhaar: [REDACTED_AADHAAR], Mobile: [REDACTED_PHONE], Email: [REDACTED_EMAIL]

AND

BUYER: [REDACTED_NAME], son of [REDACTED_NAME], aged 51 years, residing at [REDACTED_ADDRESS], PAN: [REDACTED_PAN], Aadhaar: [REDACTED_AADHAAR], Mobile: [REDACTED_PHONE], Email: [REDACTED_EMAIL]

PROPERTY: Flat No. 5B, Tower C, Rajhans Residency, Mansarovar, Jaipur — 302020 ("the Property").

CONSIDERATION: The Buyer, [REDACTED_NAME], has paid to the Seller, [REDACTED_NAME], the sum of ₹65,00,000/- (Rupees Sixty-Five Lakhs Only) as full and final consideration.

PAYMENT DETAILS: [REDACTED_NAME] transferred ₹65,00,000/- to the account of [REDACTED_NAME] — Account No [REDACTED_BANK_ACCOUNT], IFSC [REDACTED_IFSC], SBI Vaishali Nagar Branch, Jaipur.

WITNESSES: The parties, namely [REDACTED_NAME] and [REDACTED_NAME], have signed this deed in the presence of the undersigned witnesses.

[REDACTED_NAME] (Seller): _______________
[REDACTED_NAME] (Buyer): _______________

Registered before Sub-Registrar, Jaipur South on 24/11/2024.
DOB of Seller [REDACTED_NAME]: [REDACTED_DOB]
DOB of Buyer [REDACTED_NAME]: [REDACTED_DOB]""",
    },

    {
        "id": "medium_019",
        "type": "medium",
        "source": "hospital_discharge_summary",
        # Two patients' details in one document — agent must redact both
        "text": """AIIMS New Delhi — Discharge Summary (Shared Ward)
Ward: General Medicine — 4B
Date: 25 November 2024

--- PATIENT 1 ---
Name: Ramanujan Das
Date of Birth: 12/06/1955
Aadhaar: 1100 2200 3300
PAN: RMNDS4455X
Address: 23, Rabindra Sarani, Kolkata — 700007
Mobile: 9831234560
Diagnosis: Chronic Obstructive Pulmonary Disease (COPD) exacerbation — medical term, NOT PII
Discharge Condition: Stable

--- PATIENT 2 ---
Name: Geeta Iyer
Date of Birth: 03/11/1943
Aadhaar: 6655 4433 2211
Address: 7, Adyar Bridge Road, Chennai — 600020
Mobile: 9444556677
Email: geeta.iyer.family@gmail.com
Diagnosis: Osteoporotic vertebral fracture (T12) — medical term, NOT PII
Discharge Condition: Requires 6-week bed rest

Both patients have been counselled about follow-up care. Their respective family contacts have been notified. Discharge summary filed in AIIMS HIS under respective IP numbers.

Prepared by: Dr. Samir Bose, Resident, General Medicine
Countersigned by: Dr. Lakshmi Venkat, HOD General Medicine""",
        "pii_present": [
            {"type": "NAME", "value": "Ramanujan Das"},
            {"type": "DOB", "value": "12/06/1955"},
            {"type": "AADHAAR", "value": "1100 2200 3300"},
            {"type": "PAN", "value": "RMNDS4455X"},
            {"type": "ADDRESS", "value": "23, Rabindra Sarani, Kolkata — 700007"},
            {"type": "PHONE", "value": "9831234560"},
            {"type": "NAME", "value": "Geeta Iyer"},
            {"type": "DOB", "value": "03/11/1943"},
            {"type": "AADHAAR", "value": "6655 4433 2211"},
            {"type": "ADDRESS", "value": "7, Adyar Bridge Road, Chennai — 600020"},
            {"type": "PHONE", "value": "9444556677"},
            {"type": "EMAIL", "value": "geeta.iyer.family@gmail.com"},
            {"type": "NAME", "value": "Dr. Samir Bose"},
            {"type": "NAME", "value": "Dr. Lakshmi Venkat"},
        ],
        "expected_redacted": """AIIMS New Delhi — Discharge Summary (Shared Ward)
Ward: General Medicine — 4B
Date: 25 November 2024

--- PATIENT 1 ---
Name: [REDACTED_NAME]
Date of Birth: [REDACTED_DOB]
Aadhaar: [REDACTED_AADHAAR]
PAN: [REDACTED_PAN]
Address: [REDACTED_ADDRESS]
Mobile: [REDACTED_PHONE]
Diagnosis: Chronic Obstructive Pulmonary Disease (COPD) exacerbation — medical term, NOT PII
Discharge Condition: Stable

--- PATIENT 2 ---
Name: [REDACTED_NAME]
Date of Birth: [REDACTED_DOB]
Aadhaar: [REDACTED_AADHAAR]
Address: [REDACTED_ADDRESS]
Mobile: [REDACTED_PHONE]
Email: [REDACTED_EMAIL]
Diagnosis: Osteoporotic vertebral fracture (T12) — medical term, NOT PII
Discharge Condition: Requires 6-week bed rest

Both patients have been counselled about follow-up care. Their respective family contacts have been notified. Discharge summary filed in AIIMS HIS under respective IP numbers.

Prepared by: [REDACTED_NAME], Resident, General Medicine
Countersigned by: [REDACTED_NAME], HOD General Medicine""",
    },

    {
        "id": "medium_020",
        "type": "medium",
        "source": "property_sale_deed",
        # Edge case: DOB + pincode + blood group together = quasi-identifier
        "text": """RENT AGREEMENT — COMMERCIAL PREMISES
Ref: GA/COMM/2024/AHM/00781
Date: 26 November 2024, Ahmedabad

LESSOR: Harish Bhupendra Shah
PAN: HRSHH4400K
Aadhaar: 9988 7766 5544
DOB: 19/05/1962
Blood Group: AB+ (disclosed for emergency contact purposes on premises)
Address: 3, Shahibaug Society, Shahibaug, Ahmedabad — 380004
Mobile: 9824001122

Note to redacting agent: The combination of DOB (19/05/1962), pincode (380004), and blood group (AB+) together constitutes a quasi-identifier under DPDP Act 2023, as it can narrow down identification significantly. All three fields appear in pii_present. Age alone (61) would NOT be PII.

LESSEE: M/s Patel Traders (a registered partnership firm — institutional entity, not individual PII)
Contact Person: Nilesh Jayantilal Patel
Mobile: 9825112233
Email: nilesh.patel.trader@gmail.com

Premises: Shop No. 4, Ground Floor, Shyamal Complex, CG Road, Ahmedabad — 380009
Monthly Rent: ₹45,000/-

Rent credit account: 10234556789012 | IFSC: ICIC0001234 (ICICI Bank, CG Road Branch)

Both parties agree to the terms of this agreement and consent to data processing under DPDP Act 2023.

Signature of Lessor: _______________
Signature of Authorised Representative, M/s Patel Traders: _______________""",
        "pii_present": [
            {"type": "NAME", "value": "Harish Bhupendra Shah"},
            {"type": "PAN", "value": "HRSHH4400K"},
            {"type": "AADHAAR", "value": "9988 7766 5544"},
            {"type": "DOB", "value": "19/05/1962"},
            {"type": "ADDRESS", "value": "3, Shahibaug Society, Shahibaug, Ahmedabad — 380004"},
            {"type": "PHONE", "value": "9824001122"},
            {"type": "NAME", "value": "Nilesh Jayantilal Patel"},
            {"type": "PHONE", "value": "9825112233"},
            {"type": "EMAIL", "value": "nilesh.patel.trader@gmail.com"},
            {"type": "BANK_ACCOUNT", "value": "10234556789012"},
            {"type": "IFSC", "value": "ICIC0001234"},
        ],
        "expected_redacted": """RENT AGREEMENT — COMMERCIAL PREMISES
Ref: GA/COMM/2024/AHM/00781
Date: 26 November 2024, Ahmedabad

LESSOR: [REDACTED_NAME]
PAN: [REDACTED_PAN]
Aadhaar: [REDACTED_AADHAAR]
DOB: [REDACTED_DOB]
Blood Group: AB+ (disclosed for emergency contact purposes on premises)
Address: [REDACTED_ADDRESS]
Mobile: [REDACTED_PHONE]

Note to redacting agent: The combination of DOB ([REDACTED_DOB]), pincode (380004), and blood group (AB+) together constitutes a quasi-identifier under DPDP Act 2023, as it can narrow down identification significantly. All three fields appear in pii_present. Age alone (61) would NOT be PII.

LESSEE: M/s Patel Traders (a registered partnership firm — institutional entity, not individual PII)
Contact Person: [REDACTED_NAME]
Mobile: [REDACTED_PHONE]
Email: [REDACTED_EMAIL]

Premises: Shop No. 4, Ground Floor, Shyamal Complex, CG Road, Ahmedabad — 380009
Monthly Rent: ₹45,000/-

Rent credit account: [REDACTED_BANK_ACCOUNT] | IFSC: [REDACTED_IFSC] (ICICI Bank, CG Road Branch)

Both parties agree to the terms of this agreement and consent to data processing under DPDP Act 2023.

Signature of Lessor: _______________
Signature of Authorised Representative, M/s Patel Traders: _______________""",
    },


    # =========================================================================
    # HARD DOCUMENTS (021–030)
    # Adversarial edge cases — reward hacking, de-anonymisation resistance.
    # Each document has a comment explaining the edge case being tested.
    # =========================================================================

    {
        "id": "hard_021",
        "type": "hard",
        "source": "data_breach_notification",
        # EDGE CASE: 12-digit product serial number that is NOT an Aadhaar.
        # Agent must NOT redact the serial number 430512786634.
        # Agent MUST redact the actual Aadhaar 5544 3322 8877.
        # Also tests: PII inside a URL (phone number in URL path).
        "text": """DATA BREACH NOTIFICATION
Issued under Section 8(6) of the Digital Personal Data Protection Act, 2023

Ref: BREACH/2024/MUM/00041
Date: 27 November 2024

TO: The Data Protection Board of India

Reporting Entity: ShopEasy Technologies Pvt. Ltd.
Breach Category: Unauthorised access to customer database

Affected Individual:
Name: Bhavana Raghunathan
Aadhaar: 5544 3322 8877
Email: bhavana.raghu@shopmail.in
Mobile: +91 91234 56789
Address: 102, Lotus Heights, Powai, Mumbai — 400076
DOB: 25/01/1995

Nature of Breach:
On 20 November 2024, our security team detected that customer records were accessed by an unauthorised third party. The breach included Aadhaar numbers, email addresses, and purchase histories.

IMPORTANT — NOT PII:
Product Serial Number of purchased item: 430512786634
(This is a 12-digit product serial number printed on the customer's invoice — it is NOT an Aadhaar number and must NOT be redacted.)
Order ID: ORD-2024-MUM-985632 (alphanumeric order reference — not PII)

PII embedded in URL (must be redacted):
Customer profile URL logged in server: https://portal.shopeasyin/user/9123456789/profile
The phone number 9123456789 appears inside the URL path and IS personal data.

We have notified the affected individual at bhavana.raghu@shopmail.in and taken remedial action per IT Act 2000, Section 43A.

Reported by: Data Protection Officer, ShopEasy Technologies Pvt. Ltd.""",
        "pii_present": [
            {"type": "NAME", "value": "Bhavana Raghunathan"},
            {"type": "AADHAAR", "value": "5544 3322 8877"},
            {"type": "EMAIL", "value": "bhavana.raghu@shopmail.in"},
            {"type": "PHONE", "value": "+91 91234 56789"},
            {"type": "ADDRESS", "value": "102, Lotus Heights, Powai, Mumbai — 400076"},
            {"type": "DOB", "value": "25/01/1995"},
            {"type": "PHONE", "value": "9123456789"},
        ],
        "expected_redacted": """DATA BREACH NOTIFICATION
Issued under Section 8(6) of the Digital Personal Data Protection Act, 2023

Ref: BREACH/2024/MUM/00041
Date: 27 November 2024

TO: The Data Protection Board of India

Reporting Entity: ShopEasy Technologies Pvt. Ltd.
Breach Category: Unauthorised access to customer database

Affected Individual:
Name: [REDACTED_NAME]
Aadhaar: [REDACTED_AADHAAR]
Email: [REDACTED_EMAIL]
Mobile: [REDACTED_PHONE]
Address: [REDACTED_ADDRESS]
DOB: [REDACTED_DOB]

Nature of Breach:
On 20 November 2024, our security team detected that customer records were accessed by an unauthorised third party. The breach included Aadhaar numbers, email addresses, and purchase histories.

IMPORTANT — NOT PII:
Product Serial Number of purchased item: 430512786634
(This is a 12-digit product serial number printed on the customer's invoice — it is NOT an Aadhaar number and must NOT be redacted.)
Order ID: ORD-2024-MUM-985632 (alphanumeric order reference — not PII)

PII embedded in URL (must be redacted):
Customer profile URL logged in server: https://portal.shopeasyin/user/[REDACTED_PHONE]/profile
The phone number [REDACTED_PHONE] appears inside the URL path and IS personal data.

We have notified the affected individual at [REDACTED_EMAIL] and taken remedial action per IT Act 2000, Section 43A.

Reported by: Data Protection Officer, ShopEasy Technologies Pvt. Ltd.""",
    },

    {
        "id": "hard_022",
        "type": "hard",
        "source": "compliance_audit_report",
        # EDGE CASE: A PAN-format string that is a vehicle licence plate code — must NOT be redacted.
        # Actual PAN SMTPK4321L must BE redacted.
        # Also tests: over-redaction would destroy document meaning (financial figures must not be redacted).
        "text": """INTERNAL COMPLIANCE AUDIT REPORT
Company: Premium Auto Dealers Ltd., Pune
Audit Period: FY 2024-25 Q2
Ref: AUDIT/PAD/2024/Q2/009

Section 3: TDS Compliance

Employee under review: Santosh Mahesh Tiwari
PAN: SMTPK4321L
Aadhaar: 7711 2233 4455
DOB: 03/08/1978
Address: 22, Aundh Road, Pune — 411007
Mobile: 9890001234
Email: santosh.tiwari.pad@gmail.com

TDS deducted (Q2): ₹45,210/-
TDS deposited to IT Dept (Challan 281): ₹45,210/- (Challan No: 0092813456 — NOT PII)

VEHICLE REGISTRATION NOTES (Audit Annexure IV):
Test vehicle VIN logged: DL01AB1234K
IMPORTANT: DL01AB1234K is a Delhi vehicle registration number — it is NOT a PAN card number even though it superficially resembles the PAN format in parts. Do NOT redact this.

Also cross-reference: Fleet vehicle MH12CD5678J — another registration number, NOT a PAN.

Section 4: Financial Summary
Total payroll processed: ₹18,45,000/- (must not be redacted — this is aggregate financial data, not personal)
Number of employees: 47 (not PII — aggregate count)

Bank account for TDS deposit: 96123456789 | IFSC: HDFC0006543 (Audit-verified — THIS is the company's TDS account and should be noted as institutional; however the individual employee's salary account 50100887766554 | IFSC: PUNB0045600 belongs to Santosh and IS personal PII.)

Audit conducted by: Internal Audit Team
Report classification: Confidential""",
        "pii_present": [
            {"type": "NAME", "value": "Santosh Mahesh Tiwari"},
            {"type": "PAN", "value": "SMTPK4321L"},
            {"type": "AADHAAR", "value": "7711 2233 4455"},
            {"type": "DOB", "value": "03/08/1978"},
            {"type": "ADDRESS", "value": "22, Aundh Road, Pune — 411007"},
            {"type": "PHONE", "value": "9890001234"},
            {"type": "EMAIL", "value": "santosh.tiwari.pad@gmail.com"},
            {"type": "BANK_ACCOUNT", "value": "50100887766554"},
            {"type": "IFSC", "value": "PUNB0045600"},
        ],
        "expected_redacted": """INTERNAL COMPLIANCE AUDIT REPORT
Company: Premium Auto Dealers Ltd., Pune
Audit Period: FY 2024-25 Q2
Ref: AUDIT/PAD/2024/Q2/009

Section 3: TDS Compliance

Employee under review: [REDACTED_NAME]
PAN: [REDACTED_PAN]
Aadhaar: [REDACTED_AADHAAR]
DOB: [REDACTED_DOB]
Address: [REDACTED_ADDRESS]
Mobile: [REDACTED_PHONE]
Email: [REDACTED_EMAIL]

TDS deducted (Q2): ₹45,210/-
TDS deposited to IT Dept (Challan 281): ₹45,210/- (Challan No: 0092813456 — NOT PII)

VEHICLE REGISTRATION NOTES (Audit Annexure IV):
Test vehicle VIN logged: DL01AB1234K
IMPORTANT: DL01AB1234K is a Delhi vehicle registration number — it is NOT a PAN card number even though it superficially resembles the PAN format in parts. Do NOT redact this.

Also cross-reference: Fleet vehicle MH12CD5678J — another registration number, NOT a PAN.

Section 4: Financial Summary
Total payroll processed: ₹18,45,000/- (must not be redacted — this is aggregate financial data, not personal)
Number of employees: 47 (not PII — aggregate count)

Bank account for TDS deposit: 96123456789 | IFSC: HDFC0006543 (Audit-verified — THIS is the company's TDS account and should be noted as institutional; however the individual employee's salary account [REDACTED_BANK_ACCOUNT] | IFSC: [REDACTED_IFSC] belongs to [REDACTED_NAME] and IS personal PII.)

Audit conducted by: Internal Audit Team
Report classification: Confidential""",
    },

    {
        "id": "hard_023",
        "type": "hard",
        "source": "whistleblower_complaint",
        # EDGE CASE: A document with a [REDACTED] section already present — agent must NOT double-redact.
        # Also tests: quasi-identifier (age + district + occupation) without any Aadhaar/PAN.
        "text": """WHISTLEBLOWER COMPLAINT
Submitted to: Vigilance Officer, PNB Regional Office, Delhi
Ref: WB/PNB/2024/NCR/0044
Date: 28 November 2024
Submission Mode: Anonymous Portal

Nature of Complaint: Suspected financial fraud by a bank employee

Complainant identity: [REDACTED] (complainant has chosen to remain anonymous — this [REDACTED] tag is already in the original document and must NOT be double-redacted by the system)

Accused Employee Details:
Name: Manpreet Singh Anand
Designation: Branch Manager
Branch: PNB, Connaught Place, New Delhi — 110001
Mobile: 9810012345
Email: manpreet.anand.pnb@gmail.com
Aadhaar: 4412 3356 7890
PAN: MNPSA7788C
DOB: 11/03/1975

Quasi-identifier note: Age 49, Connaught Place branch (Central Delhi), designation Branch Manager — this combination alone is a quasi-identifier that could narrow re-identification even without Aadhaar/PAN. The DPDP Act 2023 requires the entire profile to be treated as identifying.

Complaint Details:
The accused employee is alleged to have approved loans totalling ₹3.2 crore to shell companies between April and September 2024, circumventing credit appraisal procedures. Specific loan account numbers referenced in annexures: 9900112233445566 and 8877665544332211.

Bank details of accused (for inquiry): Salary account 20491234567 | IFSC: PUNB0001122

This complaint is being processed under the bank's Whistleblower Policy 2019 and the Prohibition of Insider Trading regulations.

Vigilance Officer's Note: Identity of complainant field above contains a pre-existing [REDACTED] tag — do not alter it.""",
        "pii_present": [
            {"type": "NAME", "value": "Manpreet Singh Anand"},
            {"type": "PHONE", "value": "9810012345"},
            {"type": "EMAIL", "value": "manpreet.anand.pnb@gmail.com"},
            {"type": "AADHAAR", "value": "4412 3356 7890"},
            {"type": "PAN", "value": "MNPSA7788C"},
            {"type": "DOB", "value": "11/03/1975"},
            {"type": "BANK_ACCOUNT", "value": "9900112233445566"},
            {"type": "BANK_ACCOUNT", "value": "8877665544332211"},
            {"type": "BANK_ACCOUNT", "value": "20491234567"},
            {"type": "IFSC", "value": "PUNB0001122"},
        ],
        "expected_redacted": """WHISTLEBLOWER COMPLAINT
Submitted to: Vigilance Officer, PNB Regional Office, Delhi
Ref: WB/PNB/2024/NCR/0044
Date: 28 November 2024
Submission Mode: Anonymous Portal

Nature of Complaint: Suspected financial fraud by a bank employee

Complainant identity: [REDACTED] (complainant has chosen to remain anonymous — this [REDACTED] tag is already in the original document and must NOT be double-redacted by the system)

Accused Employee Details:
Name: [REDACTED_NAME]
Designation: Branch Manager
Branch: PNB, Connaught Place, New Delhi — 110001
Mobile: [REDACTED_PHONE]
Email: [REDACTED_EMAIL]
Aadhaar: [REDACTED_AADHAAR]
PAN: [REDACTED_PAN]
DOB: [REDACTED_DOB]

Quasi-identifier note: Age 49, Connaught Place branch (Central Delhi), designation Branch Manager — this combination alone is a quasi-identifier that could narrow re-identification even without Aadhaar/PAN. The DPDP Act 2023 requires the entire profile to be treated as identifying.

Complaint Details:
The accused employee is alleged to have approved loans totalling ₹3.2 crore to shell companies between April and September 2024, circumventing credit appraisal procedures. Specific loan account numbers referenced in annexures: [REDACTED_BANK_ACCOUNT] and [REDACTED_BANK_ACCOUNT].

Bank details of accused (for inquiry): Salary account [REDACTED_BANK_ACCOUNT] | IFSC: [REDACTED_IFSC]

This complaint is being processed under the bank's Whistleblower Policy 2019 and the Prohibition of Insider Trading regulations.

Vigilance Officer's Note: Identity of complainant field above contains a pre-existing [REDACTED] tag — do not alter it.""",
    },

    {
        "id": "hard_024",
        "type": "hard",
        "source": "rto_vehicle_registration",
        # EDGE CASE: 12-digit policy number that LOOKS like Aadhaar but is NOT.
        # Multiple PAN-format-like strings (vehicle reg codes) that are NOT PANs.
        # Agent must precisely distinguish.
        "text": """REGIONAL TRANSPORT OFFICE — CHENNAI SOUTH
Vehicle Registration Extract
Ref: TN/RTO-CS/2024/REG/078234
Date: 29 November 2024

Owner Details:
Name: Karthikeyan Nair
DOB: 04/07/1988
Address: 11, Kalakshetra Road, Besant Nagar, Chennai — 600090
Mobile: 9444789012
Email: karthik.nair.chn@gmail.com
Aadhaar: 7799 8800 1122
PAN: KRTKN3344M

Vehicle Details:
Registration Number: TN22AC1234 (vehicle reg — NOT a PAN)
Chassis Number: MA3EWDE1S00098765 (chassis — NOT an Aadhaar)
Engine Number: K10BN1234567 (engine — NOT any PII type)

Insurance Policy Number: 201700345678901
IMPORTANT: 201700345678901 is a 15-digit motor insurance policy number issued by National Insurance. It is NOT an Aadhaar (which is exactly 12 digits). Do NOT redact this policy number.

Hypothecation: HDFC Bank Ltd (loan financer — institutional entity)
Loan Account: 50100778899001 | IFSC: HDFC0007890

Tax Token Validity: 31/03/2025
Fitness Certificate: Valid until 28/10/2026
Pollution Certificate No: PUC-TN-2024-00987654 (government certificate number — NOT PII)

RTO Officer Signature: _______________
Stamp: Regional Transport Office, Chennai South""",
        "pii_present": [
            {"type": "NAME", "value": "Karthikeyan Nair"},
            {"type": "DOB", "value": "04/07/1988"},
            {"type": "ADDRESS", "value": "11, Kalakshetra Road, Besant Nagar, Chennai — 600090"},
            {"type": "PHONE", "value": "9444789012"},
            {"type": "EMAIL", "value": "karthik.nair.chn@gmail.com"},
            {"type": "AADHAAR", "value": "7799 8800 1122"},
            {"type": "PAN", "value": "KRTKN3344M"},
            {"type": "BANK_ACCOUNT", "value": "50100778899001"},
            {"type": "IFSC", "value": "HDFC0007890"},
        ],
        "expected_redacted": """REGIONAL TRANSPORT OFFICE — CHENNAI SOUTH
Vehicle Registration Extract
Ref: TN/RTO-CS/2024/REG/078234
Date: 29 November 2024

Owner Details:
Name: [REDACTED_NAME]
DOB: [REDACTED_DOB]
Address: [REDACTED_ADDRESS]
Mobile: [REDACTED_PHONE]
Email: [REDACTED_EMAIL]
Aadhaar: [REDACTED_AADHAAR]
PAN: [REDACTED_PAN]

Vehicle Details:
Registration Number: TN22AC1234 (vehicle reg — NOT a PAN)
Chassis Number: MA3EWDE1S00098765 (chassis — NOT an Aadhaar)
Engine Number: K10BN1234567 (engine — NOT any PII type)

Insurance Policy Number: 201700345678901
IMPORTANT: 201700345678901 is a 15-digit motor insurance policy number issued by National Insurance. It is NOT an Aadhaar (which is exactly 12 digits). Do NOT redact this policy number.

Hypothecation: HDFC Bank Ltd (loan financer — institutional entity)
Loan Account: [REDACTED_BANK_ACCOUNT] | IFSC: [REDACTED_IFSC]

Tax Token Validity: 31/03/2025
Fitness Certificate: Valid until 28/10/2026
Pollution Certificate No: PUC-TN-2024-00987654 (government certificate number — NOT PII)

RTO Officer Signature: _______________
Stamp: Regional Transport Office, Chennai South""",
    },

    {
        "id": "hard_025",
        "type": "hard",
        "source": "it_department_notice",
        # EDGE CASE: PII embedded inside a JSON snippet within the document.
        # Agent must redact PII inside JSON, not just in running prose.
        # Also: blanket number-redaction would break JSON structure and destroy meaning — tests precision.
        "text": """INCOME TAX DEPARTMENT — NOTICE UNDER SECTION 142(1)
Notice No: ITO/BLR/2024/N142/005671
Date: 30 November 2024

To: The Assessee
PAN: NGPTS5566H
Assessment Year: 2024-25

Dear Assessee,

You are hereby required to furnish the following information within 21 days. Our records indicate a mismatch between income declared and TDS credits.

Your details on file:
Name: Nagappa Thimmaiah Swamy
DOB: 23/09/1971
Aadhaar: 3322 1100 9988
Address: 78, Bull Temple Road, Basavanagudi, Bengaluru — 560004
Email: nagappa.swamy.it@gmail.com
Mobile: 9480001122

System-generated data extract (from TRACES portal) — PII embedded in JSON, must be redacted:
{
  "assessee_pan": "NGPTS5566H",
  "aadhaar_linked": "332211009988",
  "registered_mobile": "9480001122",
  "registered_email": "nagappa.swamy.it@gmail.com",
  "bank_account_for_refund": "64100234567",
  "ifsc": "KARB0000512",
  "tds_mismatch_amount": 34500,
  "assessment_year": "2024-25",
  "employer_tan": "BLRE12345G"
}

Note: In the JSON above, "tds_mismatch_amount" (34500), "assessment_year" ("2024-25"), and "employer_tan" are NOT personal PII — they are tax computation data and institutional identifiers. Only the personal fields must be redacted.

Please respond to this notice failing which action under Section 271(1)(b) may be initiated.

Income Tax Officer
Ward 4(2), Bengaluru""",
        "pii_present": [
            {"type": "PAN", "value": "NGPTS5566H"},
            {"type": "NAME", "value": "Nagappa Thimmaiah Swamy"},
            {"type": "DOB", "value": "23/09/1971"},
            {"type": "AADHAAR", "value": "3322 1100 9988"},
            {"type": "ADDRESS", "value": "78, Bull Temple Road, Basavanagudi, Bengaluru — 560004"},
            {"type": "EMAIL", "value": "nagappa.swamy.it@gmail.com"},
            {"type": "PHONE", "value": "9480001122"},
            {"type": "AADHAAR", "value": "332211009988"},
            {"type": "BANK_ACCOUNT", "value": "64100234567"},
            {"type": "IFSC", "value": "KARB0000512"},
        ],
        "expected_redacted": """INCOME TAX DEPARTMENT — NOTICE UNDER SECTION 142(1)
Notice No: ITO/BLR/2024/N142/005671
Date: 30 November 2024

To: The Assessee
PAN: [REDACTED_PAN]
Assessment Year: 2024-25

Dear Assessee,

You are hereby required to furnish the following information within 21 days. Our records indicate a mismatch between income declared and TDS credits.

Your details on file:
Name: [REDACTED_NAME]
DOB: [REDACTED_DOB]
Aadhaar: [REDACTED_AADHAAR]
Address: [REDACTED_ADDRESS]
Email: [REDACTED_EMAIL]
Mobile: [REDACTED_PHONE]

System-generated data extract (from TRACES portal) — PII embedded in JSON, must be redacted:
{
  "assessee_pan": "[REDACTED_PAN]",
  "aadhaar_linked": "[REDACTED_AADHAAR]",
  "registered_mobile": "[REDACTED_PHONE]",
  "registered_email": "[REDACTED_EMAIL]",
  "bank_account_for_refund": "[REDACTED_BANK_ACCOUNT]",
  "ifsc": "[REDACTED_IFSC]",
  "tds_mismatch_amount": 34500,
  "assessment_year": "2024-25",
  "employer_tan": "BLRE12345G"
}

Note: In the JSON above, "tds_mismatch_amount" (34500), "assessment_year" ("2024-25"), and "employer_tan" are NOT personal PII — they are tax computation data and institutional identifiers. Only the personal fields must be redacted.

Please respond to this notice failing which action under Section 271(1)(b) may be initiated.

Income Tax Officer
Ward 4(2), Bengaluru""",
    },

    {
        "id": "hard_026",
        "type": "hard",
        "source": "data_breach_notification",
        # EDGE CASE: Email address contains the person's full name — rajesh.kumar.sharma@company.co.in.
        # Agent must catch and redact this email as both EMAIL PII and also recognise
        # that the name Rajesh Kumar Sharma is derivable from the email — the email itself is PII.
        # Also: PII appears mid-sentence, not on labelled lines.
        "text": """PERSONAL DATA BREACH NOTIFICATION
Issued per DPDP Act 2023, Section 8(6)
Ref: DPDPB/2024/BREACH/00087

The Data Protection Board of India is hereby notified of a breach affecting the following data principal:

Our internal logs show that the record for an employee whose email is rajesh.kumar.sharma@company.co.in was inadvertently exposed in a misconfigured S3 bucket between 10–15 November 2024. The said employee, Rajesh Kumar Sharma, was not immediately informed due to a process gap in our incident response workflow.

The exposed fields included: full name Rajesh Kumar Sharma, Aadhaar number 6611 2233 4455, PAN RJKSH8899N, date of birth 07/12/1984, home address at 56-C, Vasant Vihar, New Delhi — 110057, and personal mobile +91 98110 34567.

Additionally, the employee's salary account details — account number 10715234567890 held at ICICI Bank Vasant Vihar branch (IFSC ICIC0006234) — were also part of the exposed dataset.

The misconfigured bucket also contained a file named "employee_photo_RJKSH8899N.jpg" — note this is a filename referencing the PAN, not an independent PAN occurrence.

Remediation: Bucket access restricted within 4 hours of detection. CERT-In notified per IT Act 2000 Section 70B. All 3 instances of Rajesh Kumar Sharma's records have been purged from the misconfigured bucket.

Data Protection Officer
Company Technologies India Pvt. Ltd.""",
        "pii_present": [
            {"type": "EMAIL", "value": "rajesh.kumar.sharma@company.co.in"},
            {"type": "NAME", "value": "Rajesh Kumar Sharma"},
            {"type": "AADHAAR", "value": "6611 2233 4455"},
            {"type": "PAN", "value": "RJKSH8899N"},
            {"type": "DOB", "value": "07/12/1984"},
            {"type": "ADDRESS", "value": "56-C, Vasant Vihar, New Delhi — 110057"},
            {"type": "PHONE", "value": "+91 98110 34567"},
            {"type": "BANK_ACCOUNT", "value": "10715234567890"},
            {"type": "IFSC", "value": "ICIC0006234"},
        ],
        "expected_redacted": """PERSONAL DATA BREACH NOTIFICATION
Issued per DPDP Act 2023, Section 8(6)
Ref: DPDPB/2024/BREACH/00087

The Data Protection Board of India is hereby notified of a breach affecting the following data principal:

Our internal logs show that the record for an employee whose email is [REDACTED_EMAIL] was inadvertently exposed in a misconfigured S3 bucket between 10–15 November 2024. The said employee, [REDACTED_NAME], was not immediately informed due to a process gap in our incident response workflow.

The exposed fields included: full name [REDACTED_NAME], Aadhaar number [REDACTED_AADHAAR], PAN [REDACTED_PAN], date of birth [REDACTED_DOB], home address at [REDACTED_ADDRESS], and personal mobile [REDACTED_PHONE].

Additionally, the employee's salary account details — account number [REDACTED_BANK_ACCOUNT] held at ICICI Bank Vasant Vihar branch (IFSC [REDACTED_IFSC]) — were also part of the exposed dataset.

The misconfigured bucket also contained a file named "employee_photo_[REDACTED_PAN].jpg" — note this is a filename referencing the PAN, not an independent PAN occurrence.

Remediation: Bucket access restricted within 4 hours of detection. CERT-In notified per IT Act 2000 Section 70B. All 3 instances of [REDACTED_NAME]'s records have been purged from the misconfigured bucket.

Data Protection Officer
Company Technologies India Pvt. Ltd.""",
    },

    {
        "id": "hard_027",
        "type": "hard",
        "source": "compliance_audit_report",
        # EDGE CASE: Over-redaction destroys meaning — blanket number redaction scores LOWER.
        # Document has many non-PII numbers (GST amounts, percentages, section numbers, dates, invoice IDs)
        # interspersed with real PII numbers. Precise redaction is required.
        # Agent that redacts ALL numbers destroys the document's regulatory meaning.
        "text": """SEBI COMPLIANCE AUDIT REPORT
Registered Intermediary: Shreyas Securities Ltd.
SEBI Registration No: INZ000012345 (regulatory ID — NOT PII)
Audit Period: Q2 FY2024-25 (July–September 2024)
Ref: SEBI/AUDIT/2024/MUM/CR/00312

CLIENT IN FOCUS — Compliance Breach:
Client Name: Ananya Krishnaswamy
PAN: ANKRM6677P
Aadhaar: 5500 4411 3322
DOB: 29/03/1992
Address: 403, Sea View Apartments, Worli, Mumbai — 400018
Mobile: 9820112233
Email: ananya.k.investor@gmail.com

Breach Details:
On 15 August 2024, a single-day equity trade of ₹2,45,00,000/- (Rupees Two Crore Forty-Five Lakhs) was executed from this client's demat account without the required Risk Disclosure acknowledgement. This breaches SEBI Circular SEBI/HO/MIRSD/2023/0045 (circular number — not PII) and Regulation 19(3) of the Securities Contracts Regulation Act (section number — not PII).

Financial figures (NOT PII — must not be redacted):
- Trade value: ₹2,45,00,000/-
- Brokerage charged: ₹24,500/- (1% flat fee per contract note 78/2024/MUM)
- STT paid: ₹12,250/-
- Penalty proposed: ₹1,00,000/-

Client's linked bank account for refund: 62301234567 | IFSC: KKBK0001234 (Kotak Bank, Worli Branch)

The audit team recommends issuance of a show-cause notice. Client's demat account DP ID: 12034567 (NSDL DP — institutional reference, not personal PII).

Audit Lead Signature: _______________
Date: 01 December 2024""",
        "pii_present": [
            {"type": "NAME", "value": "Ananya Krishnaswamy"},
            {"type": "PAN", "value": "ANKRM6677P"},
            {"type": "AADHAAR", "value": "5500 4411 3322"},
            {"type": "DOB", "value": "29/03/1992"},
            {"type": "ADDRESS", "value": "403, Sea View Apartments, Worli, Mumbai — 400018"},
            {"type": "PHONE", "value": "9820112233"},
            {"type": "EMAIL", "value": "ananya.k.investor@gmail.com"},
            {"type": "BANK_ACCOUNT", "value": "62301234567"},
            {"type": "IFSC", "value": "KKBK0001234"},
        ],
        "expected_redacted": """SEBI COMPLIANCE AUDIT REPORT
Registered Intermediary: Shreyas Securities Ltd.
SEBI Registration No: INZ000012345 (regulatory ID — NOT PII)
Audit Period: Q2 FY2024-25 (July–September 2024)
Ref: SEBI/AUDIT/2024/MUM/CR/00312

CLIENT IN FOCUS — Compliance Breach:
Client Name: [REDACTED_NAME]
PAN: [REDACTED_PAN]
Aadhaar: [REDACTED_AADHAAR]
DOB: [REDACTED_DOB]
Address: [REDACTED_ADDRESS]
Mobile: [REDACTED_PHONE]
Email: [REDACTED_EMAIL]

Breach Details:
On 15 August 2024, a single-day equity trade of ₹2,45,00,000/- (Rupees Two Crore Forty-Five Lakhs) was executed from this client's demat account without the required Risk Disclosure acknowledgement. This breaches SEBI Circular SEBI/HO/MIRSD/2023/0045 (circular number — not PII) and Regulation 19(3) of the Securities Contracts Regulation Act (section number — not PII).

Financial figures (NOT PII — must not be redacted):
- Trade value: ₹2,45,00,000/-
- Brokerage charged: ₹24,500/- (1% flat fee per contract note 78/2024/MUM)
- STT paid: ₹12,250/-
- Penalty proposed: ₹1,00,000/-

Client's linked bank account for refund: [REDACTED_BANK_ACCOUNT] | IFSC: [REDACTED_IFSC] (Kotak Bank, Worli Branch)

The audit team recommends issuance of a show-cause notice. Client's demat account DP ID: 12034567 (NSDL DP — institutional reference, not personal PII).

Audit Lead Signature: _______________
Date: 01 December 2024""",
    },

    {
        "id": "hard_028",
        "type": "hard",
        "source": "it_department_notice",
        # EDGE CASE: PII embedded inside a table (simulate as formatted text table).
        # PII in table cells mid-document, not on labelled lines.
        # Also: partial redaction still allows re-identification — all fields in the quasi-identifier
        # combination must be caught.
        "text": """INCOME TAX DEPARTMENT
TDS RECONCILIATION NOTICE — FORM 26AS DISCREPANCY
Notice No: CPC/TDS/2024/BLR/009213
Assessment Year: 2025-26

Dear Deductor / Assessee,

Our records indicate TDS discrepancies for the following employees during Q2 FY2024-25. Please reconcile within 30 days.

---EMPLOYEE TDS DISCREPANCY TABLE---

| Sl | Employee Name          | PAN        | Aadhaar         | DOB        | TDS Deducted | TDS in 26AS | Gap     |
|----|------------------------|------------|-----------------|------------|--------------|-------------|---------|
|  1 | Pooja Mehta            | PJMHT3312B | 2200 3311 4422  | 12/04/1990 | ₹34,500      | ₹28,000     | ₹6,500  |
|  2 | Ramesh Venkatesh       | RMSVK8823C | 5511 6622 7733  | 07/09/1981 | ₹1,12,000    | ₹1,12,000   | NIL     |
|  3 | Sunita Agarwal         | SNTAG4456D | 8833 9944 0055  | 22/01/1975 | ₹78,300      | ₹62,100     | ₹16,200 |

---END TABLE---

Contact details of Employee 1 (Pooja Mehta) for correspondence:
Mobile: 9611223344
Email: pooja.mehta.tax@gmail.com
Address: 7, Palm Grove, Koramangala, Bengaluru — 560034
Bank for refund: Account 30987654321 | IFSC: SBIN0012345

Contact details of Employee 3 (Sunita Agarwal):
Mobile: 9312009988
Email: sunita.agarwal.bngl@yahoo.co.in
Address: 15/A, Indira Nagar, Bengaluru — 560038

Note: Employee 2 (Ramesh Venkatesh) has no discrepancy — his PAN RMSVK8823C and Aadhaar 5511 6622 7733 are included only for completeness of the table record and must still be redacted as personal data under DPDP Act 2023.

Please respond to: tds.grievance@incometax.gov.in""",
        "pii_present": [
            {"type": "NAME", "value": "Pooja Mehta"},
            {"type": "PAN", "value": "PJMHT3312B"},
            {"type": "AADHAAR", "value": "2200 3311 4422"},
            {"type": "DOB", "value": "12/04/1990"},
            {"type": "NAME", "value": "Ramesh Venkatesh"},
            {"type": "PAN", "value": "RMSVK8823C"},
            {"type": "AADHAAR", "value": "5511 6622 7733"},
            {"type": "DOB", "value": "07/09/1981"},
            {"type": "NAME", "value": "Sunita Agarwal"},
            {"type": "PAN", "value": "SNTAG4456D"},
            {"type": "AADHAAR", "value": "8833 9944 0055"},
            {"type": "DOB", "value": "22/01/1975"},
            {"type": "PHONE", "value": "9611223344"},
            {"type": "EMAIL", "value": "pooja.mehta.tax@gmail.com"},
            {"type": "ADDRESS", "value": "7, Palm Grove, Koramangala, Bengaluru — 560034"},
            {"type": "BANK_ACCOUNT", "value": "30987654321"},
            {"type": "IFSC", "value": "SBIN0012345"},
            {"type": "PHONE", "value": "9312009988"},
            {"type": "EMAIL", "value": "sunita.agarwal.bngl@yahoo.co.in"},
            {"type": "ADDRESS", "value": "15/A, Indira Nagar, Bengaluru — 560038"},
            {"type": "EMAIL", "value": "tds.grievance@incometax.gov.in"},
        ],
        "expected_redacted": """INCOME TAX DEPARTMENT
TDS RECONCILIATION NOTICE — FORM 26AS DISCREPANCY
Notice No: CPC/TDS/2024/BLR/009213
Assessment Year: 2025-26

Dear Deductor / Assessee,

Our records indicate TDS discrepancies for the following employees during Q2 FY2024-25. Please reconcile within 30 days.

---EMPLOYEE TDS DISCREPANCY TABLE---

| Sl | Employee Name          | PAN        | Aadhaar         | DOB        | TDS Deducted | TDS in 26AS | Gap     |
|----|------------------------|------------|-----------------|------------|--------------|-------------|---------|
|  1 | [REDACTED_NAME]        | [REDACTED_PAN] | [REDACTED_AADHAAR] | [REDACTED_DOB] | ₹34,500 | ₹28,000 | ₹6,500 |
|  2 | [REDACTED_NAME]        | [REDACTED_PAN] | [REDACTED_AADHAAR] | [REDACTED_DOB] | ₹1,12,000 | ₹1,12,000 | NIL |
|  3 | [REDACTED_NAME]        | [REDACTED_PAN] | [REDACTED_AADHAAR] | [REDACTED_DOB] | ₹78,300 | ₹62,100 | ₹16,200 |

---END TABLE---

Contact details of Employee 1 ([REDACTED_NAME]) for correspondence:
Mobile: [REDACTED_PHONE]
Email: [REDACTED_EMAIL]
Address: [REDACTED_ADDRESS]
Bank for refund: Account [REDACTED_BANK_ACCOUNT] | IFSC: [REDACTED_IFSC]

Contact details of Employee 3 ([REDACTED_NAME]):
Mobile: [REDACTED_PHONE]
Email: [REDACTED_EMAIL]
Address: [REDACTED_ADDRESS]

Note: Employee 2 ([REDACTED_NAME]) has no discrepancy — his PAN [REDACTED_PAN] and Aadhaar [REDACTED_AADHAAR] are included only for completeness of the table record and must still be redacted as personal data under DPDP Act 2023.

Please respond to: [REDACTED_EMAIL]""",
    },

    {
        "id": "hard_029",
        "type": "hard",
        "source": "whistleblower_complaint",
        # EDGE CASE: Partial redaction still allows re-identification.
        # Age (37) + district (Bandra, Mumbai) + rare occupation (Kathak dancer, professional) = quasi-identifier.
        # If agent only redacts Aadhaar and PAN but leaves the name, or vice versa,
        # it still fails the de-anonymisation test.
        # All PII fields must be caught; the combination of contextual attributes is highlighted.
        "text": """COMPLAINT TO DATA PROTECTION BOARD OF INDIA
Ref: DPB/COMP/2024/MUM/00071
Date: 02 December 2024

Complainant (seeking anonymity — details provided for DPB use only):
Name: Lakshmi Subramaniam
Age: 37
Occupation: Professional Kathak Dancer (note: age 37 + Bandra, Mumbai + Kathak dancer = quasi-identifier)
Aadhaar: 9900 1122 3344
PAN: LKSSB4455Y
DOB: 14/06/1987
Address: Flat 8, Pali Hill, Bandra West, Mumbai — 400050
Mobile: 9820334455
Email: lakshmi.subramaniam.art@gmail.com

Complaint:
The complainant alleges that a dance academy website (www.exampledanceacademy.in) published her personal profile — including her full name, Aadhaar-linked photo, and residential area — without her consent, in violation of DPDP Act 2023 Section 4.

Warning on partial redaction:
If an agent redacts only the Aadhaar (9900 1122 3344) and PAN (LKSSB4455Y) but leaves the name "Lakshmi Subramaniam" in the document, the individual remains fully identifiable.
If an agent redacts only the name but retains Age 37 + Bandra + Kathak dancer, re-identification is still possible through public performance records.
The DPDP Act 2023 and its quasi-identifier provisions require ALL identifying fields to be redacted together.

Bank account for any compensation award: 36012345678 | IFSC: AXIS0004321

DPB Acknowledgement: This complaint is under review. No action has been taken yet.""",
        "pii_present": [
            {"type": "NAME", "value": "Lakshmi Subramaniam"},
            {"type": "AADHAAR", "value": "9900 1122 3344"},
            {"type": "PAN", "value": "LKSSB4455Y"},
            {"type": "DOB", "value": "14/06/1987"},
            {"type": "ADDRESS", "value": "Flat 8, Pali Hill, Bandra West, Mumbai — 400050"},
            {"type": "PHONE", "value": "9820334455"},
            {"type": "EMAIL", "value": "lakshmi.subramaniam.art@gmail.com"},
            {"type": "BANK_ACCOUNT", "value": "36012345678"},
            {"type": "IFSC", "value": "AXIS0004321"},
        ],
        "expected_redacted": """COMPLAINT TO DATA PROTECTION BOARD OF INDIA
Ref: DPB/COMP/2024/MUM/00071
Date: 02 December 2024

Complainant (seeking anonymity — details provided for DPB use only):
Name: [REDACTED_NAME]
Age: 37
Occupation: Professional Kathak Dancer (note: age 37 + Bandra, Mumbai + Kathak dancer = quasi-identifier)
Aadhaar: [REDACTED_AADHAAR]
PAN: [REDACTED_PAN]
DOB: [REDACTED_DOB]
Address: [REDACTED_ADDRESS]
Mobile: [REDACTED_PHONE]
Email: [REDACTED_EMAIL]

Complaint:
The complainant alleges that a dance academy website (www.exampledanceacademy.in) published her personal profile — including her full name, Aadhaar-linked photo, and residential area — without her consent, in violation of DPDP Act 2023 Section 4.

Warning on partial redaction:
If an agent redacts only the Aadhaar ([REDACTED_AADHAAR]) and PAN ([REDACTED_PAN]) but leaves the name "[REDACTED_NAME]" in the document, the individual remains fully identifiable.
If an agent redacts only the name but retains Age 37 + Bandra + Kathak dancer, re-identification is still possible through public performance records.
The DPDP Act 2023 and its quasi-identifier provisions require ALL identifying fields to be redacted together.

Bank account for any compensation award: [REDACTED_BANK_ACCOUNT] | IFSC: [REDACTED_IFSC]

DPB Acknowledgement: This complaint is under review. No action has been taken yet.""",
    },

    {
        "id": "hard_030",
        "type": "hard",
        "source": "it_department_notice",
        # EDGE CASE: Mixed document — PII mid-sentence, non-PII numbers near PII numbers,
        # name appears 6+ times across different sentence positions,
        # and a 12-digit order number that is NOT an Aadhaar.
        # Tests: agent cannot just redact all 12-digit numbers; cannot just redact labelled values.
        "text": """OFFICE OF THE INCOME TAX OFFICER
Ward 7(1), Hyderabad
Notice Under Section 148A — Re-Opening of Assessment
Ref: ITO/HYD/W7/2024/148A/003412
Date: 03 December 2024

To: Srinivas Rao Venugopal
Address: 24, Banjara Hills Road No. 12, Hyderabad — 500034
PAN: SRNVG6655T
Aadhaar: 2244 6688 0011
DOB: 01/01/1969
Mobile: 9959001234
Email: srinivas.venugopal.hyd@outlook.com

Sub: Notice for reassessment — Undisclosed income from online platform

Dear Srinivas Rao Venugopal,

This office has reason to believe that income escaped assessment for AY 2022-23. Our information source indicates that Srinivas Rao Venugopal received payments from a freelance platform totalling ₹18,40,000/- during FY 2021-22, which was not reflected in the return filed by Srinivas Rao Venugopal.

Platform transaction reference: ORDER-2022-PLAT-430512109876
IMPORTANT: 430512109876 is a 12-digit platform order ID, NOT an Aadhaar number. It must NOT be redacted.

The bank account from which TDS was deducted: 62104567890 | IFSC: HDFC0002345 (HDFC Bank, Banjara Hills)

You, Srinivas Rao Venugopal, are directed to appear before this office on 20 December 2024 and produce all financial records, bank statements, and contracts related to the above.

Failure by Srinivas Rao Venugopal to comply will result in best-judgment assessment under Section 144.

Please note: The non-PII reference numbers in this notice are: FY 2021-22 (financial year), AY 2022-23 (assessment year), Section 148A (legal section), Ward 7(1) (administrative unit), ₹18,40,000/- (income amount). These must NOT be redacted.

Income Tax Officer, Ward 7(1)
Hyderabad""",
        "pii_present": [
            {"type": "NAME", "value": "Srinivas Rao Venugopal"},
            {"type": "ADDRESS", "value": "24, Banjara Hills Road No. 12, Hyderabad — 500034"},
            {"type": "PAN", "value": "SRNVG6655T"},
            {"type": "AADHAAR", "value": "2244 6688 0011"},
            {"type": "DOB", "value": "01/01/1969"},
            {"type": "PHONE", "value": "9959001234"},
            {"type": "EMAIL", "value": "srinivas.venugopal.hyd@outlook.com"},
            {"type": "BANK_ACCOUNT", "value": "62104567890"},
            {"type": "IFSC", "value": "HDFC0002345"},
        ],
        "expected_redacted": """OFFICE OF THE INCOME TAX OFFICER
Ward 7(1), Hyderabad
Notice Under Section 148A — Re-Opening of Assessment
Ref: ITO/HYD/W7/2024/148A/003412
Date: 03 December 2024

To: [REDACTED_NAME]
Address: [REDACTED_ADDRESS]
PAN: [REDACTED_PAN]
Aadhaar: [REDACTED_AADHAAR]
DOB: [REDACTED_DOB]
Mobile: [REDACTED_PHONE]
Email: [REDACTED_EMAIL]

Sub: Notice for reassessment — Undisclosed income from online platform

Dear [REDACTED_NAME],

This office has reason to believe that income escaped assessment for AY 2022-23. Our information source indicates that [REDACTED_NAME] received payments from a freelance platform totalling ₹18,40,000/- during FY 2021-22, which was not reflected in the return filed by [REDACTED_NAME].

Platform transaction reference: ORDER-2022-PLAT-430512109876
IMPORTANT: 430512109876 is a 12-digit platform order ID, NOT an Aadhaar number. It must NOT be redacted.

The bank account from which TDS was deducted: [REDACTED_BANK_ACCOUNT] | IFSC: [REDACTED_IFSC] (HDFC Bank, Banjara Hills)

You, [REDACTED_NAME], are directed to appear before this office on 20 December 2024 and produce all financial records, bank statements, and contracts related to the above.

Failure by [REDACTED_NAME] to comply will result in best-judgment assessment under Section 144.

Please note: The non-PII reference numbers in this notice are: FY 2021-22 (financial year), AY 2022-23 (assessment year), Section 148A (legal section), Ward 7(1) (administrative unit), ₹18,40,000/- (income amount). These must NOT be redacted.

Income Tax Officer, Ward 7(1)
Hyderabad""",
    },

]