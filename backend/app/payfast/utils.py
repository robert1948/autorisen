import hashlib
import urllib.parse

import httpx

from .config import PAYFAST_CFG


def _normalize(params: dict) -> dict:
    # drop None and empty strings
    return {k: v for k, v in params.items() if v is not None and v != ""}

def build_signature(params: dict) -> str:
    # sort, urlencode (space as +), append passphrase, md5
    clean = _normalize(params)
    query = urllib.parse.urlencode(clean, doseq=True)
    if PAYFAST_CFG["passphrase"]:
        query = f"{query}&passphrase={urllib.parse.quote(PAYFAST_CFG['passphrase'])}"
    return hashlib.md5(query.encode("utf-8")).hexdigest()

def host() -> str:
    return PAYFAST_CFG["base"]

async def validate_itn_with_payfast(raw_body: bytes) -> bool:
    # PayFast docs: POST back the exact payload to /eng/query/validate
    url = f"{host()}/eng/query/validate"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(url, content=raw_body, headers=headers)
    return r.text.strip() == "VALID"
