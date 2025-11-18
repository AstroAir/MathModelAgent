<template>
  <div class="search-error-handler">
    <!-- Network Error -->
    <Alert v-if="errorType === 'network'" variant="destructive" class="mb-4">
      <Wifi class="h-4 w-4" />
      <AlertTitle>Network Error</AlertTitle>
      <AlertDescription>
        Unable to connect to search services. Please check your internet connection and try again.
      </AlertDescription>
      <div class="mt-3 flex space-x-2">
        <Button size="sm" variant="outline" @click="$emit('retry')">
          <RefreshCw class="w-3 h-3 mr-1" />
          Retry
        </Button>
        <Button size="sm" variant="ghost" @click="checkConnection">
          <Wifi class="w-3 h-3 mr-1" />
          Test Connection
        </Button>
      </div>
    </Alert>

    <!-- Rate Limit Error -->
    <Alert v-else-if="errorType === 'rate_limit'" variant="destructive" class="mb-4">
      <Clock class="h-4 w-4" />
      <AlertTitle>Rate Limit Exceeded</AlertTitle>
      <AlertDescription>
        Too many search requests. Please wait {{ formatTime(retryAfter) }} before trying again.
      </AlertDescription>
      <div class="mt-3">
        <div class="flex items-center space-x-2 text-sm text-muted-foreground">
          <Clock class="w-3 h-3" />
          <span>Retry available in: {{ countdown }}</span>
        </div>
        <Button
          size="sm"
          variant="outline"
          class="mt-2"
          :disabled="retryAfter > 0"
          @click="$emit('retry')"
        >
          <RefreshCw class="w-3 h-3 mr-1" />
          {{ retryAfter > 0 ? `Wait ${formatTime(retryAfter)}` : 'Retry Now' }}
        </Button>
      </div>
    </Alert>

    <!-- Authentication Error -->
    <Alert v-else-if="errorType === 'auth'" variant="destructive" class="mb-4">
      <Key class="h-4 w-4" />
      <AlertTitle>Authentication Failed</AlertTitle>
      <AlertDescription>
        Invalid or missing API key for {{ provider }}. Please check your configuration.
      </AlertDescription>
      <div class="mt-3 flex space-x-2">
        <Button size="sm" variant="outline" @click="$emit('configure')">
          <Settings class="w-3 h-3 mr-1" />
          Configure API Keys
        </Button>
        <Button size="sm" variant="ghost" @click="$emit('switch-provider')">
          <ArrowRight class="w-3 h-3 mr-1" />
          Try Different Provider
        </Button>
      </div>
    </Alert>

    <!-- Provider Unavailable -->
    <Alert v-else-if="errorType === 'provider_unavailable'" variant="destructive" class="mb-4">
      <AlertTriangle class="h-4 w-4" />
      <AlertTitle>Provider Unavailable</AlertTitle>
      <AlertDescription>
        {{ provider }} search service is currently unavailable.
        {{ fallbackAvailable ? 'Trying fallback provider...' : 'No fallback providers available.' }}
      </AlertDescription>
      <div class="mt-3 flex space-x-2">
        <Button
          size="sm"
          variant="outline"
          @click="$emit('retry')"
          :disabled="isRetrying"
        >
          <RefreshCw class="w-3 h-3 mr-1" :class="{ 'animate-spin': isRetrying }" />
          {{ isRetrying ? 'Retrying...' : 'Retry' }}
        </Button>
        <Button size="sm" variant="ghost" @click="$emit('check-status')">
          <Activity class="w-3 h-3 mr-1" />
          Check Status
        </Button>
      </div>
    </Alert>

    <!-- Search Failed -->
    <Alert v-else-if="errorType === 'search_failed'" variant="destructive" class="mb-4">
      <Search class="h-4 w-4" />
      <AlertTitle>Search Failed</AlertTitle>
      <AlertDescription>
        {{ errorMessage || 'The search request failed. Please try again with different terms.' }}
      </AlertDescription>
      <div class="mt-3 flex space-x-2">
        <Button size="sm" variant="outline" @click="$emit('retry')">
          <RefreshCw class="w-3 h-3 mr-1" />
          Retry Search
        </Button>
        <Button size="sm" variant="ghost" @click="$emit('modify-query')">
          <Edit class="w-3 h-3 mr-1" />
          Modify Query
        </Button>
      </div>
    </Alert>

    <!-- Generic Error -->
    <Alert v-else variant="destructive" class="mb-4">
      <AlertCircle class="h-4 w-4" />
      <AlertTitle>Search Error</AlertTitle>
      <AlertDescription>
        {{ errorMessage || 'An unexpected error occurred during the search operation.' }}
      </AlertDescription>
      <div class="mt-3 flex space-x-2">
        <Button size="sm" variant="outline" @click="$emit('retry')">
          <RefreshCw class="w-3 h-3 mr-1" />
          Retry
        </Button>
        <Button size="sm" variant="ghost" @click="showDetails = !showDetails">
          <Info class="w-3 h-3 mr-1" />
          {{ showDetails ? 'Hide' : 'Show' }} Details
        </Button>
      </div>

      <!-- Error Details -->
      <div v-if="showDetails" class="mt-3 p-3 bg-muted rounded-lg">
        <div class="text-xs font-mono text-muted-foreground">
          <div><strong>Error Code:</strong> {{ errorCode || 'Unknown' }}</div>
          <div><strong>Provider:</strong> {{ provider || 'Unknown' }}</div>
          <div><strong>Timestamp:</strong> {{ new Date().toLocaleString() }}</div>
          <div v-if="errorDetails" class="mt-2">
            <strong>Details:</strong>
            <pre class="mt-1 whitespace-pre-wrap">{{ errorDetails }}</pre>
          </div>
        </div>
      </div>
    </Alert>

    <!-- Suggestions -->
    <div v-if="suggestions.length > 0" class="suggestions mt-4">
      <h4 class="text-sm font-medium mb-2">Suggestions:</h4>
      <ul class="space-y-1 text-sm text-muted-foreground">
        <li v-for="suggestion in suggestions" :key="suggestion" class="flex items-start space-x-2">
          <Lightbulb class="w-3 h-3 mt-0.5 flex-shrink-0" />
          <span>{{ suggestion }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
	Activity,
	AlertCircle,
	AlertTriangle,
	ArrowRight,
	Clock,
	Edit,
	Info,
	Key,
	Lightbulb,
	RefreshCw,
	Search,
	Settings,
	Wifi,
} from "lucide-vue-next";
import { computed, onMounted, onUnmounted, ref } from "vue";

// Props
interface Props {
	errorType:
		| "network"
		| "rate_limit"
		| "auth"
		| "provider_unavailable"
		| "search_failed"
		| "generic";
	errorMessage?: string;
	errorCode?: string;
	errorDetails?: string;
	provider?: string;
	retryAfter?: number;
	fallbackAvailable?: boolean;
	isRetrying?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
	retryAfter: 0,
	fallbackAvailable: false,
	isRetrying: false,
});

// Emits
defineEmits<{
	retry: [];
	configure: [];
	"switch-provider": [];
	"check-status": [];
	"modify-query": [];
}>();

// State
const showDetails = ref(false);
const countdown = ref("");
let countdownInterval: NodeJS.Timeout | null = null;

// Computed
const suggestions = computed(() => {
	const suggestionMap: Record<string, string[]> = {
		network: [
			"Check your internet connection",
			"Try refreshing the page",
			"Disable VPN if active",
		],
		rate_limit: [
			"Wait for the rate limit to reset",
			"Try using a different search provider",
			"Reduce the number of search results requested",
		],
		auth: [
			"Verify your API key is correct",
			"Check if your API key has expired",
			"Ensure you have sufficient API credits",
		],
		provider_unavailable: [
			"Try a different search provider",
			"Check the provider status page",
			"Wait and try again later",
		],
		search_failed: [
			"Try different search terms",
			"Reduce the complexity of your query",
			"Check for typos in your search terms",
		],
		generic: [
			"Try refreshing the page",
			"Check your internet connection",
			"Contact support if the problem persists",
		],
	};

	return suggestionMap[props.errorType] || suggestionMap.generic;
});

// Methods
const formatTime = (seconds: number): string => {
	if (seconds < 60) return `${seconds}s`;
	const minutes = Math.floor(seconds / 60);
	const remainingSeconds = seconds % 60;
	return `${minutes}m ${remainingSeconds}s`;
};

const updateCountdown = () => {
	if (props.retryAfter > 0) {
		countdown.value = formatTime(props.retryAfter);
	} else {
		countdown.value = "";
	}
};

const checkConnection = async () => {
	try {
		const response = await fetch("/api/health", { method: "HEAD" });
		if (response.ok) {
			alert("Connection is working. The issue may be with the search service.");
		} else {
			alert("Connection issue detected. Please check your network.");
		}
	} catch {
		alert(
			"Unable to connect to the server. Please check your internet connection.",
		);
	}
};

// Lifecycle
onMounted(() => {
	updateCountdown();
	if (props.retryAfter > 0) {
		countdownInterval = setInterval(updateCountdown, 1000);
	}
});

onUnmounted(() => {
	if (countdownInterval) {
		clearInterval(countdownInterval);
	}
});
</script>

<style scoped>
.search-error-handler {
  @apply w-full;
}

.suggestions {
  @apply bg-muted/30 border rounded-lg p-3;
}

pre {
  @apply text-xs bg-background border rounded p-2 mt-1;
}
</style>
