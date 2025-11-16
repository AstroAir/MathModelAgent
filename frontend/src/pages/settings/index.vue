<script setup lang="ts">
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useSettingsStore } from "@/stores/settings";
import { Bell, Lock, LogOut, Shield, User } from "lucide-vue-next";
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import AccountSettings from "./components/AccountSettings.vue";
import NotificationSettings from "./components/NotificationSettings.vue";
import PrivacySettings from "./components/PrivacySettings.vue";
import SecuritySettings from "./components/SecuritySettings.vue";

const settingsStore = useSettingsStore();
const router = useRouter();
const activeTab = ref("account");

onMounted(async () => {
	// Load all settings on mount
	await Promise.all([
		settingsStore.loadProfile(),
		settingsStore.loadNotifications(),
		settingsStore.loadPrivacy(),
		settingsStore.load2FAStatus(),
		settingsStore.loadSessions(),
	]);
});

const handleLogout = () => {
	// In production, clear auth tokens and redirect to login
	router.push("/login");
};
</script>

<template>
  <div class="min-h-screen bg-background">
    <div class="container mx-auto px-4 py-8 max-w-6xl">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold tracking-tight mb-2">Settings</h1>
        <p class="text-muted-foreground">
          Manage your account settings and preferences
        </p>
      </div>

      <!-- Settings Tabs -->
      <Tabs v-model="activeTab" class="space-y-6">
        <TabsList class="grid w-full grid-cols-2 lg:grid-cols-4 h-auto">
          <TabsTrigger value="account" class="flex items-center gap-2 py-3">
            <User class="h-4 w-4" />
            <span class="hidden sm:inline">Account</span>
          </TabsTrigger>
          <TabsTrigger value="security" class="flex items-center gap-2 py-3">
            <Shield class="h-4 w-4" />
            <span class="hidden sm:inline">Security</span>
          </TabsTrigger>
          <TabsTrigger value="notifications" class="flex items-center gap-2 py-3">
            <Bell class="h-4 w-4" />
            <span class="hidden sm:inline">Notifications</span>
          </TabsTrigger>
          <TabsTrigger value="privacy" class="flex items-center gap-2 py-3">
            <Lock class="h-4 w-4" />
            <span class="hidden sm:inline">Privacy</span>
          </TabsTrigger>
        </TabsList>

        <!-- Account Tab -->
        <TabsContent value="account" class="space-y-6">
          <AccountSettings />
        </TabsContent>

        <!-- Security Tab -->
        <TabsContent value="security" class="space-y-6">
          <SecuritySettings />
        </TabsContent>

        <!-- Notifications Tab -->
        <TabsContent value="notifications" class="space-y-6">
          <NotificationSettings />
        </TabsContent>

        <!-- Privacy Tab -->
        <TabsContent value="privacy" class="space-y-6">
          <PrivacySettings />
        </TabsContent>
      </Tabs>

      <!-- Logout Section -->
      <Card class="mt-8 border-destructive">
        <CardHeader>
          <CardTitle class="flex items-center gap-2 text-destructive">
            <LogOut class="h-5 w-5" />
            Sign Out
          </CardTitle>
          <CardDescription>
            Sign out of your account on this device
          </CardDescription>
        </CardHeader>
        <CardContent>
          <button
            @click="handleLogout"
            class="px-4 py-2 bg-destructive text-destructive-foreground rounded-md hover:bg-destructive/90 transition-colors"
          >
            Sign Out
          </button>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
