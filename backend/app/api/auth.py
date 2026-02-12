"""OAuth authentication routes."""
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.core.config import get_settings
from app.services.oauth import oauth, create_access_token, get_or_create_user_from_google, verify_token

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google/login")
async def google_login(request: Request):
    """Initiate Google OAuth flow."""
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Handle Google OAuth callback."""
    try:
        # Get the authorization token
        token = await oauth.google.authorize_access_token(request)
        
        # Get user info from Google
        user_info = token.get('userinfo')
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info from Google")
        
        # Get or create user in database
        user = await get_or_create_user_from_google(db, user_info)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        # Debug logging
        print(f"✅ OAuth Success: User {user.email} logged in")
        print(f"✅ JWT Token created: {access_token[:50]}...")
        print(f"✅ Redirecting to: {settings.FRONTEND_URL}/auth/callback?token=...")
        
        # Redirect to frontend with token
        frontend_url = f"{settings.FRONTEND_URL}/auth/callback?token={access_token}"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        # Debug logging
        import traceback
        print(f"❌ OAuth Error: {str(e)}")
        print(f"❌ Error Type: {type(e).__name__}")
        print(f"❌ Traceback:")
        traceback.print_exc()
        # Redirect to frontend with error
        frontend_url = f"{settings.FRONTEND_URL}/login?error=oauth_failed"
        return RedirectResponse(url=frontend_url)


@router.get("/me")
async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated user info."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        # Verify token and get user info
        user = await verify_token(token, db)
        
        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
