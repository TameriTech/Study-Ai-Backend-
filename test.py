from utils.email import send_email

# Example usage
success = send_email(
    to="tembanblaise1@gmail.com",
    subject="Test Email",
    body="Hello from our new email system!"
)

if success:
    print("Email sent!")
else:
    print("Failed to send email")