"""Google OAuth service for user authentication."""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from jose import jwt
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import get_settings
from app.models.user import User

settings = get_settings()

# Configure OAuth
oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_or_create_user_from_google(
    db: AsyncSession,
    google_user_info: Dict[str, Any]
) -> User:
    """Get existing user or create new user from Google OAuth data."""
    email = google_user_info.get('email')
    
    # Check if user exists
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()
    
    if user:
        # Update user info if needed
        user.full_name = google_user_info.get('name', user.full_name)
        user.is_verified = google_user_info.get('email_verified', False)
        await db.commit()
        await db.refresh(user)
        return user
    
    # Create new user
    new_user = User(
        email=email,
        full_name=google_user_info.get('name', ''),
        password_hash='',  # No password for OAuth users
        is_active=True,
        is_verified=google_user_info.get('email_verified', False)
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user
