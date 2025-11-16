from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any, List
from app.utils.log_util import logger
import json
import os
from datetime import datetime

router = APIRouter(prefix="/api/settings", tags=["settings"])

# In-memory storage for demo purposes
# In production, this should be replaced with a database
SETTINGS_FILE = "./project/user_settings.json"

# Pydantic models for request/response validation
class UserProfile(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    avatar: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = None
    timezone: Optional[str] = "UTC"
    language: Optional[str] = "en"

class PasswordChange(BaseModel):
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

class TwoFactorAuth(BaseModel):
    enabled: bool
    method: Optional[str] = "app"  # app, sms, email

class AccountDeletion(BaseModel):
    password: str
    confirmation_text: str
    reason: Optional[str] = None

class PrivacySettings(BaseModel):
    data_collection: bool = True
    analytics: bool = True
    personalization: bool = True
    share_usage_data: bool = False

class NotificationPreferences(BaseModel):
    email_enabled: bool = True
    push_enabled: bool = True
    in_app_enabled: bool = True
    
    # Email notification categories
    email_security_alerts: bool = True
    email_system_updates: bool = True
    email_task_updates: bool = True
    email_weekly_summary: bool = False
    email_marketing: bool = False
    
    # Push notification categories
    push_security_alerts: bool = True
    push_system_updates: bool = False
    push_task_updates: bool = True
    
    # In-app notification categories
    inapp_security_alerts: bool = True
    inapp_system_updates: bool = True
    inapp_task_updates: bool = True
    
    # Notification timing
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[str] = "22:00"
    quiet_hours_end: Optional[str] = "08:00"
    
    # Delivery preferences
    notification_frequency: str = "instant"  # instant, hourly, daily, weekly
    digest_enabled: bool = False

class SessionInfo(BaseModel):
    session_id: str
    device: str
    location: str
    last_active: str
    current: bool = False


def load_settings() -> Dict[str, Any]:
    """Load settings from file"""
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            return get_default_settings()
    return get_default_settings()


def save_settings(settings: Dict[str, Any]) -> None:
    """Save settings to file"""
    try:
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save settings: {str(e)}")


def get_default_settings() -> Dict[str, Any]:
    """Get default settings"""
    return {
        "profile": {
            "name": "San Jin",
            "email": "mathmodel@mathmodel.com",
            "avatar": "https://github.com/jihe520.png",
            "bio": "",
            "phone": "",
            "timezone": "UTC",
            "language": "en"
        },
        "security": {
            "two_factor_enabled": False,
            "two_factor_method": "app",
            "password_last_changed": datetime.now().isoformat()
        },
        "privacy": {
            "data_collection": True,
            "analytics": True,
            "personalization": True,
            "share_usage_data": False
        },
        "notifications": {
            "email_enabled": True,
            "push_enabled": True,
            "in_app_enabled": True,
            "email_security_alerts": True,
            "email_system_updates": True,
            "email_task_updates": True,
            "email_weekly_summary": False,
            "email_marketing": False,
            "push_security_alerts": True,
            "push_system_updates": False,
            "push_task_updates": True,
            "inapp_security_alerts": True,
            "inapp_system_updates": True,
            "inapp_task_updates": True,
            "quiet_hours_enabled": False,
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "08:00",
            "notification_frequency": "instant",
            "digest_enabled": False
        },
        "sessions": []
    }


# User Profile Endpoints
@router.get("/profile")
async def get_profile() -> UserProfile:
    """Get user profile"""
    settings = load_settings()
    return UserProfile(**settings.get("profile", {}))


@router.put("/profile")
async def update_profile(profile: UserProfile) -> Dict[str, Any]:
    """Update user profile"""
    try:
        settings = load_settings()
        settings["profile"] = profile.model_dump()
        save_settings(settings)
        
        logger.info(f"Profile updated for user: {profile.email}")
        return {
            "success": True,
            "message": "Profile updated successfully",
            "data": profile.model_dump()
        }
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Password Management Endpoints
@router.post("/password/change")
async def change_password(password_data: PasswordChange) -> Dict[str, Any]:
    """Change user password"""
    # Validate passwords match
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(status_code=400, detail="New passwords do not match")
    
    # In production, verify current_password against database
    # For demo purposes, we'll accept any current password
    
    try:
        settings = load_settings()
        settings["security"]["password_last_changed"] = datetime.now().isoformat()
        save_settings(settings)
        
        logger.info("Password changed successfully")
        return {
            "success": True,
            "message": "Password changed successfully"
        }
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Two-Factor Authentication Endpoints
@router.get("/security/2fa")
async def get_2fa_status() -> Dict[str, Any]:
    """Get two-factor authentication status"""
    settings = load_settings()
    security = settings.get("security", {})
    return {
        "enabled": security.get("two_factor_enabled", False),
        "method": security.get("two_factor_method", "app")
    }


@router.put("/security/2fa")
async def update_2fa(two_factor: TwoFactorAuth) -> Dict[str, Any]:
    """Enable/disable two-factor authentication"""
    try:
        settings = load_settings()
        settings["security"]["two_factor_enabled"] = two_factor.enabled
        settings["security"]["two_factor_method"] = two_factor.method
        save_settings(settings)
        
        logger.info(f"2FA {'enabled' if two_factor.enabled else 'disabled'}")
        return {
            "success": True,
            "message": f"Two-factor authentication {'enabled' if two_factor.enabled else 'disabled'} successfully",
            "data": two_factor.model_dump()
        }
    except Exception as e:
        logger.error(f"Error updating 2FA: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Session Management Endpoints
@router.get("/security/sessions")
async def get_active_sessions() -> List[SessionInfo]:
    """Get all active sessions"""
    settings = load_settings()
    sessions = settings.get("sessions", [])
    
    # Add mock sessions for demo if none exist
    if not sessions:
        sessions = [
            {
                "session_id": "sess_001",
                "device": "Chrome on Windows",
                "location": "Beijing, China",
                "last_active": datetime.now().isoformat(),
                "current": True
            },
            {
                "session_id": "sess_002",
                "device": "Safari on iPhone",
                "location": "Shanghai, China",
                "last_active": "2024-01-15T10:30:00",
                "current": False
            }
        ]
    
    return [SessionInfo(**session) for session in sessions]


@router.delete("/security/sessions/{session_id}")
async def revoke_session(session_id: str) -> Dict[str, Any]:
    """Revoke a specific session"""
    try:
        settings = load_settings()
        sessions = settings.get("sessions", [])
        sessions = [s for s in sessions if s.get("session_id") != session_id]
        settings["sessions"] = sessions
        save_settings(settings)
        
        logger.info(f"Session revoked: {session_id}")
        return {
            "success": True,
            "message": "Session revoked successfully"
        }
    except Exception as e:
        logger.error(f"Error revoking session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Privacy Settings Endpoints
@router.get("/privacy")
async def get_privacy_settings() -> PrivacySettings:
    """Get privacy settings"""
    settings = load_settings()
    return PrivacySettings(**settings.get("privacy", {}))


@router.put("/privacy")
async def update_privacy_settings(privacy: PrivacySettings) -> Dict[str, Any]:
    """Update privacy settings"""
    try:
        settings = load_settings()
        settings["privacy"] = privacy.model_dump()
        save_settings(settings)
        
        logger.info("Privacy settings updated")
        return {
            "success": True,
            "message": "Privacy settings updated successfully",
            "data": privacy.model_dump()
        }
    except Exception as e:
        logger.error(f"Error updating privacy settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Account Deletion Endpoint
@router.post("/account/delete")
async def delete_account(deletion_data: AccountDeletion) -> Dict[str, Any]:
    """Delete user account"""
    # Verify confirmation text
    if deletion_data.confirmation_text != "DELETE":
        raise HTTPException(
            status_code=400, 
            detail="Invalid confirmation text. Please type 'DELETE' to confirm."
        )
    
    # In production, verify password against database
    # For demo purposes, we'll accept any password
    
    try:
        # Log the deletion request
        logger.warning(f"Account deletion requested. Reason: {deletion_data.reason}")
        
        # In production, this would:
        # 1. Mark account for deletion
        # 2. Schedule data cleanup
        # 3. Send confirmation email
        # 4. Log out user
        
        return {
            "success": True,
            "message": "Account deletion request submitted. Your account will be deleted within 30 days.",
            "deletion_date": (datetime.now()).isoformat()
        }
    except Exception as e:
        logger.error(f"Error processing account deletion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Notification Preferences Endpoints
@router.get("/notifications")
async def get_notification_preferences() -> NotificationPreferences:
    """Get notification preferences"""
    settings = load_settings()
    return NotificationPreferences(**settings.get("notifications", {}))


@router.put("/notifications")
async def update_notification_preferences(
    notifications: NotificationPreferences
) -> Dict[str, Any]:
    """Update notification preferences"""
    try:
        settings = load_settings()
        settings["notifications"] = notifications.model_dump()
        save_settings(settings)
        
        logger.info("Notification preferences updated")
        return {
            "success": True,
            "message": "Notification preferences updated successfully",
            "data": notifications.model_dump()
        }
    except Exception as e:
        logger.error(f"Error updating notification preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Get all settings at once
@router.get("/all")
async def get_all_settings() -> Dict[str, Any]:
    """Get all settings"""
    return load_settings()


# Reset settings to default
@router.post("/reset")
async def reset_settings() -> Dict[str, Any]:
    """Reset all settings to default"""
    try:
        default_settings = get_default_settings()
        save_settings(default_settings)
        
        logger.info("Settings reset to default")
        return {
            "success": True,
            "message": "Settings reset to default successfully",
            "data": default_settings
        }
    except Exception as e:
        logger.error(f"Error resetting settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))
