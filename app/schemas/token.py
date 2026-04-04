from pydantic import BaseModel

class TokenResponse(BaseModel):
    """Schema for returning JWT access token after login or refresh."""
    access_token: str
    token_type: str = "bearer"

