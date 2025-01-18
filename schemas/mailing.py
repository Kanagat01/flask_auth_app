from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel


class MailingCreateSchema(BaseModel):
    subject: str
    body: str
    recipient_email: str
    send_at: Optional[datetime] = datetime.now(timezone.utc)

    class Config:
        from_attributes = True
