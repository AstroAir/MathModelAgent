<script setup lang="ts">
import { useLogStore } from "@/stores/log";
import type { LogLevel } from "@/types/log";
import {
	AlertTriangle,
	Bug,
	ChevronDown,
	ChevronUp,
	Clock,
	Download,
	Filter,
	Info,
	Pause,
	Play,
	RotateCcw,
	Search,
	Trash2,
	X,
} from "lucide-vue-next";
import { computed, nextTick, onMounted, onUnmounted, ref } from "vue";

const logStore = useLogStore();

// Component state
const isAutoScroll = ref(true);
const searchQuery = ref("");
const selectedLevels = ref<LogLevel[]>([
	"DEBUG",
	"INFO",
	"WARN",
	"ERROR",
	"FATAL",
]);
const selectedSource = ref("");
const startDate = ref("");
const endDate = ref("");
const expandedLogId = ref<string | null>(null);
const sortBy = ref<"timestamp" | "level" | "source">("timestamp");
const sortOrder = ref<"asc" | "desc">("desc");
const isRegexSearch = ref(false);
const showFilters = ref(false);
const pageSize = ref(50);
const currentPage = ref(0);

// Refs for DOM elements
const logContainer = ref<HTMLElement>();
const searchInput = ref<HTMLInputElement>();

// Log level colors and icons
const logLevelConfig = {
	DEBUG: { color: "text-muted-foreground bg-muted", icon: Bug },
	INFO: { color: "text-primary bg-primary/10", icon: Info },
	WARN: { color: "text-yellow-600 bg-yellow-500/10", icon: AlertTriangle },
	ERROR: { color: "text-destructive bg-destructive/10", icon: X },
	FATAL: { color: "text-destructive-foreground bg-destructive", icon: X },
};

// Computed properties
const filteredLogs = computed(() => {
	let logs = [...logStore.logs];

	// Filter by log levels
	logs = logs.filter((log) => selectedLevels.value.includes(log.level));

	// Filter by source
	if (selectedSource.value) {
		logs = logs.filter((log) => log.source === selectedSource.value);
	}

	// Filter by date range
	if (startDate.value) {
		const start = new Date(startDate.value).getTime();
		logs = logs.filter((log) => log.timestamp >= start);
	}
	if (endDate.value) {
		const end = new Date(endDate.value).getTime() + 24 * 60 * 60 * 1000 - 1; // End of day
		logs = logs.filter((log) => log.timestamp <= end);
	}

	// Filter by search query
	if (searchQuery.value.trim()) {
		const query = searchQuery.value.trim();
		if (isRegexSearch.value) {
			try {
				const regex = new RegExp(query, "i");
				logs = logs.filter((log) => regex.test(log.message));
			} catch (e) {
				// Invalid regex, fall back to simple search
				logs = logs.filter((log) =>
					log.message.toLowerCase().includes(query.toLowerCase()),
				);
			}
		} else {
			logs = logs.filter((log) =>
				log.message.toLowerCase().includes(query.toLowerCase()),
			);
		}
	}

	// Sort logs
	logs.sort((a, b) => {
		let comparison = 0;

		switch (sortBy.value) {
			case "timestamp":
				comparison = a.timestamp - b.timestamp;
				break;
			case "level":
				const levelOrder = { DEBUG: 0, INFO: 1, WARN: 2, ERROR: 3, FATAL: 4 };
				comparison = levelOrder[a.level] - levelOrder[b.level];
				break;
			case "source":
				comparison = a.source.localeCompare(b.source);
				break;
		}

		return sortOrder.value === "desc" ? -comparison : comparison;
	});

	return logs;
});

const uniqueSources = computed(() => {
	const sources = new Set(logStore.logs.map((log) => log.source));
	return Array.from(sources).sort();
});

const logStats = computed(() => {
	const stats = { DEBUG: 0, INFO: 0, WARN: 0, ERROR: 0, FATAL: 0 };
	filteredLogs.value.forEach((log) => {
		stats[log.level]++;
	});
	return stats;
});

// Paginated logs for performance
const paginatedLogs = computed(() => {
	const start = currentPage.value * pageSize.value;
	const end = start + pageSize.value;
	return filteredLogs.value.slice(start, end);
});

const totalPages = computed(() => {
	return Math.ceil(filteredLogs.value.length / pageSize.value);
});

const hasNextPage = computed(() => {
	return currentPage.value < totalPages.value - 1;
});

const hasPrevPage = computed(() => {
	return currentPage.value > 0;
});

// Methods
const formatTimestamp = (timestamp: number) => {
	const date = new Date(timestamp);
	return (
		date.toLocaleString("zh-CN", {
			month: "2-digit",
			day: "2-digit",
			hour: "2-digit",
			minute: "2-digit",
			second: "2-digit",
		}) +
		"." +
		String(date.getMilliseconds()).padStart(3, "0")
	);
};

const toggleLogExpansion = (logId: string) => {
	expandedLogId.value = expandedLogId.value === logId ? null : logId;
};

const clearLogs = () => {
	logStore.clearLogs();
	expandedLogId.value = null;
};

const toggleAutoScroll = () => {
	isAutoScroll.value = !isAutoScroll.value;
	if (isAutoScroll.value) {
		scrollToBottom();
	}
};

const scrollToBottom = async () => {
	if (!logContainer.value) return;
	await nextTick();
	logContainer.value.scrollTop = logContainer.value.scrollHeight;
};

const nextPage = () => {
	if (hasNextPage.value) {
		currentPage.value++;
	}
};

const prevPage = () => {
	if (hasPrevPage.value) {
		currentPage.value--;
	}
};

const resetFilters = () => {
	searchQuery.value = "";
	selectedLevels.value = ["DEBUG", "INFO", "WARN", "ERROR", "FATAL"];
	selectedSource.value = "";
	startDate.value = "";
	endDate.value = "";
	isRegexSearch.value = false;
};

const exportLogs = (format: "json" | "csv" | "txt") => {
	const logs = filteredLogs.value;
	let content = "";
	let filename = "";
	let mimeType = "";

	switch (format) {
		case "json":
			content = JSON.stringify(logs, null, 2);
			filename = `logs_${Date.now()}.json`;
			mimeType = "application/json";
			break;
		case "csv":
			const headers = ["Timestamp", "Level", "Source", "Message"];
			const csvRows = [
				headers.join(","),
				...logs.map((log) =>
					[
						new Date(log.timestamp).toISOString(),
						log.level,
						log.source,
						`"${log.message.replace(/"/g, '""')}"`,
					].join(","),
				),
			];
			content = csvRows.join("\n");
			filename = `logs_${Date.now()}.csv`;
			mimeType = "text/csv";
			break;
		case "txt":
			content = logs
				.map(
					(log) =>
						`[${formatTimestamp(log.timestamp)}] ${log.level} ${log.source}: ${log.message}`,
				)
				.join("\n");
			filename = `logs_${Date.now()}.txt`;
			mimeType = "text/plain";
			break;
	}

	const blob = new Blob([content], { type: mimeType });
	const url = URL.createObjectURL(blob);
	const a = document.createElement("a");
	a.href = url;
	a.download = filename;
	a.click();
	URL.revokeObjectURL(url);
};

// Quick filter presets
const applyQuickFilter = (preset: string) => {
	switch (preset) {
		case "errors":
			selectedLevels.value = ["ERROR", "FATAL"];
			break;
		case "lastHour":
			startDate.value = new Date(Date.now() - 60 * 60 * 1000)
				.toISOString()
				.slice(0, 16);
			break;
		case "currentSession":
			// Assuming session starts when component mounts
			startDate.value = new Date().toISOString().slice(0, 16);
			break;
	}
};

// Keyboard shortcuts
const handleKeydown = (event: KeyboardEvent) => {
	if (event.ctrlKey || event.metaKey) {
		switch (event.key) {
			case "k":
				event.preventDefault();
				searchInput.value?.focus();
				break;
			case "l":
				event.preventDefault();
				clearLogs();
				break;
			case "s":
				event.preventDefault();
				toggleAutoScroll();
				break;
		}
	}
};

// Auto-scroll when new logs are added
const handleLogUpdate = () => {
	if (isAutoScroll.value) {
		scrollToBottom();
	}
};

// Lifecycle
onMounted(() => {
	document.addEventListener("keydown", handleKeydown);
	// Watch for new logs and auto-scroll if enabled
	logStore.$subscribe(handleLogUpdate);
});

onUnmounted(() => {
	document.removeEventListener("keydown", handleKeydown);
});
</script>

<template>
  <div class="log-panel flex flex-col h-full bg-card border border-border rounded-lg shadow-sm">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-border bg-muted/50">
      <div class="flex items-center gap-2">
        <Bug class="w-5 h-5 text-muted-foreground" />
        <h3 class="text-lg font-semibold text-foreground">日志面板</h3>
        <span class="text-sm text-muted-foreground">({{ filteredLogs.length }} 条)</span>
      </div>

      <div class="flex items-center gap-2">
        <!-- Auto-scroll toggle -->
        <button
          @click="toggleAutoScroll"
          :class="[
            'flex items-center gap-1 px-3 py-1.5 text-sm rounded-md border transition-colors',
            isAutoScroll
              ? 'bg-green-500/10 border-green-500/20 text-green-600'
              : 'bg-muted border-border text-muted-foreground hover:bg-accent'
          ]"
        >
          <component :is="isAutoScroll ? Pause : Play" class="w-4 h-4" />
          {{ isAutoScroll ? '暂停滚动' : '自动滚动' }}
        </button>

        <!-- Clear logs -->
        <button
          @click="clearLogs"
          class="flex items-center gap-1 px-3 py-1.5 text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-md hover:bg-destructive/20 transition-colors"
        >
          <Trash2 class="w-4 h-4" />
          清空
        </button>

        <!-- Export dropdown -->
        <div class="relative group">
          <button class="flex items-center gap-1 px-3 py-1.5 text-sm text-muted-foreground bg-muted border border-border rounded-md hover:bg-accent transition-colors">
            <Download class="w-4 h-4" />
            导出
          </button>
          <div class="absolute right-0 top-full mt-1 bg-card border border-border rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
            <button @click="exportLogs('json')" class="block w-full text-left px-4 py-2 text-sm text-foreground hover:bg-accent">JSON</button>
            <button @click="exportLogs('csv')" class="block w-full text-left px-4 py-2 text-sm text-foreground hover:bg-accent">CSV</button>
            <button @click="exportLogs('txt')" class="block w-full text-left px-4 py-2 text-sm text-foreground hover:bg-accent">TXT</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="p-4 border-b border-border bg-muted/50">
      <!-- Search bar -->
      <div class="flex items-center gap-2 mb-3">
        <div class="relative flex-1">
          <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            ref="searchInput"
            v-model="searchQuery"
            type="text"
            placeholder="搜索日志消息... (Ctrl+K)"
            class="w-full pl-10 pr-4 py-2 border border-input rounded-md focus:ring-2 focus:ring-ring focus:border-ring"
          />
        </div>
        <label class="flex items-center gap-2 text-sm text-muted-foreground">
          <input v-model="isRegexSearch" type="checkbox" class="rounded" />
          正则表达式
        </label>
        <button
          @click="showFilters = !showFilters"
          :class="[
            'flex items-center gap-1 px-3 py-2 text-sm rounded-md border transition-colors',
            showFilters
              ? 'bg-primary/10 border-primary/20 text-primary'
              : 'bg-muted border-border text-muted-foreground hover:bg-accent'
          ]"
        >
          <Filter class="w-4 h-4" />
          筛选
          <component :is="showFilters ? ChevronUp : ChevronDown" class="w-4 h-4" />
        </button>
      </div>

      <!-- Expanded filters -->
      <div v-if="showFilters" class="space-y-3">
        <!-- Quick filter presets -->
        <div class="flex items-center gap-2">
          <span class="text-sm font-medium text-foreground">快速筛选:</span>
          <button @click="applyQuickFilter('errors')" class="px-2 py-1 text-xs bg-destructive/10 text-destructive rounded hover:bg-destructive/20">仅错误</button>
          <button @click="applyQuickFilter('lastHour')" class="px-2 py-1 text-xs bg-primary/10 text-primary rounded hover:bg-primary/20">最近一小时</button>
          <button @click="applyQuickFilter('currentSession')" class="px-2 py-1 text-xs bg-green-500/10 text-green-600 rounded hover:bg-green-500/20">当前会话</button>
          <button @click="resetFilters" class="px-2 py-1 text-xs bg-muted text-muted-foreground rounded hover:bg-accent flex items-center gap-1">
            <RotateCcw class="w-3 h-3" />
            重置
          </button>
        </div>

        <!-- Log level filters -->
        <div class="flex items-center gap-2 flex-wrap">
          <span class="text-sm font-medium text-foreground">日志级别:</span>
          <label v-for="level in ['DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL']" :key="level" class="flex items-center gap-1">
            <input
              v-model="selectedLevels"
              :value="level"
              type="checkbox"
              class="rounded"
            />
            <span :class="['text-xs px-2 py-1 rounded font-medium', logLevelConfig[level as LogLevel].color]">
              {{ level }}
            </span>
          </label>
        </div>

        <!-- Source and date filters -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div>
            <label class="block text-sm font-medium text-foreground mb-1">来源模块</label>
            <select v-model="selectedSource" class="w-full px-3 py-2 border border-input rounded-md focus:ring-2 focus:ring-ring focus:border-ring bg-background">
              <option value="">全部来源</option>
              <option v-for="source in uniqueSources" :key="source" :value="source">{{ source }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-foreground mb-1">开始时间</label>
            <input v-model="startDate" type="datetime-local" class="w-full px-3 py-2 border border-input rounded-md focus:ring-2 focus:ring-ring focus:border-ring bg-background" />
          </div>
          <div>
            <label class="block text-sm font-medium text-foreground mb-1">结束时间</label>
            <input v-model="endDate" type="datetime-local" class="w-full px-3 py-2 border border-input rounded-md focus:ring-2 focus:ring-ring focus:border-ring bg-background" />
          </div>
        </div>
      </div>
    </div>

    <!-- Log statistics -->
    <div class="px-4 py-2 bg-muted/50 border-b border-border">
      <div class="flex items-center gap-4 text-sm">
        <span class="font-medium text-foreground">统计:</span>
        <span v-for="(count, level) in logStats" :key="level" :class="['px-2 py-1 rounded text-xs font-medium', logLevelConfig[level as LogLevel].color]">
          {{ level }}: {{ count }}
        </span>
      </div>
    </div>

    <!-- Sorting controls -->
    <div class="px-4 py-2 bg-muted/50 border-b border-border">
      <div class="flex items-center gap-4 text-sm">
        <span class="font-medium text-foreground">排序:</span>
        <select v-model="sortBy" class="px-2 py-1 border border-input rounded text-xs bg-background">
          <option value="timestamp">时间</option>
          <option value="level">级别</option>
          <option value="source">来源</option>
        </select>
        <button
          @click="sortOrder = sortOrder === 'asc' ? 'desc' : 'asc'"
          class="flex items-center gap-1 px-2 py-1 text-xs bg-muted border border-border rounded hover:bg-accent"
        >
          {{ sortOrder === 'asc' ? '升序' : '降序' }}
          <component :is="sortOrder === 'asc' ? ChevronUp : ChevronDown" class="w-3 h-3" />
        </button>
      </div>
    </div>

    <!-- Log entries -->
    <div
      ref="logContainer"
      class="flex-1 overflow-y-auto p-4 space-y-2 bg-background"
    >
      <div v-if="filteredLogs.length === 0" class="text-center text-muted-foreground py-8">
        <Bug class="w-12 h-12 mx-auto mb-2 text-muted-foreground/50" />
        <p class="text-lg font-medium">暂无日志</p>
        <p class="text-sm">日志将在这里显示</p>
      </div>

      <div
        v-for="log in paginatedLogs"
        :key="log.id"
        class="log-entry border border-border rounded-lg overflow-hidden hover:shadow-sm transition-shadow"
      >
        <!-- Log entry header -->
        <div
          @click="toggleLogExpansion(log.id)"
          class="flex items-center gap-3 p-3 cursor-pointer hover:bg-accent transition-colors"
        >
          <!-- Log level indicator -->
          <div :class="['flex items-center gap-1 px-2 py-1 rounded text-xs font-medium', logLevelConfig[log.level].color]">
            <component :is="logLevelConfig[log.level].icon" class="w-3 h-3" />
            {{ log.level }}
          </div>

          <!-- Timestamp -->
          <div class="flex items-center gap-1 text-xs text-muted-foreground">
            <Clock class="w-3 h-3" />
            {{ formatTimestamp(log.timestamp) }}
          </div>

          <!-- Source -->
          <div class="text-xs text-muted-foreground bg-muted px-2 py-1 rounded">
            {{ log.source }}
          </div>

          <!-- Message preview -->
          <div class="flex-1 text-sm text-foreground truncate">
            <span v-if="searchQuery && !isRegexSearch" v-html="log.message.replace(new RegExp(searchQuery, 'gi'), '<mark class=&quot;bg-primary/20&quot;>$&</mark>')"></span>
            <span v-else>{{ log.message }}</span>
          </div>

          <!-- Expand indicator -->
          <component
            :is="expandedLogId === log.id ? ChevronUp : ChevronDown"
            class="w-4 h-4 text-muted-foreground"
          />
        </div>

        <!-- Expanded log details -->
        <div v-if="expandedLogId === log.id" class="border-t border-border bg-muted/50 p-3">
          <div class="space-y-3">
            <!-- Full message -->
            <div>
              <h4 class="text-sm font-medium text-foreground mb-2">完整消息</h4>
              <div class="bg-background border border-border rounded p-3 text-sm text-foreground whitespace-pre-wrap">{{ log.message }}</div>
            </div>

            <!-- Details (if available) -->
            <div v-if="log.details">
              <h4 class="text-sm font-medium text-foreground mb-2">详细信息</h4>
              <div class="bg-gray-900 dark:bg-black rounded-lg overflow-hidden">
                <pre class="text-xs text-gray-200 p-3 overflow-x-auto"><code>{{ JSON.stringify(log.details, null, 2) }}</code></pre>
              </div>
            </div>

            <!-- Log metadata -->
            <div class="grid grid-cols-2 gap-4 text-xs">
              <div>
                <span class="font-medium text-muted-foreground">日志ID:</span>
                <span class="text-foreground font-mono ml-1">{{ log.id }}</span>
              </div>
              <div>
                <span class="font-medium text-muted-foreground">精确时间:</span>
                <span class="text-foreground ml-1">{{ new Date(log.timestamp).toISOString() }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer with keyboard shortcuts -->
    <div class="px-4 py-2 bg-muted/50 border-t border-border text-xs text-muted-foreground">
      <div class="flex items-center gap-4">
        <span>快捷键:</span>
        <span><kbd class="px-1 py-0.5 bg-muted rounded">Ctrl+K</kbd> 搜索</span>
        <span><kbd class="px-1 py-0.5 bg-muted rounded">Ctrl+L</kbd> 清空</span>
        <span><kbd class="px-1 py-0.5 bg-muted rounded">Ctrl+S</kbd> 切换自动滚动</span>
      </div>
    </div>

    <!-- Pagination -->
    <div class="px-4 py-2 bg-muted/50 border-t border-border flex items-center justify-between text-sm">
      <div>
        <span class="text-muted-foreground">总计: {{ filteredLogs.length }} 条</span>
        <span class="text-muted-foreground/50 mx-2">|</span>
        <span class="text-muted-foreground">页数: {{ currentPage + 1 }} / {{ totalPages }}</span>
      </div>
      <div class="flex items-center gap-2">
        <button
          @click="prevPage"
          :disabled="!hasPrevPage"
          class="px-3 py-1 border border-border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-accent"
        >
          上一页
        </button>
        <button
          @click="nextPage"
          :disabled="!hasNextPage"
          class="px-3 py-1 border border-border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-accent"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>
