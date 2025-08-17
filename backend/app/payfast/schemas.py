from pydantic import BaseModel, Field, condecimal

class CreateCheckoutIn(BaseModel):
    m_payment_id: str = Field(..., description="Your internal order id")
    amount: condecimal(gt=0)      # Decimal string OK
    item_name: str
    item_description: str | None = None
    email_address: str | None = None  # buyer email (optional)

class CreateCheckoutOut(BaseModel):
    redirect_url: str

class ITNResult(BaseModel):
    status: str
