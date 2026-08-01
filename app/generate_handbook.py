from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

OUTPUT_PATH = "data/documents/memos-2026.pdf"

os.makedirs("data/documents", exist_ok=True)

content = [
    "COMPANY MEMOS",
    "",

    "Memo 1: Office Renovation",
    "Date: January 15, 2025",
    "The Facilities Department will begin office renovations on February 1, 2025. Renovation work will be completed in phases to minimize disruption. Employees located on the third floor will be temporarily relocated to the fourth floor during construction. Please keep personal belongings secured and follow directional signs throughout the building.",
    "",
    "Meeting rooms A and B will be unavailable during the renovation period. Employees should reserve alternative meeting rooms using the Outlook booking system.",
    "",

    "Memo 2: Password Security",
    "Date: February 3, 2025",
    "To improve cybersecurity, all employees must update their passwords every ninety days. Passwords should contain at least twelve characters including uppercase letters, lowercase letters, numbers, and special symbols. Password sharing is strictly prohibited.",
    "",
    "Multi-factor authentication (MFA) is mandatory for all business applications including email, VPN, Microsoft Teams, and HR systems.",
    "",

    "Memo 3: Quarterly Town Hall",
    "Date: March 10, 2025",
    "The CEO will host the quarterly town hall meeting on March 28 at 10:00 AM in the main conference hall. Employees working remotely may attend using Microsoft Teams. Department leaders will present business updates, financial performance, customer achievements, and upcoming strategic initiatives.",
    "",
    "Employees are encouraged to submit questions before the meeting through the HR portal.",
    "",

    "Memo 4: Annual Performance Review",
    "Date: April 5, 2025",
    "Managers will begin annual performance reviews on April 15. Employees should complete their self-assessment forms before April 10. Reviews will focus on goal achievement, technical competencies, teamwork, communication, innovation, and professional development.",
    "",
    "Managers should schedule one-hour meetings with each team member to discuss performance and career development plans.",
    "",

    "Memo 5: IT System Maintenance",
    "Date: May 12, 2025",
    "The IT Department will perform scheduled maintenance on company servers on Saturday from 9:00 PM until 2:00 AM. During this period, VPN access, email services, and internal applications may be temporarily unavailable.",
    "",
    "Employees are advised to save their work and log out before the maintenance window begins.",
    "",

    "Memo 6: Remote Work Guidelines",
    "Date: June 8, 2025",
    "Employees approved for remote work must remain available during standard business hours and attend all scheduled meetings. Company laptops should be connected to the corporate VPN whenever accessing internal resources.",
    "",
    "Sensitive company information should never be stored on personal devices or cloud storage services.",
    "",

    "Memo 7: Employee Wellness Program",
    "Date: July 2, 2025",
    "The Human Resources Department is launching a new wellness program designed to promote employee health and well-being. The program includes free annual health screenings, fitness challenges, mental health counseling, nutrition workshops, and stress management sessions.",
    "",
    "Employees who participate in wellness activities may qualify for additional recognition awards.",
    "",

    "Memo 8: Expense Reimbursement",
    "Date: August 14, 2025",
    "Business travel expenses must be submitted within thirty days of travel completion. Original receipts are required for reimbursement. Expenses without supporting documentation may be rejected by the Finance Department.",
    "",
    "Employees should use the online expense management system for all reimbursement requests.",
    "",

    "Memo 9: Data Privacy Reminder",
    "Date: September 18, 2025",
    "Employees handling customer information must comply with company privacy policies and applicable data protection regulations. Customer records should only be accessed for legitimate business purposes.",
    "",
    "Any suspected data breach should be reported immediately to the Information Security Team.",
    "",

    "Memo 10: Holiday Schedule",
    "Date: October 20, 2025",
    "The company holiday calendar for the upcoming year has been published on the HR portal. Managers should ensure adequate staffing during holiday periods while allowing employees to utilize their annual leave fairly.",
    "",
    "Employees planning extended vacations should submit leave requests as early as possible to avoid scheduling conflicts.",
    "",

    "End of Company Memos",
    "These memos serve as official internal communications. Employees are responsible for reviewing company announcements regularly and complying with all instructions communicated through official memos."
]

def create_pdf(path):
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter

    y = height - 50

    for line in content:
        c.drawString(50, y, line)
        y -= 20

        if y < 50:
            c.showPage()
            y = height - 50

    c.save()

if __name__ == "__main__":
    create_pdf(OUTPUT_PATH)
    print(f"PDF created at: {OUTPUT_PATH}")