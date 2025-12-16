from fastapi import APIRouter, HTTPException
from config.email_config import EmailRequest
from utils.email import send_email  # you'll need to implement this

router = APIRouter(prefix="/api")

@router.post("/send-email/to-all-users", tags=["Send Email"])
async def send_email_route(request: EmailRequest):
    """Endpoint to send a customized email"""
    success = await send_email(
        recipient=request.recipient,
        subject=request.subject,
        body=request.body,
        button_url=request.button_url,
        button_text=request.button_text
    )
    
    if success:
        return {"message": "Email sent successfully"}
    else:
        raise HTTPException(status_code=500, detail="Email sending failed")