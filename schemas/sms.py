from pydantic import BaseModel, Field


class SMSRequest(BaseModel):
    to: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$',
                    description="Номер телефона в формате E.164")
    body: str = Field(..., min_length=1, max_length=1600,
                      description="Тело сообщения")


class BulkSMSRequest(BaseModel):
    messages: list[SMSRequest]
