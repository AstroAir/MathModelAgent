<template>
  <div class="search-results-card">
    <!-- Search Results Header -->
    <div class="results-header">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center space-x-2">
          <Search class="w-5 h-5 text-primary" />
          <h3 class="text-lg font-semibold">Web Search Results</h3>
          <Badge variant="secondary">{{ results.length }} results</Badge>
        </div>
        <div class="flex items-center space-x-2 text-sm text-muted-foreground">
          <Clock class="w-4 h-4" />
          <span>{{ searchTime.toFixed(2) }}s</span>
        </div>
      </div>

      <div class="search-info mb-4 p-3 bg-muted/30 rounded-lg">
        <p class="text-sm">
          <span class="font-medium">Query:</span> "{{ query }}"
        </p>
        <p class="text-xs text-muted-foreground mt-1">
          Found {{ totalResults }} total results • Showing top {{ results.length }}
        </p>
      </div>
    </div>

    <!-- Compact Results List -->
    <div class="results-list space-y-3">
      <div
        v-for="(result, index) in displayResults"
        :key="index"
        class="result-card border rounded-lg p-4 hover:bg-muted/20 transition-colors"
      >
        <!-- Result Header -->
        <div class="result-header mb-2">
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <h4
                class="text-base font-medium text-primary hover:underline cursor-pointer truncate"
                @click="openUrl(result.url)"
                :title="result.title"
              >
                {{ result.title }}
              </h4>
              <div class="flex items-center space-x-2 mt-1">
                <span class="text-sm text-green-600 font-medium">
                  {{ getDomain(result.url) }}
                </span>
                <Badge v-if="result.score" variant="outline" class="text-xs">
                  {{ Math.round(result.score * 100) }}%
                </Badge>
              </div>
            </div>

            <div class="flex items-center space-x-1 ml-2">
              <Button
                variant="ghost"
                size="sm"
                @click="openUrl(result.url)"
                title="Open in new tab"
              >
                <ExternalLink class="w-4 h-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                @click="copyToChat(result)"
                title="Add to chat"
              >
                <MessageSquare class="w-4 h-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                @click="copyUrl(result.url)"
                title="Copy URL"
              >
                <Copy class="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>

        <!-- Result Content Preview -->
        <div class="result-content">
          <p class="text-sm text-muted-foreground line-clamp-2 leading-relaxed">
            {{ result.content || 'No content preview available.' }}
          </p>
        </div>

        <!-- Result Metadata -->
        <div v-if="result.published_date" class="result-metadata mt-2 pt-2 border-t">
          <div class="flex items-center text-xs text-muted-foreground">
            <Calendar class="w-3 h-3 mr-1" />
            <span>{{ formatDate(result.published_date) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Show More/Less Toggle -->
    <div v-if="results.length > initialDisplayCount" class="show-more-container mt-4 text-center">
      <Button
        variant="outline"
        size="sm"
        @click="toggleShowAll"
      >
        {{ showAll ? 'Show Less' : `Show ${results.length - initialDisplayCount} More` }}
        <ChevronDown
          class="w-4 h-4 ml-1 transition-transform"
          :class="{ 'rotate-180': showAll }"
        />
      </Button>
    </div>

    <!-- Action Buttons -->
    <div class="action-buttons mt-4 pt-4 border-t flex justify-between">
      <div class="flex space-x-2">
        <Button variant="outline" size="sm" @click="$emit('new-search')">
          <Search class="w-4 h-4 mr-1" />
          New Search
        </Button>
        <Button variant="outline" size="sm" @click="exportResults">
          <Download class="w-4 h-4 mr-1" />
          Export
        </Button>
      </div>

      <Button variant="outline" size="sm" @click="addAllToChat">
        <MessageSquare class="w-4 h-4 mr-1" />
        Add All to Chat
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { SearchResult } from "@/types/search";
import {
	Calendar,
	ChevronDown,
	Clock,
	Copy,
	Download,
	ExternalLink,
	MessageSquare,
	Search,
} from "lucide-vue-next";
import { computed, ref } from "vue";

// Props
interface Props {
	results: SearchResult[];
	query: string;
	searchTime: number;
	totalResults: number;
	initialDisplayCount?: number;
}

const props = withDefaults(defineProps<Props>(), {
	initialDisplayCount: 5,
});

// Emits
const emit = defineEmits<{
	"new-search": [];
	"add-to-chat": [content: string];
	"url-opened": [url: string];
}>();

// State
const showAll = ref(false);

// Computed
const displayResults = computed(() => {
	if (showAll.value || props.results.length <= props.initialDisplayCount) {
		return props.results;
	}
	return props.results.slice(0, props.initialDisplayCount);
});

// Methods
const getDomain = (url: string): string => {
	try {
		return new URL(url).hostname;
	} catch {
		return url;
	}
};

const formatDate = (dateString: string): string => {
	try {
		const date = new Date(dateString);
		return date.toLocaleDateString("en-US", {
			year: "numeric",
			month: "short",
			day: "numeric",
		});
	} catch {
		return dateString;
	}
};

const openUrl = (url: string) => {
	window.open(url, "_blank");
	emit("url-opened", url);
};

const copyUrl = async (url: string) => {
	try {
		await navigator.clipboard.writeText(url);
		// Could add toast notification here
	} catch (err) {
		console.error("Failed to copy URL:", err);
	}
};

const copyToChat = (result: SearchResult) => {
	const content = `**${result.title}**\n${result.url}\n\n${result.content || "No content preview available."}`;
	emit("add-to-chat", content);
};

const addAllToChat = () => {
	const allContent = props.results
		.map(
			(result, index) =>
				`${index + 1}. **${result.title}**\n   ${result.url}\n   ${result.content || "No content preview available."}`,
		)
		.join("\n\n");

	const summary = `**Web Search Results for "${props.query}"**\n\nFound ${props.totalResults} results in ${props.searchTime.toFixed(2)}s:\n\n${allContent}`;
	emit("add-to-chat", summary);
};

const toggleShowAll = () => {
	showAll.value = !showAll.value;
};

const exportResults = () => {
	const exportData = {
		query: props.query,
		searchTime: props.searchTime,
		totalResults: props.totalResults,
		timestamp: new Date().toISOString(),
		results: props.results.map((result) => ({
			title: result.title,
			url: result.url,
			content: result.content,
			source: result.source,
			published_date: result.published_date,
			score: result.score,
		})),
	};

	const blob = new Blob([JSON.stringify(exportData, null, 2)], {
		type: "application/json",
	});

	const url = URL.createObjectURL(blob);
	const a = document.createElement("a");
	a.href = url;
	a.download = `search-results-${props.query.replace(/[^a-z0-9]/gi, "-")}-${Date.now()}.json`;
	document.body.appendChild(a);
	a.click();
	document.body.removeChild(a);
	URL.revokeObjectURL(url);
};
</script>

<style scoped>
.search-results-card {
  @apply bg-card border rounded-lg p-4;
}

.result-card {
  @apply bg-background;
}

.result-card:hover {
  @apply shadow-sm;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.show-more-container {
  @apply border-t pt-4;
}

.action-buttons {
  @apply bg-muted/20 -mx-4 -mb-4 px-4 py-3 rounded-b-lg;
}
</style>
