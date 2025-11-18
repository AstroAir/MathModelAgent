<template>
  <div class="search-results">
    <!-- Results Header -->
    <div class="results-header mb-4 p-4 bg-muted/30 rounded-lg">
      <div class="flex justify-between items-center">
        <div>
          <h3 class="text-lg font-semibold">Search Results</h3>
          <p class="text-sm text-muted-foreground">
            Found {{ totalResults }} results for "{{ query }}" in {{ searchTime.toFixed(2) }}s
          </p>
        </div>
        <div class="flex space-x-2">
          <Button variant="outline" size="sm" @click="exportResults">
            <Download class="w-4 h-4 mr-1" />
            Export
          </Button>
          <Button variant="outline" size="sm" @click="$emit('refresh')">
            <RefreshCw class="w-4 h-4 mr-1" />
            Refresh
          </Button>
        </div>
      </div>
    </div>

    <!-- Results List -->
    <div class="results-list space-y-4">
      <div
        v-for="(result, index) in results"
        :key="index"
        class="result-item border rounded-lg p-4 hover:shadow-md transition-shadow"
      >
        <!-- Result Header -->
        <div class="result-header mb-2">
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <h4 class="text-lg font-medium text-primary hover:underline cursor-pointer"
                  @click="$emit('open-url', result.url)">
                {{ result.title }}
              </h4>
              <div class="flex items-center space-x-2 mt-1">
                <span class="text-sm text-green-600 font-medium">{{ result.source || getDomain(result.url) }}</span>
                <span class="text-xs text-muted-foreground">{{ result.url }}</span>
                <Badge v-if="result.score" variant="secondary" class="text-xs">
                  Score: {{ (result.score * 100).toFixed(0) }}%
                </Badge>
              </div>
            </div>
            <div class="flex items-center space-x-1 ml-4">
              <Button variant="ghost" size="sm" @click="$emit('open-url', result.url)">
                <ExternalLink class="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" @click="$emit('get-content', result.url)">
                <FileText class="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" @click="copyUrl(result.url)">
                <Copy class="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>

        <!-- Result Content -->
        <div class="result-content">
          <p class="text-sm text-muted-foreground leading-relaxed">
            {{ result.content || 'No content preview available.' }}
          </p>
        </div>

        <!-- Result Metadata -->
        <div v-if="result.published_date || result.metadata" class="result-metadata mt-3 pt-3 border-t">
          <div class="flex flex-wrap gap-2 text-xs text-muted-foreground">
            <span v-if="result.published_date" class="flex items-center">
              <Calendar class="w-3 h-3 mr-1" />
              {{ formatDate(result.published_date) }}
            </span>
            <span v-if="result.metadata?.author" class="flex items-center">
              <User class="w-3 h-3 mr-1" />
              {{ result.metadata.author }}
            </span>
            <span v-if="result.metadata?.highlights?.length" class="flex items-center">
              <Highlight class="w-3 h-3 mr-1" />
              {{ result.metadata.highlights.length }} highlights
            </span>
          </div>
        </div>

        <!-- Expandable Content -->
        <div v-if="result.metadata?.highlights?.length" class="mt-3">
          <Button
            variant="ghost"
            size="sm"
            @click="toggleHighlights(index)"
            class="text-xs"
          >
            <ChevronDown
              class="w-3 h-3 mr-1 transition-transform"
              :class="{ 'rotate-180': expandedResults.has(index) }"
            />
            {{ expandedResults.has(index) ? 'Hide' : 'Show' }} Highlights
          </Button>

          <div v-if="expandedResults.has(index)" class="mt-2 space-y-1">
            <div
              v-for="(highlight, hIndex) in result.metadata.highlights"
              :key="hIndex"
              class="text-xs bg-yellow-50 dark:bg-yellow-900/20 p-2 rounded border-l-2 border-yellow-400"
            >
              "{{ highlight }}"
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Load More Button -->
    <div v-if="canLoadMore" class="load-more mt-6 text-center">
      <Button variant="outline" @click="$emit('load-more')" :disabled="isLoadingMore">
        <MoreHorizontal class="w-4 h-4 mr-2" />
        Load More Results
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
	Copy,
	Download,
	ExternalLink,
	FileText,
	Highlighter as Highlight,
	MoreHorizontal,
	RefreshCw,
	User,
} from "lucide-vue-next";
import { ref } from "vue";

// Props
interface Props {
	results: SearchResult[];
	query: string;
	searchTime: number;
	totalResults: number;
	canLoadMore?: boolean;
	isLoadingMore?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
	canLoadMore: false,
	isLoadingMore: false,
});

// Emits
defineEmits<{
	"open-url": [url: string];
	"get-content": [url: string];
	refresh: [];
	"load-more": [];
}>();

// State
const expandedResults = ref(new Set<number>());

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

const copyUrl = async (url: string) => {
	try {
		await navigator.clipboard.writeText(url);
		// Could add a toast notification here
	} catch (err) {
		console.error("Failed to copy URL:", err);
	}
};

const toggleHighlights = (index: number) => {
	if (expandedResults.value.has(index)) {
		expandedResults.value.delete(index);
	} else {
		expandedResults.value.add(index);
	}
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
.search-results {
  @apply w-full;
}

.result-item {
  @apply bg-card;
}

.result-item:hover {
  @apply bg-muted/20;
}

.result-header h4 {
  @apply line-clamp-2;
}

.result-content p {
  @apply line-clamp-3;
}

.result-metadata {
  @apply bg-muted/20;
}

.load-more {
  @apply border-t pt-4;
}
</style>
