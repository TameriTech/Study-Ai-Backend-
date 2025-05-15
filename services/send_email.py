from sqlalchemy.orm import Session
from fastapi import HTTPException
from utils.email import send_email  # you'll need to implement this
from database.models import User


async def send_email_to_all_users(db: Session, subject: str, body: str, button_url: str = None, button_text: str = None):
    """Send email to all users with retry logic"""
    users = db.query(User).all()  # Fetch all users
    failed_users = []

    for user in users:
        # First attempt to send the email
        success = await send_email(
            recipient=user.email,
            subject=subject,
            body=body,
            button_url=button_url,
            button_text=button_text
        )

        # If the first attempt fails, try again
        if not success:
            print(f"First attempt failed for {user.email}. Retrying...")
            success = await send_email(
                recipient=user.email,
                subject=subject,
                body=body,
                button_url=button_url,
                button_text=button_text
            )

        # If it fails again, move to the next user
        if not success:
            print(f"Second attempt failed for {user.email}. Moving to the next user.")
            failed_users.append(user.email)

    return {"message": "Emails sent to all users.", "failed_users": failed_users}
