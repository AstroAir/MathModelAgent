<script setup lang="ts">
import { reactive, watch } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import type { NotificationPreferences } from '@/apis/settingsApi'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Separator } from '@/components/ui/separator'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Input } from '@/components/ui/input'
import { Loader2, Save, Mail, Bell, MessageSquare, Clock } from 'lucide-vue-next'

const settingsStore = useSettingsStore()

// Form state
const formData = reactive<NotificationPreferences>({ ...settingsStore.notifications })

// Watch for store updates
watch(() => settingsStore.notifications, (newNotifications) => {
  Object.assign(formData, newNotifications)
}, { deep: true })

const onSubmit = async () => {
  await settingsStore.saveNotifications(formData)
}

const notificationFrequencies = [
  { value: 'instant', label: 'Instant' },
  { value: 'hourly', label: 'Hourly Digest' },
  { value: 'daily', label: 'Daily Digest' },
  { value: 'weekly', label: 'Weekly Digest' },
]
</script>

<template>
  <div class="space-y-6">
    <!-- Email Notifications -->
    <Card>
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <Mail class="h-5 w-5" />
          Email Notifications
        </CardTitle>
        <CardDescription>
          Manage your email notification preferences
        </CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <div class="flex items-center justify-between">
          <div class="space-y-0.5">
            <div class="font-medium">Enable Email Notifications</div>
            <div class="text-sm text-muted-foreground">
              Receive notifications via email
            </div>
          </div>
          <Switch
            :checked="formData.email_enabled"
            @update:checked="(checked: boolean) => formData.email_enabled = checked"
          />
        </div>

        <Separator />

        <div v-if="formData.email_enabled" class="space-y-4 pl-6">
          <div class="flex items-center justify-between">
            <div class="space-y-0.5">
              <div class="text-sm font-medium">Security Alerts</div>
              <div class="text-xs text-muted-foreground">
                Critical security updates and alerts
              </div>
            </div>
            <Switch
              :checked="formData.email_security_alerts"
              @update:checked="(checked: boolean) => formData.email_security_alerts = checked"
            />
          </div>

          <div class="flex items-center justify-between">
            <div class="space-y-0.5">
              <div class="text-sm font-medium">System Updates</div>
              <div class="text-xs text-muted-foreground">
                Platform updates and new features
              </div>
            </div>
            <Switch
              :checked="formData.email_system_updates"
              @update:checked="(checked: boolean) => formData.email_system_updates = checked"
            />
          </div>

          <div class="flex items-center justify-between">
            <div class="space-y-0.5">
              <div class="text-sm font-medium">Task Updates</div>
              <div class="text-xs text-muted-foreground">
                Updates about your modeling tasks
              </div>
            </div>
            <Switch
              :checked="formData.email_task_updates"
              @update:checked="(checked: boolean) => formData.email_task_updates = checked"
            />
          </div>

          <div class="flex items-center justify-between">
            <div class="space-y-0.5">
              <div class="text-sm font-medium">Weekly Summary</div>
              <div class="text-xs text-muted-foreground">
                Weekly summary of your activity
              </div>
            </div>
            <Switch
              :checked="formData.email_weekly_summary"
              @update:checked="(checked: boolean) => formData.email_weekly_summary = checked"
            />
          </div>

          <div class="flex items-center justify-between">
            <div class="space-y-0.5">
              <div class="text-sm font-medium">Marketing Emails</div>
              <div class="text-xs text-muted-foreground">
                Tips, news, and product updates
              </div>
            </div>
            <Switch
              :checked="formData.email_marketing"
              @update:checked="(checked: boolean) => formData.email_marketing = checked"
            />
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Push Notifications -->
    <Card>
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <Bell class="h-5 w-5" />
          Push Notifications
        </CardTitle>
        <CardDescription>
          Manage browser push notification preferences
        </CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <div class="flex items-center justify-between">
          <div class="space-y-0.5">
            <div class="font-medium">Enable Push Notifications</div>
            <div class="text-sm text-muted-foreground">
              Receive push notifications in your browser
            </div>
          </div>
          <Switch
            :checked="formData.push_enabled"
            @update:checked="(checked: boolean) => formData.push_enabled = checked"
          />
        </div>

        <Separator />

        <div v-if="formData.push_enabled" class="space-y-4 pl-6">
          <div class="flex items-center justify-between">
            <div class="space-y-0.5">
              <div class="text-sm font-medium">Security Alerts</div>
              <div class="text-xs text-muted-foreground">
                Urgent security notifications
              </div>
            </div>
            <Switch
              :checked="formData.push_security_alerts"
              @update:checked="(checked: boolean) => formData.push_security_alerts = checked"
            />
          </div>

          <div class="flex items-center justify-between">
            <div class="space-y-0.5">
              <div class="text-sm font-medium">System Updates</div>
              <div class="text-xs text-muted-foreground">
                Important system notifications
              </div>
            </div>
            <Switch
              :checked="formData.push_system_updates"
              @update:checked="(checked: boolean) => formData.push_system_updates = checked"
            />
          </div>

          <div class="flex items-center justify-between">
            <div class="space-y-0.5">
              <div class="text-sm font-medium">Task Updates</div>
              <div class="text-xs text-muted-foreground">
                Real-time task completion notifications
              </div>
            </div>
            <Switch
              :checked="formData.push_task_updates"
              @update:checked="(checked: boolean) => formData.push_task_updates = checked"
            />
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- In-App Notifications -->
    <Card>
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <MessageSquare class="h-5 w-5" />
          In-App Notifications
        </CardTitle>
        <CardDescription>
          Manage notifications shown within the application
        </CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <div class="flex items-center justify-between">
          <div class="space-y-0.5">
            <div class="font-medium">Enable In-App Notifications</div>
            <div class="text-sm text-muted-foreground">
              Show notifications within the app
            </div>
          </div>
          <Switch
            :checked="formData.in_app_enabled"
            @update:checked="(checked: boolean) => formData.in_app_enabled = checked"
          />
        </div>

        <Separator />

        <div v-if="formData.in_app_enabled" class="space-y-4 pl-6">
          <div class="flex items-center justify-between">
            <div class="space-y-0.5">
              <div class="text-sm font-medium">Security Alerts</div>
              <div class="text-xs text-muted-foreground">
                Security-related notifications
              </div>
            </div>
            <Switch
              :checked="formData.inapp_security_alerts"
              @update:checked="(checked: boolean) => formData.inapp_security_alerts = checked"
            />
          </div>

          <div class="flex items-center justify-between">
            <div class="space-y-0.5">
              <div class="text-sm font-medium">System Updates</div>
              <div class="text-xs text-muted-foreground">
                Platform announcements
              </div>
            </div>
            <Switch
              :checked="formData.inapp_system_updates"
              @update:checked="(checked: boolean) => formData.inapp_system_updates = checked"
            />
          </div>

          <div class="flex items-center justify-between">
            <div class="space-y-0.5">
              <div class="text-sm font-medium">Task Updates</div>
              <div class="text-xs text-muted-foreground">
                Task progress and completions
              </div>
            </div>
            <Switch
              :checked="formData.inapp_task_updates"
              @update:checked="(checked: boolean) => formData.inapp_task_updates = checked"
            />
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Notification Preferences -->
    <Card>
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <Clock class="h-5 w-5" />
          Notification Preferences
        </CardTitle>
        <CardDescription>
          Control when and how you receive notifications
        </CardDescription>
      </CardHeader>
      <CardContent class="space-y-6">
        <!-- Notification Frequency -->
        <div>
          <Label>Notification Frequency</Label>
          <Select v-model="formData.notification_frequency">
            <SelectTrigger class="mt-2">
              <SelectValue placeholder="Select frequency" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="freq in notificationFrequencies" :key="freq.value" :value="freq.value">
                {{ freq.label }}
              </SelectItem>
            </SelectContent>
          </Select>
          <p class="text-sm text-muted-foreground mt-1">
            Control how often you receive notifications
          </p>
        </div>

        <Separator />

        <!-- Digest Notifications -->
        <div class="flex items-center justify-between">
          <div class="space-y-0.5">
            <div class="font-medium">Notification Digest</div>
            <div class="text-sm text-muted-foreground">
              Combine multiple notifications into a single message
            </div>
          </div>
          <Switch
            :checked="formData.digest_enabled"
            @update:checked="(checked: boolean) => formData.digest_enabled = checked"
          />
        </div>

        <Separator />

        <!-- Quiet Hours -->
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <div class="space-y-0.5">
              <div class="font-medium">Quiet Hours</div>
              <div class="text-sm text-muted-foreground">
                Pause notifications during specified hours
              </div>
            </div>
            <Switch
              :checked="formData.quiet_hours_enabled"
              @update:checked="(checked: boolean) => formData.quiet_hours_enabled = checked"
            />
          </div>

          <div v-if="formData.quiet_hours_enabled" class="grid grid-cols-2 gap-4 pl-6">
            <div>
              <Label>Start Time</Label>
              <Input
                v-model="formData.quiet_hours_start"
                type="time"
                class="mt-2"
              />
            </div>
            <div>
              <Label>End Time</Label>
              <Input
                v-model="formData.quiet_hours_end"
                type="time"
                class="mt-2"
              />
            </div>
          </div>
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
