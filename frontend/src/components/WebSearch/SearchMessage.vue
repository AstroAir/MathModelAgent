<template>
  <div class="search-message">
    <!-- Search Tool Call Message -->
    <div v-if="messageType === 'tool_call'" class="tool-call-message mb-4">
      <div class="flex items-center space-x-2 mb-2">
        <Search class="w-4 h-4 text-primary" />
        <span class="text-sm font-medium">Web Search</span>
        <Badge variant="secondary" class="text-xs">{{ searchData.search_type || 'general' }}</Badge>
      </div>

      <div class="search-query bg-muted/30 rounded-lg p-3">
        <p class="text-sm">
          <span class="font-medium">Searching for:</span> "{{ searchData.query }}"
        </p>
        <div class="flex items-center space-x-4 mt-2 text-xs text-muted-foreground">
          <span v-if="searchData.provider">Provider: {{ searchData.provider }}</span>
          <span v-if="searchData.max_results">Max results: {{ searchData.max_results }}</span>
        </div>
      </div>
    </div>

    <!-- Search Results Message -->
    <div v-else-if="messageType === 'tool_result'" class="tool-result-message">
      <div v-if="searchResults.length > 0" class="search-results">
        <SearchResultsCard
          :results="searchResults"
          :query="searchData.query"
          :search-time="searchTime"
          :total-results="totalResults"
          :initial-display-count="3"
          @add-to-chat="handleAddToChat"
          @url-opened="handleUrlOpened"
          @new-search="handleNewSearch"
        />
      </div>

      <div v-else-if="errorMessage" class="search-error">
        <Alert variant="destructive">
          <AlertCircle class="h-4 w-4" />
          <AlertTitle>Search Failed</AlertTitle>
          <AlertDescription>{{ errorMessage }}</AlertDescription>
        </Alert>
      </div>

      <div v-else class="no-results">
        <div class="text-center py-6 text-muted-foreground">
          <Search class="w-8 h-8 mx-auto mb-2 opacity-50" />
          <p class="text-sm">No results found for "{{ searchData.query }}"</p>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-else-if="messageType === 'loading'" class="search-loading">
      <div class="flex items-center space-x-3 p-4 bg-muted/20 rounded-lg">
        <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-primary"></div>
        <div>
          <p class="text-sm font-medium">Searching the web...</p>
          <p class="text-xs text-muted-foreground">Finding relevant information for "{{ searchData.query }}"</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import type { SearchResult } from "@/types/search";
import { AlertCircle, Search } from "lucide-vue-next";
import { computed } from "vue";
import SearchResultsCard from "./SearchResultsCard.vue";

// Props
interface Props {
	messageType: "tool_call" | "tool_result" | "loading";
	searchData: {
		query: string;
		search_type?: string;
		provider?: string;
		max_results?: number;
	};
	content?: string;
	error?: string;
}

const props = defineProps<Props>();

// Emits
const emit = defineEmits<{
	"add-to-chat": [content: string];
	"url-opened": [url: string];
	"new-search": [];
}>();

// Computed properties
const searchResults = computed<SearchResult[]>(() => {
	if (!props.content || props.messageType !== "tool_result") return [];

	try {
		// Parse the search results from the content
		// This assumes the backend returns formatted search results
		const lines = props.content.split("\n");
		const results: SearchResult[] = [];

		let currentResult: Partial<SearchResult> = {};

		for (const line of lines) {
			if (line.match(/^\d+\.\s/)) {
				// New result starting
				if (currentResult.title) {
					results.push(currentResult as SearchResult);
				}
				currentResult = {
					title: line.replace(/^\d+\.\s/, "").trim(),
				};
			} else if (line.trim().startsWith("URL:")) {
				currentResult.url = line.replace("URL:", "").trim();
			} else if (line.trim().startsWith("Snippet:")) {
				currentResult.content = line.replace("Snippet:", "").trim();
			} else if (line.trim() && currentResult.title && !currentResult.content) {
				// Continuation of content
				currentResult.content = `${currentResult.content || ""} ${line.trim()}`;
			}
		}

		// Add the last result
		if (currentResult.title) {
			results.push(currentResult as SearchResult);
		}

		return results;
	} catch (error) {
		console.error("Failed to parse search results:", error);
		return [];
	}
});

const errorMessage = computed(() => {
	return (
		props.error ||
		(props.messageType === "tool_result" &&
		!searchResults.value.length &&
		props.content?.includes("failed")
			? props.content
			: null)
	);
});

const searchTime = computed(() => {
	// Extract search time from content if available
	const timeMatch = props.content?.match(/in ([\d.]+)s/);
	return timeMatch ? Number.parseFloat(timeMatch[1]) : 0;
});

const totalResults = computed(() => {
	// Extract total results from content if available
	const resultsMatch = props.content?.match(/Found (\d+) results/);
	return resultsMatch
		? Number.parseInt(resultsMatch[1])
		: searchResults.value.length;
});

// Methods
const handleAddToChat = (content: string) => {
	emit("add-to-chat", content);
};

const handleUrlOpened = (url: string) => {
	emit("url-opened", url);
};

const handleNewSearch = () => {
	emit("new-search");
};
</script>

<style scoped>
.search-message {
  @apply w-full;
}

.tool-call-message {
  @apply border-l-4 border-primary pl-4;
}

.tool-result-message {
  @apply mt-2;
}

.search-loading {
  @apply border-l-4 border-yellow-400 pl-4;
}

.search-error {
  @apply mt-2;
}

.no-results {
  @apply bg-muted/20 rounded-lg;
}
</style>
