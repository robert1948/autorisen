import os

def pf_base_url():
    return "https://sandbox.payfast.co.za" if os.getenv("PAYFAST_MODE","sandbox") != "live" \
           else "https://www.payfast.co.za"

PAYFAST_CFG = {
    "merchant_id": os.getenv("PAYFAST_MERCHANT_ID"),
    "merchant_key": os.getenv("PAYFAST_MERCHANT_KEY"),
    "passphrase": os.getenv("PAYFAST_PASSPHRASE", ""),  # required if set on account
    "return_url": os.getenv("PAYFAST_RETURN_URL"),
    "cancel_url": os.getenv("PAYFAST_CANCEL_URL"),
    "notify_url": os.getenv("PAYFAST_NOTIFY_URL"),
    "base": pf_base_url(),
}
