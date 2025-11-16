<script setup lang="ts">
import type { UserProfile } from "@/apis/settingsApi";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useSettingsStore } from "@/stores/settings";
import { Loader2, Save } from "lucide-vue-next";
import { reactive, ref, watch } from "vue";

const settingsStore = useSettingsStore();

// Form state
const formData = reactive<UserProfile>({ ...settingsStore.profile });
const errors = ref<Partial<Record<keyof UserProfile, string>>>({});

// Watch for store updates
watch(
	() => settingsStore.profile,
	(newProfile) => {
		Object.assign(formData, newProfile);
	},
	{ deep: true },
);

// Validation
const validateForm = (): boolean => {
	errors.value = {};

	if (!formData.name || formData.name.trim().length === 0) {
		errors.value.name = "Name is required";
		return false;
	}

	if (!formData.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
		errors.value.email = "Invalid email address";
		return false;
	}

	if (formData.bio && formData.bio.length > 500) {
		errors.value.bio = "Bio must be 500 characters or less";
		return false;
	}

	return true;
};

const onSubmit = async () => {
	if (!validateForm()) return;

	await settingsStore.saveProfile(formData);
};

const timezones = [
	{ value: "UTC", label: "UTC" },
	{ value: "America/New_York", label: "Eastern Time" },
	{ value: "America/Chicago", label: "Central Time" },
	{ value: "America/Denver", label: "Mountain Time" },
	{ value: "America/Los_Angeles", label: "Pacific Time" },
	{ value: "Europe/London", label: "London" },
	{ value: "Europe/Paris", label: "Paris" },
	{ value: "Asia/Shanghai", label: "Shanghai" },
	{ value: "Asia/Tokyo", label: "Tokyo" },
];

const languages = [
	{ value: "en", label: "English" },
	{ value: "zh", label: "中文" },
	{ value: "es", label: "Español" },
	{ value: "fr", label: "Français" },
	{ value: "de", label: "Deutsch" },
	{ value: "ja", label: "日本語" },
];
</script>

<template>
  <div class="space-y-6">
    <!-- Profile Information -->
    <Card>
      <CardHeader>
        <CardTitle>Profile Information</CardTitle>
        <CardDescription>
          Update your account profile information
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form @submit="onSubmit" class="space-y-6">
          <!-- Avatar -->
          <div class="flex items-center gap-4">
            <Avatar class="h-20 w-20">
              <AvatarImage :src="formData.avatar || ''" :alt="formData.name" />
              <AvatarFallback>{{ (formData.name || 'US').substring(0, 2).toUpperCase() }}</AvatarFallback>
            </Avatar>
            <div class="flex-1">
              <Label>Avatar URL</Label>
              <Input
                v-model="formData.avatar"
                type="url"
                placeholder="https://example.com/avatar.jpg"
                class="mt-2"
              />
              <p class="text-sm text-muted-foreground mt-1">
                Enter a URL to your profile picture
              </p>
            </div>
          </div>

          <!-- Name -->
          <div>
            <Label>Name *</Label>
            <Input
              v-model="formData.name"
              type="text"
              placeholder="Enter your name"
              :class="{ 'border-destructive': errors.name }"
              class="mt-2"
            />
            <p v-if="errors.name" class="text-sm text-destructive mt-1">{{ errors.name }}</p>
          </div>

          <!-- Email -->
          <div>
            <Label>Email *</Label>
            <Input
              v-model="formData.email"
              type="email"
              placeholder="your.email@example.com"
              :class="{ 'border-destructive': errors.email }"
              class="mt-2"
            />
            <p v-if="errors.email" class="text-sm text-destructive mt-1">{{ errors.email }}</p>
            <p v-else class="text-sm text-muted-foreground mt-1">
              Your email address for account notifications
            </p>
          </div>

          <!-- Phone -->
          <div>
            <Label>Phone Number</Label>
            <Input
              v-model="formData.phone"
              type="tel"
              placeholder="+1 (555) 000-0000"
              class="mt-2"
            />
            <p class="text-sm text-muted-foreground mt-1">
              Optional: For account recovery and notifications
            </p>
          </div>

          <!-- Bio -->
          <div>
            <Label>Bio</Label>
            <Textarea
              v-model="formData.bio"
              placeholder="Tell us about yourself..."
              class="resize-none mt-2"
              :rows="4"
              :class="{ 'border-destructive': errors.bio }"
            />
            <p v-if="errors.bio" class="text-sm text-destructive mt-1">{{ errors.bio }}</p>
            <p v-else class="text-sm text-muted-foreground mt-1">
              {{ (formData.bio?.length || 0) }}/500 characters
            </p>
          </div>

          <!-- Timezone -->
          <div>
            <Label>Timezone</Label>
            <Select v-model="formData.timezone">
              <SelectTrigger class="mt-2">
                <SelectValue placeholder="Select a timezone" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="tz in timezones" :key="tz.value" :value="tz.value">
                  {{ tz.label }}
                </SelectItem>
              </SelectContent>
            </Select>
            <p class="text-sm text-muted-foreground mt-1">
              Your local timezone for scheduling
            </p>
          </div>

          <!-- Language -->
          <div>
            <Label>Language</Label>
            <Select v-model="formData.language">
              <SelectTrigger class="mt-2">
                <SelectValue placeholder="Select a language" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="lang in languages" :key="lang.value" :value="lang.value">
                  {{ lang.label }}
                </SelectItem>
              </SelectContent>
            </Select>
            <p class="text-sm text-muted-foreground mt-1">
              Your preferred language for the interface
            </p>
          </div>

          <!-- Submit Button -->
          <div class="flex justify-end">
            <Button
              type="submit"
              :disabled="settingsStore.saving"
              class="min-w-32"
            >
              <Loader2 v-if="settingsStore.saving" class="mr-2 h-4 w-4 animate-spin" />
              <Save v-else class="mr-2 h-4 w-4" />
              Save Changes
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  </div>
</template>
