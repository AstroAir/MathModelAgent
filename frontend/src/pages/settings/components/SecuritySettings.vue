<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { changePassword, deleteAccount } from '@/apis/settingsApi'
import type { PasswordChange, AccountDeletion } from '@/apis/settingsApi'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Separator } from '@/components/ui/separator'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Loader2, Shield, Smartphone, Mail, Key, Trash2, Monitor } from 'lucide-vue-next'
import { useToast } from '@/components/ui/toast/use-toast'

const settingsStore = useSettingsStore()
const { toast } = useToast()

// Password change state
const passwordForm = reactive<PasswordChange>({
  current_password: '',
  new_password: '',
  confirm_password: ''
})
const passwordDialogOpen = ref(false)
const savingPassword = ref(false)

// Account deletion state
const deletionForm = reactive<AccountDeletion>({
  password: '',
  confirmation_text: '',
  reason: ''
})
const deletionDialogOpen = ref(false)
const deletingAccount = ref(false)

// Handle password change
const handlePasswordChange = async () => {
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    toast({
      title: 'Error',
      description: 'New passwords do not match',
      variant: 'destructive'
    })
    return
  }

  if (passwordForm.new_password.length < 8) {
    toast({
      title: 'Error',
      description: 'Password must be at least 8 characters long',
      variant: 'destructive'
    })
    return
  }

  try {
    savingPassword.value = true
    const response = await changePassword(passwordForm)
    
    toast({
      title: 'Success',
      description: response.data.message
    })
    
    passwordDialogOpen.value = false
    passwordForm.current_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
  } catch (error: any) {
    toast({
      title: 'Error',
      description: error.response?.data?.detail || 'Failed to change password',
      variant: 'destructive'
    })
  } finally {
    savingPassword.value = false
  }
}

// Handle account deletion
const handleAccountDeletion = async () => {
  if (deletionForm.confirmation_text !== 'DELETE') {
    toast({
      title: 'Error',
      description: 'Please type DELETE to confirm account deletion',
      variant: 'destructive'
    })
    return
  }

  try {
    deletingAccount.value = true
    const response = await deleteAccount(deletionForm)
    
    toast({
      title: 'Account Deletion Requested',
      description: response.data.message
    })
    
    deletionDialogOpen.value = false
    // In production, redirect to logout
  } catch (error: any) {
    toast({
      title: 'Error',
      description: error.response?.data?.detail || 'Failed to process account deletion',
      variant: 'destructive'
    })
  } finally {
    deletingAccount.value = false
  }
}

// Handle session revoke
const handleRevokeSession = async (sessionId: string) => {
  await settingsStore.terminateSession(sessionId)
}
</script>

<template>
  <div class="space-y-6">
    <!-- Password -->
    <Card>
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <Key class="h-5 w-5" />
          Password
        </CardTitle>
        <CardDescription>
          Change your password regularly to keep your account secure
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Dialog v-model:open="passwordDialogOpen">
          <DialogTrigger as-child>
            <Button variant="outline">
              Change Password
            </Button>
          </DialogTrigger>
          <DialogContent class="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Change Password</DialogTitle>
              <DialogDescription>
                Enter your current password and choose a new one
              </DialogDescription>
            </DialogHeader>
            <div class="space-y-4 py-4">
              <div>
                <Label>Current Password</Label>
                <Input
                  v-model="passwordForm.current_password"
                  type="password"
                  placeholder="Enter current password"
                  class="mt-2"
                />
              </div>
              <div>
                <Label>New Password</Label>
                <Input
                  v-model="passwordForm.new_password"
                  type="password"
                  placeholder="Enter new password"
                  class="mt-2"
                />
                <p class="text-sm text-muted-foreground mt-1">
                  Must be at least 8 characters long
                </p>
              </div>
              <div>
                <Label>Confirm New Password</Label>
                <Input
                  v-model="passwordForm.confirm_password"
                  type="password"
                  placeholder="Confirm new password"
                  class="mt-2"
                />
              </div>
            </div>
            <DialogFooter>
              <Button
                @click="handlePasswordChange"
                :disabled="savingPassword"
              >
                <Loader2 v-if="savingPassword" class="mr-2 h-4 w-4 animate-spin" />
                Update Password
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>

    <!-- Two-Factor Authentication -->
    <Card>
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <Shield class="h-5 w-5" />
          Two-Factor Authentication
        </CardTitle>
        <CardDescription>
          Add an extra layer of security to your account
        </CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <div class="flex items-center justify-between">
          <div class="space-y-0.5">
            <div class="font-medium">Enable 2FA</div>
            <div class="text-sm text-muted-foreground">
              Require a verification code in addition to your password
            </div>
          </div>
          <Switch
            :checked="settingsStore.twoFactorAuth.enabled"
            @update:checked="(checked: boolean) => settingsStore.toggle2FA(checked, 'app')"
          />
        </div>

        <Separator />

        <div v-if="settingsStore.twoFactorAuth.enabled" class="space-y-3">
          <p class="text-sm font-medium">Authentication Method</p>
          
          <div class="flex items-center gap-2 p-3 border rounded-lg">
            <Smartphone class="h-5 w-5 text-muted-foreground" />
            <div class="flex-1">
              <p class="text-sm font-medium">Authenticator App</p>
              <p class="text-xs text-muted-foreground">Use an app like Google Authenticator</p>
            </div>
            <Button
              size="sm"
              variant="outline"
              @click="settingsStore.toggle2FA(true, 'app')"
            >
              {{ settingsStore.twoFactorAuth.method === 'app' ? 'Active' : 'Setup' }}
            </Button>
          </div>

          <div class="flex items-center gap-2 p-3 border rounded-lg">
            <Mail class="h-5 w-5 text-muted-foreground" />
            <div class="flex-1">
              <p class="text-sm font-medium">Email</p>
              <p class="text-xs text-muted-foreground">Receive codes via email</p>
            </div>
            <Button
              size="sm"
              variant="outline"
              @click="settingsStore.toggle2FA(true, 'email')"
            >
              {{ settingsStore.twoFactorAuth.method === 'email' ? 'Active' : 'Setup' }}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Active Sessions -->
    <Card>
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <Monitor class="h-5 w-5" />
          Active Sessions
        </CardTitle>
        <CardDescription>
          Manage devices where you're currently signed in
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div class="space-y-3">
          <div
            v-for="session in settingsStore.sessions"
            :key="session.session_id"
            class="flex items-center justify-between p-3 border rounded-lg"
          >
            <div class="flex-1">
              <div class="flex items-center gap-2">
                <p class="text-sm font-medium">{{ session.device }}</p>
                <span v-if="session.current" class="text-xs bg-primary text-primary-foreground px-2 py-0.5 rounded">
                  Current
                </span>
              </div>
              <p class="text-xs text-muted-foreground">{{ session.location }}</p>
              <p class="text-xs text-muted-foreground">
                Last active: {{ new Date(session.last_active).toLocaleString() }}
              </p>
            </div>
            <Button
              v-if="!session.current"
              size="sm"
              variant="outline"
              @click="handleRevokeSession(session.session_id)"
            >
              Revoke
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Danger Zone -->
    <Card class="border-destructive">
      <CardHeader>
        <CardTitle class="flex items-center gap-2 text-destructive">
          <Trash2 class="h-5 w-5" />
          Danger Zone
        </CardTitle>
        <CardDescription>
          Irreversible actions that permanently affect your account
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Dialog v-model:open="deletionDialogOpen">
          <DialogTrigger as-child>
            <Button variant="destructive">
              Delete Account
            </Button>
          </DialogTrigger>
          <DialogContent class="sm:max-w-[525px]">
            <DialogHeader>
              <DialogTitle>Are you absolutely sure?</DialogTitle>
              <DialogDescription class="space-y-4">
                <p>
                  This action cannot be undone. This will permanently delete your account
                  and remove all your data from our servers.
                </p>
                
                <div class="space-y-3">
                  <div>
                    <Label>Confirm Password</Label>
                    <Input
                      v-model="deletionForm.password"
                      type="password"
                      placeholder="Enter your password"
                      class="mt-2"
                    />
                  </div>
                  
                  <div>
                    <Label>Type DELETE to confirm</Label>
                    <Input
                      v-model="deletionForm.confirmation_text"
                      type="text"
                      placeholder="DELETE"
                      class="mt-2"
                    />
                  </div>
                  
                  <div>
                    <Label>Reason (optional)</Label>
                    <Input
                      v-model="deletionForm.reason"
                      type="text"
                      placeholder="Why are you leaving?"
                      class="mt-2"
                    />
                  </div>
                </div>
              </DialogDescription>
            </DialogHeader>
            <DialogFooter class="gap-2">
              <Button
                variant="outline"
                @click="deletionDialogOpen = false"
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                @click="handleAccountDeletion"
                :disabled="deletingAccount || deletionForm.confirmation_text !== 'DELETE'"
              >
                <Loader2 v-if="deletingAccount" class="mr-2 h-4 w-4 animate-spin" />
                Delete Account
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  </div>
</template>
