from fastapi import Request, HTTPException
import hmac
import hashlib

from avaris.defaults import Secrets


async def validate_signature(request: Request):
    """
    Dependency that validates the request's signature or allows the request if the LISTENER_KEY is None.
    """
    if Secrets.LISTENER_KEY is None:
        # If SECRET_TOKEN is None, bypass signature check
        return True

    signature = request.headers.get('x-hub-signature')

    if signature is None or '=' not in signature:
        raise HTTPException(
            status_code=403,
            detail="Signature required and must be formatted correctly.")

    sha_name, signature_hash = signature.split('=')
    if sha_name.lower() != 'sha1':
        raise HTTPException(status_code=501,
                            detail="Hash algorithm not supported.")

    body = await request.body()
    encoded_bytes = Secrets.LISTENER_KEY.encode()
    mac = hmac.new(encoded_bytes,
                   msg=body,
                   digestmod=hashlib.sha1)  # Ensure LISTENER_KEY is bytes

    if not hmac.compare_digest(mac.hexdigest(), signature_hash):
        raise HTTPException(status_code=403, detail="Invalid signature.")

    return True
