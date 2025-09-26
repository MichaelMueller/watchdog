from typing import Optional

from pydantic import BaseModel, HttpUrl, Field


class OidcConfig(BaseModel):
    issuer: str = Field(..., pattern=r'^https?://.+')
    client_id: str
    client_s: str
    tenant_id: Optional[str] = None  # For multi-tenant providers like Azure AD
    
    # allowed emails (or sub, or whatever claim you want)
    allowed_users: Optional[list[str]] = None
    allowed_o365_groups: Optional[list[str]] = None

    