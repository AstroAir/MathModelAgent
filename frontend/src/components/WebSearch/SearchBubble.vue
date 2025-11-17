<template>
  <div class="search-bubble">
    <!-- Web Search Tool Call -->
    <div v-if="isSearchToolCall" class="tool-call-bubble">
      <div class="flex items-start space-x-3 p-4 bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-lg">
        <div class="flex-shrink-0">
          <div class="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
            <Search class="w-4 h-4 text-blue-600 dark:text-blue-400" />
          </div>
        </div>

        <div class="flex-1 min-w-0">
          <div class="flex items-center space-x-2 mb-2">
            <h4 class="text-sm font-medium text-blue-900 dark:text-blue-100">Web Search</h4>
            <Badge variant="secondary" class="text-xs">{{ searchParams.search_type || 'general' }}</Badge>
          </div>

          <div class="space-y-2">
            <p class="text-sm text-blue-800 dark:text-blue-200">
              <span class="font-medium">Query:</span> "{{ searchParams.query }}"
            </p>

            <div class="flex flex-wrap gap-2 text-xs text-blue-600 dark:text-blue-300">
              <span v-if="searchParams.provider" class="bg-blue-100 dark:bg-blue-900 px-2 py-1 rounded">
                Provider: {{ searchParams.provider }}
              </span>
              <span v-if="searchParams.max_results" class="bg-blue-100 dark:bg-blue-900 px-2 py-1 rounded">
                Max results: {{ searchParams.max_results }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Web Search Results -->
    <div v-else-if="isSearchResult" class="search-result-bubble">
      <div v-if="parsedResults.length > 0" class="search-results-container">
        <div class="mb-4 p-3 bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-800 rounded-lg">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center space-x-2">
              <CheckCircle class="w-4 h-4 text-green-600 dark:text-green-400" />
              <span class="text-sm font-medium text-green-900 dark:text-green-100">Search Completed</span>
            </div>
            <Badge variant="outline" class="text-xs">{{ parsedResults.length }} results</Badge>
          </div>

          <p class="text-xs text-green-700 dark:text-green-300">
            Found {{ parsedResults.length }} results for "{{ extractQuery() }}"
          </p>
        </div>

        <!-- Compact Results Display -->
        <div class="space-y-3">
          <div
            v-for="(result, index) in displayResults"
            :key="index"
            class="result-item border rounded-lg p-3 hover:bg-muted/50 transition-colors"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1 min-w-0">
                <h5
                  class="text-sm font-medium text-primary hover:underline cursor-pointer truncate"
                  @click="openUrl(result.url)"
                  :title="result.title"
                >
                  {{ result.title }}
                </h5>
                <p class="text-xs text-muted-foreground mt-1 line-clamp-2">
                  {{ result.content }}
                </p>
                <div class="flex items-center space-x-2 mt-2">
                  <span class="text-xs text-green-600 font-medium">{{ getDomain(result.url) }}</span>
                  <Badge v-if="result.score" variant="outline" class="text-xs">
                    {{ Math.round(result.score * 100) }}%
                  </Badge>
                </div>
              </div>

              <div class="flex items-center space-x-1 ml-2">
                <Button variant="ghost" size="sm" @click="openUrl(result.url)" title="Open">
                  <ExternalLink class="w-3 h-3" />
                </Button>
                <Button variant="ghost" size="sm" @click="copyResult(result)" title="Copy">
                  <Copy class="w-3 h-3" />
                </Button>
              </div>
            </div>
          </div>
        </div>

        <!-- Show More Toggle -->
        <div v-if="parsedResults.length > 3" class="mt-3 text-center">
          <Button variant="outline" size="sm" @click="showAll = !showAll">
            {{ showAll ? 'Show Less' : `Show ${parsedResults.length - 3} More` }}
            <ChevronDown
              class="w-3 h-3 ml-1 transition-transform"
              :class="{ 'rotate-180': showAll }"
            />
          </Button>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="hasError" class="error-state">
        <Alert variant="destructive">
          <AlertCircle class="h-4 w-4" />
          <AlertTitle>Search Failed</AlertTitle>
          <AlertDescription>{{ content }}</AlertDescription>
        </Alert>
      </div>

      <!-- No Results -->
      <div v-else class="no-results">
        <div class="text-center py-4 text-muted-foreground">
          <Search class="w-6 h-6 mx-auto mb-2 opacity-50" />
          <p class="text-sm">No results found</p>
        </div>
      </div>
    </div>

    <!-- Regular Tool Message (fallback) -->
    <div v-else class="regular-tool-message">
      <div class="flex items-start space-x-3 p-3 bg-muted/30 border rounded-lg">
        <div class="flex-shrink-0">
          <div class="w-6 h-6 bg-muted rounded-full flex items-center justify-center">
            <Wrench class="w-3 h-3 text-muted-foreground" />
          </div>
        </div>
        <div class="flex-1">
          <p class="text-sm text-muted-foreground">{{ content }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import {
  Search, CheckCircle, ExternalLink, Copy, ChevronDown,
  AlertCircle, Wrench
} from 'lucide-vue-next';

// Props
interface Props {
  content: string;
  message?: any;
}

const props = defineProps<Props>();

// State
const showAll = ref(false);

// Computed properties
const isSearchToolCall = computed(() => {
  return props.message?.tool_name === 'web_search' &&
         props.message?.msg_type === 'tool' &&
         props.content.includes('web_search');
});

const isSearchResult = computed(() => {
  return props.content.includes('Search successful') ||
         props.content.includes('Found') && props.content.includes('results') ||
         props.content.includes('Search failed');
});

const hasError = computed(() => {
  return props.content.includes('Search failed') ||
         props.content.includes('error') ||
         props.content.includes('failed');
});

const searchParams = computed(() => {
  if (!isSearchToolCall.value) return {};

  try {
    // Extract search parameters from tool call content
    const queryMatch = props.content.match(/query['":\s]+([^'",\n]+)/i);
    const typeMatch = props.content.match(/search_type['":\s]+([^'",\n]+)/i);
    const providerMatch = props.content.match(/provider['":\s]+([^'",\n]+)/i);
    const maxResultsMatch = props.content.match(/max_results['":\s]+(\d+)/i);

    return {
      query: queryMatch?.[1]?.trim() || '',
      search_type: typeMatch?.[1]?.trim() || 'general',
      provider: providerMatch?.[1]?.trim(),
      max_results: maxResultsMatch?.[1] ? parseInt(maxResultsMatch[1]) : undefined
    };
  } catch {
    return {};
  }
});

const parsedResults = computed(() => {
  if (!isSearchResult.value || hasError.value) return [];

  try {
    const lines = props.content.split('\n');
    const results: any[] = [];
    let currentResult: any = {};

    for (const line of lines) {
      const trimmedLine = line.trim();

      if (trimmedLine.match(/^\d+\.\s/)) {
        // New result
        if (currentResult.title) {
          results.push(currentResult);
        }
        currentResult = {
          title: trimmedLine.replace(/^\d+\.\s/, '').trim()
        };
      } else if (trimmedLine.startsWith('URL:')) {
        currentResult.url = trimmedLine.replace('URL:', '').trim();
      } else if (trimmedLine.startsWith('Snippet:')) {
        currentResult.content = trimmedLine.replace('Snippet:', '').trim();
      } else if (trimmedLine && currentResult.title && !currentResult.content) {
        currentResult.content = trimmedLine;
      }
    }

    if (currentResult.title) {
      results.push(currentResult);
    }

    return results;
  } catch {
    return [];
  }
});

const displayResults = computed(() => {
  if (showAll.value || parsedResults.value.length <= 3) {
    return parsedResults.value;
  }
  return parsedResults.value.slice(0, 3);
});

// Methods
const extractQuery = (): string => {
  const queryMatch = props.content.match(/for "([^"]+)"/);
  return queryMatch?.[1] || searchParams.value.query || 'search query';
};

const getDomain = (url: string): string => {
  try {
    return new URL(url).hostname;
  } catch {
    return url;
  }
};

const openUrl = (url: string) => {
  window.open(url, '_blank');
};

const copyResult = async (result: any) => {
  try {
    const text = `${result.title}\n${result.url}\n${result.content || ''}`;
    await navigator.clipboard.writeText(text);
  } catch (err) {
    console.error('Failed to copy result:', err);
  }
};
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.result-item {
  @apply bg-card;
}

.search-bubble {
  @apply w-full;
}
</style>
