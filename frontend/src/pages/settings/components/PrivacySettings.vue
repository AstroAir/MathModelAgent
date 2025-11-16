<script setup lang="ts">
import type { PrivacySettings } from "@/apis/settingsApi";
import { Button } from "@/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import { useSettingsStore } from "@/stores/settings";
import {
	BarChart,
	Database,
	Loader2,
	Lock,
	Save,
	Sparkles,
} from "lucide-vue-next";
import { reactive, watch } from "vue";

const settingsStore = useSettingsStore();

// Form state
const formData = reactive<PrivacySettings>({ ...settingsStore.privacy });

// Watch for store updates
watch(
	() => settingsStore.privacy,
	(newPrivacy) => {
		Object.assign(formData, newPrivacy);
	},
	{ deep: true },
);

const onSubmit = async () => {
	await settingsStore.savePrivacy(formData);
};
</script>

<template>
  <div class="space-y-6">
    <!-- Data Collection -->
    <Card>
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <Database class="h-5 w-5" />
          Data Collection
        </CardTitle>
        <CardDescription>
          Control what data we collect to improve your experience
        </CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <div class="flex items-center justify-between">
          <div class="space-y-0.5 max-w-lg">
            <div class="font-medium">Basic Data Collection</div>
            <div class="text-sm text-muted-foreground">
              Allow us to collect basic usage data to improve the platform. This includes
              page views, feature usage, and general interaction patterns.
            </div>
          </div>
          <Switch
            :checked="formData.data_collection"
            @update:checked="(checked: boolean) => formData.data_collection = checked"
          />
        </div>

        <Separator />

        <div class="bg-muted p-4 rounded-lg">
          <p class="text-sm">
            <strong>What we collect:</strong> Page visits, button clicks, feature usage,
            error reports, and performance metrics. We never collect passwords or sensitive
            personal information.
          </p>
        </div>
      </CardContent>
    </Card>

    <!-- Analytics -->
    <Card>
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <BarChart class="h-5 w-5" />
          Analytics
        </CardTitle>
        <CardDescription>
          Help us understand how you use our platform
        </CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <div class="flex items-center justify-between">
          <div class="space-y-0.5 max-w-lg">
            <div class="font-medium">Usage Analytics</div>
            <div class="text-sm text-muted-foreground">
              Allow us to track your usage patterns to identify popular features and
              areas for improvement. This helps us make data-driven decisions.
            </div>
          </div>
          <Switch
            :checked="formData.analytics"
            @update:checked="(checked: boolean) => formData.analytics = checked"
          />
        </div>

        <Separator />

        <div class="bg-muted p-4 rounded-lg">
          <p class="text-sm">
            <strong>How it helps:</strong> Analytics data helps us understand which
            features are most valuable to you, identify bugs faster, and prioritize
            development efforts.
          </p>
        </div>
      </CardContent>
    </Card>

    <!-- Personalization -->
    <Card>
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <Sparkles class="h-5 w-5" />
          Personalization
        </CardTitle>
        <CardDescription>
          Customize your experience based on your preferences
        </CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <div class="flex items-center justify-between">
          <div class="space-y-0.5 max-w-lg">
            <div class="font-medium">Personalized Experience</div>
            <div class="text-sm text-muted-foreground">
              Allow us to personalize your experience based on your usage patterns,
              preferences, and behavior. This includes content recommendations and
              customized UI elements.
            </div>
          </div>
          <Switch
            :checked="formData.personalization"
            @update:checked="(checked: boolean) => formData.personalization = checked"
          />
        </div>

        <Separator />

        <div class="bg-muted p-4 rounded-lg">
          <p class="text-sm">
            <strong>Benefits:</strong> Personalization helps us show you relevant
            content, suggest helpful features, and adapt the interface to match your
            workflow.
          </p>
        </div>
      </CardContent>
    </Card>

    <!-- Data Sharing -->
    <Card>
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <Lock class="h-5 w-5" />
          Data Sharing
        </CardTitle>
        <CardDescription>
          Control how we share your data with third parties
        </CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <div class="flex items-center justify-between">
          <div class="space-y-0.5 max-w-lg">
            <div class="font-medium">Share Usage Data</div>
            <div class="text-sm text-muted-foreground">
              Allow us to share anonymized usage data with trusted partners to improve
              integrations and provide better services. No personal information is shared.
            </div>
          </div>
          <Switch
            :checked="formData.share_usage_data"
            @update:checked="(checked: boolean) => formData.share_usage_data = checked"
          />
        </div>

        <Separator />

        <div class="bg-muted p-4 rounded-lg">
          <p class="text-sm">
            <strong>Your control:</strong> We only share anonymized, aggregated data
            with vetted partners. You can opt out at any time. We never sell your
            personal information.
          </p>
        </div>
      </CardContent>
    </Card>

    <!-- Privacy Policy -->
    <Card>
      <CardHeader>
        <CardTitle>Privacy Resources</CardTitle>
        <CardDescription>
          Learn more about how we protect your data
        </CardDescription>
      </CardHeader>
      <CardContent class="space-y-3">
        <div class="flex items-center justify-between p-3 border rounded-lg hover:bg-accent transition-colors cursor-pointer">
          <div>
            <p class="font-medium">Privacy Policy</p>
            <p class="text-sm text-muted-foreground">Read our full privacy policy</p>
          </div>
          <Button variant="ghost" size="sm">View</Button>
        </div>

        <div class="flex items-center justify-between p-3 border rounded-lg hover:bg-accent transition-colors cursor-pointer">
          <div>
            <p class="font-medium">Data Request</p>
            <p class="text-sm text-muted-foreground">Request a copy of your data</p>
          </div>
          <Button variant="ghost" size="sm">Request</Button>
        </div>

        <div class="flex items-center justify-between p-3 border rounded-lg hover:bg-accent transition-colors cursor-pointer">
          <div>
            <p class="font-medium">Cookie Settings</p>
            <p class="text-sm text-muted-foreground">Manage cookie preferences</p>
          </div>
          <Button variant="ghost" size="sm">Manage</Button>
        </div>
      </CardContent>
    </Card>

    <!-- Save Button -->
    <div class="flex justify-end">
      <Button
        @click="onSubmit"
        :disabled="settingsStore.saving"
        class="min-w-32"
      >
        <Loader2 v-if="settingsStore.saving" class="mr-2 h-4 w-4 animate-spin" />
        <Save v-else class="mr-2 h-4 w-4" />
        Save Changes
      </Button>
    </div>
  </div>
</template>
