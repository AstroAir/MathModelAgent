<template>
  <div class="web-search-interface">
    <!-- Search Form -->
    <div class="search-form-container mb-6">
      <div class="flex flex-col space-y-4">
        <!-- Search Input -->
        <div class="flex space-x-2">
          <Input
            v-model="searchForm.query"
            placeholder="Enter your search query..."
            class="flex-1"
            @keyup.enter="handleSearch"
            :disabled="isLoading"
          />
          <Button
            @click="handleSearch"
            :disabled="!searchForm.query.trim() || isLoading"
            class="px-6"
          >
            <Search class="w-4 h-4 mr-2" />
            Search
          </Button>
        </div>

        <!-- Search Options -->
        <div class="flex flex-wrap gap-4 items-center">
          <!-- Search Type Selection -->
          <div class="flex items-center space-x-2">
            <Label for="search-type">Type:</Label>
            <Select v-model="searchForm.searchType">
              <SelectTrigger class="w-32">
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

          <!-- Provider Selection -->
          <div class="flex items-center space-x-2" v-if="showProviderSelection">
            <Label for="provider">Provider:</Label>
            <Select v-model="searchForm.provider">
              <SelectTrigger class="w-24">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">Auto</SelectItem>
                <SelectItem value="tavily">Tavily</SelectItem>
                <SelectItem value="exa">Exa</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <!-- Max Results -->
          <div class="flex items-center space-x-2">
            <Label for="max-results">Results:</Label>
            <Select v-model="searchForm.maxResults">
              <SelectTrigger class="w-16">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem :value="5">5</SelectItem>
                <SelectItem :value="10">10</SelectItem>
                <SelectItem :value="15">15</SelectItem>
                <SelectItem :value="20">20</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <!-- Advanced Options Toggle -->
          <Button
            variant="outline"
            size="sm"
            @click="showAdvanced = !showAdvanced"
          >
            <Settings class="w-4 h-4 mr-1" />
            Advanced
          </Button>
        </div>

        <!-- Advanced Options -->
        <div v-if="showAdvanced" class="advanced-options border rounded-lg p-4 bg-muted/50">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Domain Filter -->
            <div>
              <Label for="domains">Specific Domains (optional):</Label>
              <Input
                v-model="domainsInput"
                placeholder="example.com, github.com"
                class="mt-1"
              />
              <p class="text-xs text-muted-foreground mt-1">
                Comma-separated list of domains to search within
              </p>
            </div>

            <!-- Date Range -->
            <div>
              <Label>Date Range (optional):</Label>
              <div class="flex space-x-2 mt-1">
                <Input
                  v-model="dateRange.start"
                  type="date"
                  class="flex-1"
                />
                <Input
                  v-model="dateRange.end"
                  type="date"
                  class="flex-1"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-container flex items-center justify-center py-8">
      <div class="flex items-center space-x-3">
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
        <span>Searching...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="error-container mb-4">
      <Alert variant="destructive">
        <AlertCircle class="h-4 w-4" />
        <AlertTitle>Search Error</AlertTitle>
        <AlertDescription>{{ error }}</AlertDescription>
      </Alert>
    </div>

    <!-- Search Results -->
    <SearchResults
      v-if="!isLoading && results.length > 0"
      :results="results"
      :query="lastQuery"
      :search-time="searchTime"
      :total-results="totalResults"
      @open-url="handleOpenUrl"
      @get-content="handleGetContent"
    />

    <!-- No Results -->
    <div v-if="!isLoading && !error && results.length === 0 && lastQuery"
         class="no-results text-center py-8 text-muted-foreground">
      <Search class="w-12 h-12 mx-auto mb-4 opacity-50" />
      <p>No results found for "{{ lastQuery }}"</p>
      <p class="text-sm">Try adjusting your search terms or search type.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Search, Settings, AlertCircle } from 'lucide-vue-next';
import { performWebSearch, getWebContent } from '@/apis/searchApi';
import type { SearchFormData, SearchResult, SearchType } from '@/types/search';
import SearchResults from './SearchResults.vue';

// Props
interface Props {
  showProviderSelection?: boolean;
  defaultSearchType?: SearchType;
  defaultMaxResults?: number;
}

const props = withDefaults(defineProps<Props>(), {
  showProviderSelection: true,
  defaultSearchType: 'general' as SearchType,
  defaultMaxResults: 10
});

// Emits
const emit = defineEmits<{
  searchPerformed: [query: string, results: SearchResult[]];
  urlOpened: [url: string];
  contentRetrieved: [url: string, content: string];
}>();

// Reactive state
const searchForm = reactive<SearchFormData>({
  query: '',
  searchType: props.defaultSearchType,
  provider: undefined,
  maxResults: props.defaultMaxResults
});

const isLoading = ref(false);
const error = ref<string | null>(null);
const results = ref<SearchResult[]>([]);
const lastQuery = ref('');
const searchTime = ref(0);
const totalResults = ref(0);
const showAdvanced = ref(false);
const domainsInput = ref('');
const dateRange = reactive({
  start: '',
  end: ''
});

// Computed
const domains = computed(() => {
  return domainsInput.value
    ? domainsInput.value.split(',').map(d => d.trim()).filter(Boolean)
    : undefined;
});

const dateRangeFilter = computed(() => {
  if (!dateRange.start && !dateRange.end) return undefined;
  return {
    start_date: dateRange.start || undefined,
    end_date: dateRange.end || undefined
  };
});

// Methods
const handleSearch = async () => {
  if (!searchForm.query.trim() || isLoading.value) return;

  isLoading.value = true;
  error.value = null;
  results.value = [];

  try {
    const searchRequest = {
      query: searchForm.query,
      search_type: searchForm.searchType,
      provider: searchForm.provider || undefined,
      max_results: searchForm.maxResults,
      include_content: true,
      domains: domains.value,
      date_range: dateRangeFilter.value
    };

    const response = await performWebSearch(searchRequest);

    results.value = response.data.results;
    lastQuery.value = searchForm.query;
    searchTime.value = response.data.search_time;
    totalResults.value = response.data.total_results || response.data.results.length;

    emit('searchPerformed', lastQuery.value, results.value);
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || 'Search failed';
  } finally {
    isLoading.value = false;
  }
};

const handleOpenUrl = (url: string) => {
  window.open(url, '_blank');
  emit('urlOpened', url);
};

const handleGetContent = async (url: string) => {
  try {
    const response = await getWebContent([url]);
    const content = response.data[url];
    if (content) {
      emit('contentRetrieved', url, content);
    }
  } catch (err: any) {
    console.error('Failed to get content:', err);
  }
};

// Watch for external query updates
watch(() => props.defaultSearchType, (newType) => {
  searchForm.searchType = newType;
});

// Expose methods for parent components
defineExpose({
  search: handleSearch,
  clearResults: () => {
    results.value = [];
    lastQuery.value = '';
    error.value = null;
  },
  setQuery: (query: string) => {
    searchForm.query = query;
  }
});
</script>

<style scoped>
.web-search-interface {
  @apply w-full max-w-4xl mx-auto;
}

.search-form-container {
  @apply bg-card border rounded-lg p-4;
}

.advanced-options {
  @apply transition-all duration-200;
}

.loading-container {
  @apply text-muted-foreground;
}

.no-results {
  @apply bg-muted/30 rounded-lg;
}
</style>
