import request from "@/utils/request";

// Types
export interface UserProfile {
	name: string;
	email: string;
	avatar: string;
	bio: string;
	phone: string;
	timezone: string;
	language: string;
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
	quiet_hours_start: string;
	quiet_hours_end: string;
	notification_frequency: string;
	digest_enabled: boolean;
}

export interface PrivacySettings {
	data_collection: boolean;
	analytics: boolean;
	personalization: boolean;
	share_usage_data: boolean;
}

export interface TwoFactorAuth {
	enabled: boolean;
	method: string;
}

export interface SessionInfo {
	session_id: string;
	device: string;
	location: string;
	ip_address: string;
	last_active: string;
	current: boolean;
}

export interface PasswordChange {
	current_password: string;
	new_password: string;
	confirm_password: string;
}

export interface AccountDeletion {
	password: string;
	confirmation_text: string;
	reason: string;
}

// API Functions

// Profile
export function getProfile() {
	return request.get<UserProfile>("/api/settings/profile");
}

export function updateProfile(data: UserProfile) {
	return request.put<{ data: UserProfile; message: string }>(
		"/api/settings/profile",
		data
	);
}

// Notifications
export function getNotificationPreferences() {
	return request.get<NotificationPreferences>("/api/settings/notifications");
}

export function updateNotificationPreferences(data: NotificationPreferences) {
	return request.put<{ data: NotificationPreferences; message: string }>(
		"/api/settings/notifications",
		data
	);
}

// Privacy
export function getPrivacySettings() {
	return request.get<PrivacySettings>("/api/settings/privacy");
}

export function updatePrivacySettings(data: PrivacySettings) {
	return request.put<{ data: PrivacySettings; message: string }>(
		"/api/settings/privacy",
		data
	);
}

// Security
export function get2FAStatus() {
	return request.get<TwoFactorAuth>("/api/settings/security/2fa");
}

export function update2FA(data: { enabled: boolean; method?: string }) {
	return request.put<{ data: TwoFactorAuth; message: string }>(
		"/api/settings/security/2fa",
		data
	);
}

export function changePassword(data: PasswordChange) {
	return request.post<{ message: string }>(
		"/api/settings/password/change",
		data,
	);
}

// Sessions
export function getActiveSessions() {
	return request.get<SessionInfo[]>("/api/settings/security/sessions");
}

export function revokeSession(sessionId: string) {
	return request.delete<{ message: string }>(
		`/api/settings/security/sessions/${sessionId}`
	);
}

// Account
export function deleteAccount(data: AccountDeletion) {
	return request.post<{ message: string }>(
		"/api/settings/account/delete",
		data,
	);
}
