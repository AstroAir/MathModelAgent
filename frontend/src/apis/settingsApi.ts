import request from "@/utils/request";

// Types
export interface UserProfile {
  name: string;
  email: string;
  avatar?: string;
  bio?: string;
  phone?: string;
  timezone?: string;
  language?: string;
}

export interface PasswordChange {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export interface TwoFactorAuth {
  enabled: boolean;
  method?: string;
}

export interface PrivacySettings {
  data_collection: boolean;
  analytics: boolean;
  personalization: boolean;
  share_usage_data: boolean;
}

export interface NotificationPreferences {
  email_enabled: boolean;
  push_enabled: boolean;
  in_app_enabled: boolean;
  
  email_security_alerts: boolean;
  email_system_updates: boolean;
  email_task_updates: boolean;
  email_weekly_summary: boolean;
  email_marketing: boolean;
  
  push_security_alerts: boolean;
  push_system_updates: boolean;
  push_task_updates: boolean;
  
  inapp_security_alerts: boolean;
  inapp_system_updates: boolean;
  inapp_task_updates: boolean;
  
  quiet_hours_enabled: boolean;
  quiet_hours_start?: string;
  quiet_hours_end?: string;
  
  notification_frequency: string;
  digest_enabled: boolean;
}

export interface SessionInfo {
  session_id: string;
  device: string;
  location: string;
  last_active: string;
  current: boolean;
}

export interface AccountDeletion {
  password: string;
  confirmation_text: string;
  reason?: string;
}

// API Functions

// Profile
export function getProfile() {
  return request.get<UserProfile>("/api/settings/profile");
}

export function updateProfile(profile: UserProfile) {
  return request.put<{ success: boolean; message: string; data: UserProfile }>(
    "/api/settings/profile",
    profile
  );
}

// Password
export function changePassword(passwordData: PasswordChange) {
  return request.post<{ success: boolean; message: string }>(
    "/api/settings/password/change",
    passwordData
  );
}

// Two-Factor Authentication
export function get2FAStatus() {
  return request.get<{ enabled: boolean; method: string }>(
    "/api/settings/security/2fa"
  );
}

export function update2FA(twoFactor: TwoFactorAuth) {
  return request.put<{ success: boolean; message: string; data: TwoFactorAuth }>(
    "/api/settings/security/2fa",
    twoFactor
  );
}

// Sessions
export function getActiveSessions() {
  return request.get<SessionInfo[]>("/api/settings/security/sessions");
}

export function revokeSession(sessionId: string) {
  return request.delete<{ success: boolean; message: string }>(
    `/api/settings/security/sessions/${sessionId}`
  );
}

// Privacy
export function getPrivacySettings() {
  return request.get<PrivacySettings>("/api/settings/privacy");
}

export function updatePrivacySettings(privacy: PrivacySettings) {
  return request.put<{ success: boolean; message: string; data: PrivacySettings }>(
    "/api/settings/privacy",
    privacy
  );
}

// Account Deletion
export function deleteAccount(deletionData: AccountDeletion) {
  return request.post<{ success: boolean; message: string; deletion_date: string }>(
    "/api/settings/account/delete",
    deletionData
  );
}

// Notifications
export function getNotificationPreferences() {
  return request.get<NotificationPreferences>("/api/settings/notifications");
}

export function updateNotificationPreferences(notifications: NotificationPreferences) {
  return request.put<{ success: boolean; message: string; data: NotificationPreferences }>(
    "/api/settings/notifications",
    notifications
  );
}

// All Settings
export function getAllSettings() {
  return request.get<{
    profile: UserProfile;
    security: any;
    privacy: PrivacySettings;
    notifications: NotificationPreferences;
    sessions: SessionInfo[];
  }>("/api/settings/all");
}

export function resetSettings() {
  return request.post<{ success: boolean; message: string; data: any }>(
    "/api/settings/reset"
  );
}
