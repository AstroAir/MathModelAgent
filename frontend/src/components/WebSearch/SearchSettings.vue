<template>
  <div class="search-settings">
    <!-- Settings Header -->
    <div class="settings-header mb-6">
      <div class="flex items-center space-x-2 mb-2">
        <Settings class="w-5 h-5 text-primary" />
        <h3 class="text-lg font-semibold">Web Search Settings</h3>
      </div>
      <p class="text-sm text-muted-foreground">
        Configure search providers, API keys, and default search parameters.
      </p>
    </div>

    <!-- Provider Configuration -->
    <div class="provider-config mb-6">
      <h4 class="text-md font-medium mb-4 flex items-center space-x-2">
        <Globe class="w-4 h-4" />
        <span>Search Providers</span>
      </h4>

      <div class="space-y-4">
        <!-- Tavily Provider -->
        <div class="provider-card border rounded-lg p-4">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center space-x-3">
              <div class="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                <Search class="w-4 h-4 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <h5 class="font-medium">Tavily</h5>
                <p class="text-xs text-muted-foreground">AI-powered search with answers</p>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <Badge :variant="tavilyStatus.configured ? 'default' : 'secondary'">
                {{ tavilyStatus.configured ? 'Configured' : 'Not Configured' }}
              </Badge>
              <Switch v-model="settings.providers.tavily.enabled" :disabled="!tavilyStatus.configured" />
            </div>
          </div>

          <div class="space-y-3">
            <div>
              <Label for="tavily-api-key">API Key</Label>
              <div class="flex space-x-2 mt-1">
                <Input
                  id="tavily-api-key"
                  v-model="settings.providers.tavily.apiKey"
                  :type="showApiKeys.tavily ? 'text' : 'password'"
                  placeholder="tvly-your-api-key-here"
                  class="flex-1"
                />
                <Button
                  variant="outline"
                  size="sm"
                  @click="showApiKeys.tavily = !showApiKeys.tavily"
                >
                  <Eye v-if="!showApiKeys.tavily" class="w-4 h-4" />
                  <EyeOff v-else class="w-4 h-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  @click="testProvider('tavily')"
                  :disabled="!settings.providers.tavily.apiKey || isTestingProvider"
                >
                  <Activity class="w-4 h-4" />
                </Button>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <Label for="tavily-timeout">Timeout (seconds)</Label>
                <Input
                  id="tavily-timeout"
                  v-model.number="settings.providers.tavily.timeout"
                  type="number"
                  min="5"
                  max="60"
                  class="mt-1"
                />
              </div>
              <div>
                <Label for="tavily-max-results">Max Results</Label>
                <Input
                  id="tavily-max-results"
                  v-model.number="settings.providers.tavily.maxResults"
                  type="number"
                  min="1"
                  max="50"
                  class="mt-1"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Exa Provider -->
        <div class="provider-card border rounded-lg p-4">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center space-x-3">
              <div class="w-8 h-8 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center">
                <Search class="w-4 h-4 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <h5 class="font-medium">Exa</h5>
                <p class="text-xs text-muted-foreground">Embeddings-based search engine</p>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <Badge :variant="exaStatus.configured ? 'default' : 'secondary'">
                {{ exaStatus.configured ? 'Configured' : 'Not Configured' }}
              </Badge>
              <Switch v-model="settings.providers.exa.enabled" :disabled="!exaStatus.configured" />
            </div>
          </div>

          <div class="space-y-3">
            <div>
              <Label for="exa-api-key">API Key</Label>
              <div class="flex space-x-2 mt-1">
                <Input
                  id="exa-api-key"
                  v-model="settings.providers.exa.apiKey"
                  :type="showApiKeys.exa ? 'text' : 'password'"
                  placeholder="your-exa-api-key-here"
                  class="flex-1"
                />
                <Button
                  variant="outline"
                  size="sm"
                  @click="showApiKeys.exa = !showApiKeys.exa"
                >
                  <Eye v-if="!showApiKeys.exa" class="w-4 h-4" />
                  <EyeOff v-else class="w-4 h-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  @click="testProvider('exa')"
                  :disabled="!settings.providers.exa.apiKey || isTestingProvider"
                >
                  <Activity class="w-4 h-4" />
                </Button>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <Label for="exa-timeout">Timeout (seconds)</Label>
                <Input
                  id="exa-timeout"
                  v-model.number="settings.providers.exa.timeout"
                  type="number"
                  min="5"
                  max="60"
                  class="mt-1"
                />
              </div>
              <div>
                <Label for="exa-max-results">Max Results</Label>
                <Input
                  id="exa-max-results"
                  v-model.number="settings.providers.exa.maxResults"
                  type="number"
                  min="1"
                  max="50"
                  class="mt-1"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- General Settings -->
    <div class="general-settings mb-6">
      <h4 class="text-md font-medium mb-4 flex items-center space-x-2">
        <Sliders class="w-4 h-4" />
        <span>General Settings</span>
      </h4>

      <div class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label for="default-provider">Default Provider</Label>
            <Select v-model="settings.defaultProvider">
              <SelectTrigger class="mt-1">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="tavily" :disabled="!settings.providers.tavily.enabled">
                  Tavily
                </SelectItem>
                <SelectItem value="exa" :disabled="!settings.providers.exa.enabled">
                  Exa
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label for="default-search-type">Default Search Type</Label>
            <Select v-model="settings.defaultSearchType">
              <SelectTrigger class="mt-1">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="general">General</SelectItem>
                <SelectItem value="academic">Academic</SelectItem>
                <SelectItem value="code">Code</SelectItem>
                <SelectItem value="news">News</SelectItem>
                <SelectItem value="research">Research</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div class="flex items-center space-x-2">
          <Switch v-model="settings.enableFallback" />
          <Label for="enable-fallback">Enable provider fallback</Label>
          <div class="text-xs text-muted-foreground ml-2">
            Automatically try other providers if the primary one fails
          </div>
        </div>

        <div class="flex items-center space-x-2">
          <Switch v-model="settings.includeContent" />
          <Label for="include-content">Include content by default</Label>
          <div class="text-xs text-muted-foreground ml-2">
            Retrieve full content for search results
          </div>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="action-buttons flex justify-between">
      <div class="flex space-x-2">
        <Button variant="outline" @click="resetToDefaults">
          <RotateCcw class="w-4 h-4 mr-1" />
          Reset to Defaults
        </Button>
        <Button variant="outline" @click="exportSettings">
          <Download class="w-4 h-4 mr-1" />
          Export Settings
        </Button>
      </div>

      <div class="flex space-x-2">
        <Button variant="outline" @click="$emit('cancel')">
          Cancel
        </Button>
        <Button @click="saveSettings" :disabled="isSaving">
          <Save class="w-4 h-4 mr-1" />
          {{ isSaving ? 'Saving...' : 'Save Settings' }}
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
	getSearchSettings,
	testSearchProvider,
	updateSearchSettings,
} from "@/apis/searchApi";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { useWebSearch } from "@/composables/useWebSearch";
import { SearchProvider } from "@/types/search";
import {
	Activity,
	Download,
	Eye,
	EyeOff,
	Globe,
	RotateCcw,
	Save,
	Search,
	Settings,
	Sliders,
} from "lucide-vue-next";
import { computed, onMounted, reactive, ref } from "vue";

// Types
interface ProviderSettings {
	enabled: boolean;
	apiKey: string;
	timeout: number;
	maxResults: number;
}

interface SearchSettingsData {
	providers: {
		tavily: ProviderSettings;
		exa: ProviderSettings;
	};
	defaultProvider: string;
	defaultSearchType: string;
	enableFallback: boolean;
	includeContent: boolean;
	maxResults: number;
	timeout: number;
}

// Emits
const emit = defineEmits<{
	cancel: [];
	saved: [settings: SearchSettingsData];
}>();

// Composables
const { providerStatuses, checkProviderStatus } = useWebSearch();

// State
const isSaving = ref(false);
const isTestingProvider = ref(false);
const showApiKeys = reactive({
	tavily: false,
	exa: false,
});

const settings = reactive({
	providers: {
		tavily: {
			enabled: false,
			apiKey: "",
			timeout: 30,
			maxResults: 10,
		},
		exa: {
			enabled: false,
			apiKey: "",
			timeout: 30,
			maxResults: 10,
		},
	},
	defaultProvider: "tavily",
	defaultSearchType: "general",
	enableFallback: true,
	includeContent: true,
	maxResults: 10,
	timeout: 30,
});

// Computed
const tavilyStatus = computed(() => ({
	configured: !!settings.providers.tavily.apiKey,
	available: providerStatuses?.tavily?.available || false,
}));

const exaStatus = computed(() => ({
	configured: !!settings.providers.exa.apiKey,
	available: providerStatuses?.exa?.available || false,
}));

// Methods
const testProvider = async (provider: "tavily" | "exa") => {
	isTestingProvider.value = true;
	try {
		await testSearchProvider(provider as SearchProvider);
		await checkProviderStatus(provider as SearchProvider);
	} catch (error) {
		console.error("Failed to test provider:", error);
	} finally {
		isTestingProvider.value = false;
	}
};

const saveSettings = async () => {
	isSaving.value = true;
	try {
		const defaultProviderEnum =
			settings.defaultProvider === "exa"
				? SearchProvider.EXA
				: SearchProvider.TAVILY;

		const fallbackProviders: SearchProvider[] = [];
		if (settings.providers.tavily.enabled) {
			fallbackProviders.push(SearchProvider.TAVILY);
		}
		if (settings.providers.exa.enabled) {
			fallbackProviders.push(SearchProvider.EXA);
		}

		await updateSearchSettings({
			default_provider: defaultProviderEnum,
			max_results: settings.maxResults,
			timeout: settings.timeout,
			enable_fallback: settings.enableFallback,
			fallback_providers: fallbackProviders,
		});
		emit("saved", settings);
	} catch (error) {
		console.error("Failed to save settings:", error);
	} finally {
		isSaving.value = false;
	}
};

const resetToDefaults = () => {
	Object.assign(settings, {
		providers: {
			tavily: { enabled: false, apiKey: "", timeout: 30, maxResults: 10 },
			exa: { enabled: false, apiKey: "", timeout: 30, maxResults: 10 },
		},
		defaultProvider: "tavily",
		defaultSearchType: "general",
		enableFallback: true,
		includeContent: true,
	});
};

const exportSettings = () => {
	const exportData = { ...settings };
	// Remove sensitive data
	exportData.providers.tavily.apiKey = "";
	exportData.providers.exa.apiKey = "";

	const blob = new Blob([JSON.stringify(exportData, null, 2)], {
		type: "application/json",
	});

	const url = URL.createObjectURL(blob);
	const a = document.createElement("a");
	a.href = url;
	a.download = `search-settings-${Date.now()}.json`;
	document.body.appendChild(a);
	a.click();
	document.body.removeChild(a);
	URL.revokeObjectURL(url);
};

// Lifecycle
onMounted(async () => {
	try {
		const response = await getSearchSettings();
		const data = response.data;
		settings.defaultProvider = data.default_provider || "tavily";
		settings.maxResults = data.max_results ?? 10;
		settings.timeout = data.timeout ?? 30;
		settings.enableFallback = data.enable_fallback ?? true;
		settings.includeContent = true;
	} catch (error) {
		console.error("Failed to load search settings:", error);
	}
	await checkProviderStatus();
});
</script>

<style scoped>
.search-settings {
  @apply w-full max-w-2xl mx-auto;
}

.provider-card {
  @apply bg-card;
}

.action-buttons {
  @apply pt-4 border-t;
}
</style>
