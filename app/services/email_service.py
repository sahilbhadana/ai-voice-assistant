"""Email notification service for appointment reminders and confirmations."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "noreply@hospital.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your_password_here")
SENDER_NAME = os.getenv("SENDER_NAME", "City Hospital")


def send_email(recipient_email: str, subject: str, html_content: str, text_content: str = None):
    """
    Send an email with HTML content.
    
    Args:
        recipient_email: Email address of recipient
        subject: Email subject
        html_content: HTML body of email
        text_content: Plain text fallback (optional)
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
        message["To"] = recipient_email

        # Attach plain text version (fallback)
        if text_content:
            part1 = MIMEText(text_content, "plain")
            message.attach(part1)

        # Attach HTML version
        part2 = MIMEText(html_content, "html")
        message.attach(part2)

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, message.as_string())

        logger.info(f"✅ Email sent to {recipient_email}: {subject}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to send email to {recipient_email}: {str(e)}")
        return False


def send_booking_confirmation(patient_name: str, patient_email: str, doctor_name: str, 
                              appointment_date: str, appointment_time: str, 
                              location: str, appointment_id: str, language: str = "en"):
    """Send booking confirmation email."""
    
    if language == "hi":
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="background-color: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: 0 auto;">
                    
                    <h2 style="color: #2c3e50; text-align: center;">✅ अपॉइंटमेंट पुष्टि</h2>
                    
                    <p>नमस्ते <strong>{patient_name}</strong>,</p>
                    
                    <p>आपका अपॉइंटमेंट सफलतापूर्वक बुक हो गया है!</p>
                    
                    <div style="background-color: #ecf0f1; padding: 20px; border-left: 4px solid #3498db; margin: 20px 0;">
                        <p><strong>📅 तारीख:</strong> {appointment_date}</p>
                        <p><strong>⏰ समय:</strong> {appointment_time}</p>
                        <p><strong>👨‍⚕️ डॉक्टर:</strong> {doctor_name}</p>
                        <p><strong>📍 स्थान:</strong> {location}</p>
                        <p><strong>🎫 पुष्टिकरण ID:</strong> <code>{appointment_id}</code></p>
                    </div>
                    
                    <h4 style="color: #2c3e50;">क्या लाना है:</h4>
                    <ul>
                        <li>वैध पहचान पत्र</li>
                        <li>बीमा कार्ड (यदि लागू हो)</li>
                        <li>मेडिकल इतिहास दस्तावेज</li>
                    </ul>
                    
                    <h4 style="color: #2c3e50;">रद्द या पुनर्निर्धारण करना है?</h4>
                    <p>हमें <strong>+1-XXX-XXXX-XXXX</strong> पर कॉल करें या इस ईमेल का जवाब दें।</p>
                    <p>⚠️ कृपया रद्दीकरण शुल्क से बचने के लिए अपने अपॉइंटमेंट से कम से कम 24 घंटे पहले रद्द करें।</p>
                    
                    <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 20px 0;">
                    
                    <p style="color: #7f8c8d; font-size: 12px; text-align: center;">
                        🏥 सिटी अस्पताल | आपातकाल: +1-XXX-XXXX-XXXX<br>
                        यह एक स्वचालित संदेश है। कृपया संवेदनशील जानकारी के साथ जवाब न दें।
                    </p>
                </div>
            </body>
        </html>
        """
        
        text_content = f"""
        अपॉइंटमेंट पुष्टि
        
        नमस्ते {patient_name},
        
        आपका अपॉइंटमेंट सफलतापूर्वक बुक हो गया है!
        
        तारीख: {appointment_date}
        समय: {appointment_time}
        डॉक्टर: {doctor_name}
        स्थान: {location}
        पुष्टिकरण ID: {appointment_id}
        
        क्या लाना है:
        - वैध पहचान पत्र
        - बीमा कार्ड (यदि लागू हो)
        - मेडिकल इतिहास दस्तावेज
        
        रद्द या पुनर्निर्धारण करना है?
        हमें +1-XXX-XXXX-XXXX पर कॉल करें
        
        सिटी अस्पताल
        """
        
        subject = "अपॉइंटमेंट पुष्टि - सिटी अस्पताल"
    else:
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="background-color: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: 0 auto;">
                    
                    <h2 style="color: #2c3e50; text-align: center;">✅ Appointment Confirmed</h2>
                    
                    <p>Hi <strong>{patient_name}</strong>,</p>
                    
                    <p>Your appointment has been successfully booked!</p>
                    
                    <div style="background-color: #ecf0f1; padding: 20px; border-left: 4px solid #3498db; margin: 20px 0;">
                        <p><strong>📅 Date:</strong> {appointment_date}</p>
                        <p><strong>⏰ Time:</strong> {appointment_time}</p>
                        <p><strong>👨‍⚕️ Doctor:</strong> {doctor_name}</p>
                        <p><strong>📍 Location:</strong> {location}</p>
                        <p><strong>🎫 Confirmation ID:</strong> <code>{appointment_id}</code></p>
                    </div>
                    
                    <h4 style="color: #2c3e50;">What to bring:</h4>
                    <ul>
                        <li>Valid ID</li>
                        <li>Insurance card (if applicable)</li>
                        <li>Medical history documents</li>
                    </ul>
                    
                    <h4 style="color: #2c3e50;">Need to cancel or reschedule?</h4>
                    <p>Call us at <strong>+1-XXX-XXXX-XXXX</strong> or reply to this email.</p>
                    <p>⚠️ Please cancel at least 24 hours before your appointment to avoid cancellation fees.</p>
                    
                    <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 20px 0;">
                    
                    <p style="color: #7f8c8d; font-size: 12px; text-align: center;">
                        🏥 City Hospital | Emergency: +1-XXX-XXXX-XXXX<br>
                        This is an automated message. Please do not reply with sensitive information.
                    </p>
                </div>
            </body>
        </html>
        """
        
        text_content = f"""
        APPOINTMENT CONFIRMED
        
        Hi {patient_name},
        
        Your appointment has been successfully booked!
        
        Date: {appointment_date}
        Time: {appointment_time}
        Doctor: {doctor_name}
        Location: {location}
        Confirmation ID: {appointment_id}
        
        What to bring:
        - Valid ID
        - Insurance card (if applicable)
        - Medical history documents
        
        Need to cancel or reschedule?
        Call us at +1-XXX-XXXX-XXXX
        
        City Hospital
        """
        
        subject = "Appointment Confirmed - City Hospital"
    
    return send_email(patient_email, subject, html_content, text_content)


def send_reminder_24h(patient_name: str, patient_email: str, doctor_name: str, 
                      appointment_date: str, appointment_time: str, location: str, appointment_id: str):
    """Send 24-hour reminder email."""
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
            <div style="background-color: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: 0 auto;">
                
                <h2 style="color: #2c3e50; text-align: center;">📅 Appointment Reminder</h2>
                
                <p>Hi <strong>{patient_name}</strong>,</p>
                
                <p style="color: #e74c3c; font-weight: bold;">Your appointment is <strong>TOMORROW!</strong></p>
                
                <div style="background-color: #fff3cd; padding: 20px; border-left: 4px solid #ffc107; margin: 20px 0;">
                    <p><strong>📅 Date:</strong> {appointment_date}</p>
                    <p><strong>⏰ Time:</strong> {appointment_time}</p>
                    <p><strong>👨‍⚕️ Doctor:</strong> {doctor_name}</p>
                    <p><strong>📍 Location:</strong> {location}</p>
                    <p><strong>🎫 Confirmation ID:</strong> {appointment_id}</p>
                </div>
                
                <h4 style="color: #2c3e50;">⏰ Arriving Early?</h4>
                <p>Please arrive <strong>15 minutes early</strong> for check-in.</p>
                
                <h4 style="color: #2c3e50;">❌ Need to Cancel?</h4>
                <p><strong>Call us immediately at +1-XXX-XXXX-XXXX</strong> to avoid cancellation fees.</p>
                <p style="color: #e74c3c;">Cancellations within 24 hours may incur fees.</p>
                
                <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 20px 0;">
                
                <p style="color: #7f8c8d; font-size: 12px; text-align: center;">
                    🏥 City Hospital<br>
                    See you tomorrow!
                </p>
            </div>
        </body>
    </html>
    """
    
    text_content = f"""
    APPOINTMENT REMINDER - TOMORROW!
    
    Hi {patient_name},
    
    Your appointment is TOMORROW!
    
    Date: {appointment_date}
    Time: {appointment_time}
    Doctor: {doctor_name}
    Location: {location}
    Confirmation ID: {appointment_id}
    
    Please arrive 15 minutes early.
    
    Need to cancel? Call us at +1-XXX-XXXX-XXXX
    
    City Hospital
    """
    
    return send_email(patient_email, "⏰ Appointment Reminder - Tomorrow!", html_content, text_content)


def send_reminder_1h(patient_name: str, patient_email: str, doctor_name: str, 
                     appointment_time: str, location: str):
    """Send 1-hour before appointment email."""
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
            <div style="background-color: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: 0 auto;">
                
                <h2 style="color: #e74c3c; text-align: center;">⏰ Your Appointment is in 1 HOUR!</h2>
                
                <p>Hi <strong>{patient_name}</strong>,</p>
                
                <div style="background-color: #f8d7da; padding: 20px; border-left: 4px solid #dc3545; margin: 20px 0;">
                    <p><strong>⏰ Time:</strong> {appointment_time}</p>
                    <p><strong>👨‍⚕️ Doctor:</strong> {doctor_name}</p>
                    <p><strong>📍 Location:</strong> {location}</p>
                </div>
                
                <p style="color: #dc3545; font-weight: bold;">🚨 Please be ready to come in!</p>
                
                <p>If you cannot make it, <strong>call us immediately</strong> at <strong>+1-XXX-XXXX-XXXX</strong></p>
                
                <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 20px 0;">
                
                <p style="color: #7f8c8d; font-size: 12px; text-align: center;">
                    🏥 City Hospital
                </p>
            </div>
        </body>
    </html>
    """
    
    text_content = f"""
    URGENT: Your appointment is in 1 HOUR!
    
    Hi {patient_name},
    
    Your appointment with {doctor_name} is in 1 HOUR!
    
    Time: {appointment_time}
    Location: {location}
    
    If you cannot make it, call +1-XXX-XXXX-XXXX immediately.
    
    City Hospital
    """
    
    return send_email(patient_email, "⏰ URGENT: Appointment in 1 HOUR!", html_content, text_content)


def send_noshow_followup(patient_name: str, patient_email: str, doctor_name: str, 
                         appointment_date: str, appointment_time: str):
    """Send follow-up email for no-show appointments."""
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
            <div style="background-color: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: 0 auto;">
                
                <h2 style="color: #e74c3c; text-align: center;">❌ We Missed You Today</h2>
                
                <p>Hi <strong>{patient_name}</strong>,</p>
                
                <p>You did not show up for your appointment today with <strong>{doctor_name}</strong> at <strong>{appointment_time}</strong>.</p>
                
                <div style="background-color: #f8d7da; padding: 20px; border-left: 4px solid #dc3545; margin: 20px 0;">
                    <p><strong>📅 Date:</strong> {appointment_date}</p>
                    <p><strong>⏰ Time:</strong> {appointment_time}</p>
                    <p><strong>👨‍⚕️ Doctor:</strong> {doctor_name}</p>
                </div>
                
                <h4 style="color: #2c3e50;">What now?</h4>
                <ul>
                    <li>If you had an emergency, please call us to explain</li>
                    <li>If you need to reschedule, we have availability this week</li>
                    <li>Repeated no-shows may result in account suspension</li>
                </ul>
                
                <h4 style="color: #2c3e50;">🔄 Reschedule your appointment:</h4>
                <p>Call us at <strong>+1-XXX-XXXX-XXXX</strong> or reply to this email.</p>
                
                <p style="color: #7f8c8d;">We look forward to seeing you soon!</p>
                
                <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 20px 0;">
                
                <p style="color: #7f8c8d; font-size: 12px; text-align: center;">
                    🏥 City Hospital
                </p>
            </div>
        </body>
    </html>
    """
    
    text_content = f"""
    WE MISSED YOU TODAY
    
    Hi {patient_name},
    
    You did not show up for your appointment today with {doctor_name} at {appointment_time}.
    
    Date: {appointment_date}
    Time: {appointment_time}
    Doctor: {doctor_name}
    
    If you had an emergency, please call us.
    If you need to reschedule, call +1-XXX-XXXX-XXXX
    
    Repeated no-shows may result in account suspension.
    
    City Hospital
    """
    
    return send_email(patient_email, "❌ We Missed You - Please Reschedule", html_content, text_content)


def send_cancellation_confirmation(patient_name: str, patient_email: str, doctor_name: str, 
                                   appointment_date: str, appointment_time: str):
    """Send cancellation confirmation email."""
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
            <div style="background-color: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: 0 auto;">
                
                <h2 style="color: #27ae60; text-align: center;">✅ Appointment Cancelled</h2>
                
                <p>Hi <strong>{patient_name}</strong>,</p>
                
                <p>Your appointment has been <strong>successfully cancelled</strong>.</p>
                
                <div style="background-color: #d4edda; padding: 20px; border-left: 4px solid #28a745; margin: 20px 0;">
                    <p><strong>📅 Date:</strong> {appointment_date}</p>
                    <p><strong>⏰ Time:</strong> {appointment_time}</p>
                    <p><strong>👨‍⚕️ Doctor:</strong> {doctor_name}</p>
                    <p style="color: #155724; margin-top: 10px;">✅ Slot is now available for other patients</p>
                </div>
                
                <h4 style="color: #2c3e50;">Need to book another appointment?</h4>
                <p>Call us at <strong>+1-XXX-XXXX-XXXX</strong> or reply to this email.</p>
                
                <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 20px 0;">
                
                <p style="color: #7f8c8d; font-size: 12px; text-align: center;">
                    🏥 City Hospital
                </p>
            </div>
        </body>
    </html>
    """
    
    text_content = f"""
    APPOINTMENT CANCELLED
    
    Hi {patient_name},
    
    Your appointment has been successfully cancelled.
    
    Date: {appointment_date}
    Time: {appointment_time}
    Doctor: {doctor_name}
    
    Need to book another appointment?
    Call +1-XXX-XXXX-XXXX
    
    City Hospital
    """
    
    return send_email(patient_email, "✅ Appointment Cancelled", html_content, text_content)
