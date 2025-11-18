import type {
	NotificationPreferences,
	PrivacySettings,
	SessionInfo,
	TwoFactorAuth,
	UserProfile,
} from "@/apis/settingsApi";
import {
	get2FAStatus,
	getActiveSessions,
	getNotificationPreferences,
	getPrivacySettings,
	getProfile,
	revokeSession,
	update2FA,
	updateNotificationPreferences,
	updatePrivacySettings,
	updateProfile,
} from "@/apis/settingsApi";
import { useToast } from "@/components/ui/toast/use-toast";
import { defineStore } from "pinia";
import { ref } from "vue";

interface ApiError {
	response?: {
		data?: {
			detail?: string;
		};
	};
}

export const useSettingsStore = defineStore("settings", () => {
	const { toast } = useToast();

	// State
	const profile = ref<UserProfile>({
		name: "San Jin",
		email: "mathmodel@mathmodel.com",
		avatar: "https://github.com/jihe520.png",
		bio: "",
		phone: "",
		timezone: "UTC",
		language: "en",
	});

	const notifications = ref<NotificationPreferences>({
		email_enabled: true,
		push_enabled: true,
		in_app_enabled: true,
		email_security_alerts: true,
		email_system_updates: true,
		email_task_updates: true,
		email_weekly_summary: false,
		email_marketing: false,
		push_security_alerts: true,
		push_system_updates: false,
		push_task_updates: true,
		inapp_security_alerts: true,
		inapp_system_updates: true,
		inapp_task_updates: true,
		quiet_hours_enabled: false,
		quiet_hours_start: "22:00",
		quiet_hours_end: "08:00",
		notification_frequency: "instant",
		digest_enabled: false,
	});

	const privacy = ref<PrivacySettings>({
		data_collection: true,
		analytics: true,
		personalization: true,
		share_usage_data: false,
	});

	const twoFactorAuth = ref<TwoFactorAuth>({
		enabled: false,
		method: "app",
	});

	const sessions = ref<SessionInfo[]>([]);

	const loading = ref(false);
	const saving = ref(false);

	// Actions
	async function loadProfile() {
		try {
			loading.value = true;
			const response = await getProfile();
			profile.value = response.data;
		} catch (error: unknown) {
			const apiError = error as ApiError;
			toast({
				title: "Error",
				description:
					apiError.response?.data?.detail || "Failed to load profile",
				variant: "destructive",
			});
		} finally {
			loading.value = false;
		}
	}

	async function saveProfile(profileData: UserProfile) {
		try {
			saving.value = true;
			const response = await updateProfile(profileData);
			profile.value = response.data.data;
			toast({
				title: "Success",
				description: response.data.message,
			});
			return true;
		} catch (error: unknown) {
			const apiError = error as ApiError;
			toast({
				title: "Error",
				description:
					apiError.response?.data?.detail || "Failed to update profile",
				variant: "destructive",
			});
			return false;
		} finally {
			saving.value = false;
		}
	}

	async function loadNotifications() {
		try {
			loading.value = true;
			const response = await getNotificationPreferences();
			notifications.value = response.data;
		} catch (error: unknown) {
			const apiError = error as ApiError;
			toast({
				title: "Error",
				description:
					apiError.response?.data?.detail ||
					"Failed to load notification preferences",
				variant: "destructive",
			});
		} finally {
			loading.value = false;
		}
	}

	async function saveNotifications(notificationData: NotificationPreferences) {
		try {
			saving.value = true;
			const response = await updateNotificationPreferences(notificationData);
			notifications.value = response.data.data;
			toast({
				title: "Success",
				description: response.data.message,
			});
			return true;
		} catch (error: unknown) {
			const apiError = error as ApiError;
			toast({
				title: "Error",
				description:
					apiError.response?.data?.detail ||
					"Failed to update notification preferences",
				variant: "destructive",
			});
			return false;
		} finally {
			saving.value = false;
		}
	}

	async function loadPrivacy() {
		try {
			loading.value = true;
			const response = await getPrivacySettings();
			privacy.value = response.data;
		} catch (error: unknown) {
			const apiError = error as ApiError;
			toast({
				title: "Error",
				description:
					apiError.response?.data?.detail || "Failed to load privacy settings",
				variant: "destructive",
			});
		} finally {
			loading.value = false;
		}
	}

	async function savePrivacy(privacyData: PrivacySettings) {
		try {
			saving.value = true;
			const response = await updatePrivacySettings(privacyData);
			privacy.value = response.data.data;
			toast({
				title: "Success",
				description: response.data.message,
			});
			return true;
		} catch (error: unknown) {
			const apiError = error as ApiError;
			toast({
				title: "Error",
				description:
					apiError.response?.data?.detail ||
					"Failed to update privacy settings",
				variant: "destructive",
			});
			return false;
		} finally {
			saving.value = false;
		}
	}

	async function load2FAStatus() {
		try {
			const response = await get2FAStatus();
			twoFactorAuth.value = response.data;
		} catch (error: unknown) {
			const apiError = error as ApiError;
			toast({
				title: "Error",
				description:
					apiError.response?.data?.detail || "Failed to load 2FA status",
				variant: "destructive",
			});
		}
	}

	async function toggle2FA(enabled: boolean, method?: string) {
		try {
			saving.value = true;
			const response = await update2FA({ enabled, method });
			twoFactorAuth.value = response.data.data;
			toast({
				title: "Success",
				description: response.data.message,
			});
			return true;
		} catch (error: unknown) {
			const apiError = error as ApiError;
			toast({
				title: "Error",
				description: apiError.response?.data?.detail || "Failed to update 2FA",
				variant: "destructive",
			});
			return false;
		} finally {
			saving.value = false;
		}
	}

	async function loadSessions() {
		try {
			loading.value = true;
			const response = await getActiveSessions();
			sessions.value = response.data;
		} catch (error: unknown) {
			const apiError = error as ApiError;
			toast({
				title: "Error",
				description:
					apiError.response?.data?.detail || "Failed to load sessions",
				variant: "destructive",
			});
		} finally {
			loading.value = false;
		}
	}

	async function terminateSession(sessionId: string) {
		try {
			await revokeSession(sessionId);
			sessions.value = sessions.value.filter((s) => s.session_id !== sessionId);
			toast({
				title: "Success",
				description: "Session terminated successfully",
			});
			return true;
		} catch (error: unknown) {
			const apiError = error as ApiError;
			toast({
				title: "Error",
				description:
					apiError.response?.data?.detail || "Failed to terminate session",
				variant: "destructive",
			});
			return false;
		}
	}

	return {
		profile,
		notifications,
		privacy,
		twoFactorAuth,
		sessions,
		loading,
		saving,
		loadProfile,
		saveProfile,
		loadNotifications,
		saveNotifications,
		loadPrivacy,
		savePrivacy,
		load2FAStatus,
		toggle2FA,
		loadSessions,
		terminateSession,
	};
});
