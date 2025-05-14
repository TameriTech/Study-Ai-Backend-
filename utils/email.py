from pathlib import Path
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib
from config.email_config import email_settings

async def send_email(recipient: str, subject: str, body: str, 
                   button_url: str = None, button_text: str = None) -> bool:
    """Send beautiful educational email with logo"""
    try:
        # Load template
        template_path = Path("static/email_template.html")
        template_content = template_path.read_text()
        
        # Replace placeholders (simple string replacement)
        html_content = template_content\
            .replace("{{ subject }}", subject)\
            .replace("{{ body }}", body)\
            .replace("{% if button_url and button_text %}", "")\
            .replace("{% endif %}", "")
        
        # Add button if provided
        if button_url and button_text:
            button_html = f"""
            <center>
                <a href="{button_url}" class="button">{button_text}</a>
            </center>
            """
            html_content = html_content.replace('{{ button_url }}', button_url)\
                                     .replace('{{ button_text }}', button_text)\
                                     .replace('<!-- BUTTON_PLACEHOLDER -->', button_html)
        else:
            html_content = html_content.replace('<!-- BUTTON_PLACEHOLDER -->', '')

        msg = MIMEMultipart('related')
        msg['From'] = email_settings.SMTP_FROM
        msg['To'] = recipient
        msg['Subject'] = subject

        # Alternative plain text version
        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)
        msg_alternative.attach(MIMEText(body, 'plain'))
        msg_alternative.attach(MIMEText(html_content, 'html'))

        # Embed logo
        logo_path = Path("static/logo.png")
        with open(logo_path, 'rb') as f:
            logo = MIMEImage(f.read())
            logo.add_header('Content-ID', '<logo>')
            logo.add_header('Content-Disposition', 'inline', filename='logo.png')
            msg.attach(logo)

        # SMTP sending
        with smtplib.SMTP(email_settings.SMTP_HOST, email_settings.SMTP_PORT) as server:
            server.starttls()
            server.login(
                email_settings.SMTP_USERNAME,
                email_settings.SMTP_PASSWORD.get_secret_value()
            )
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        return False