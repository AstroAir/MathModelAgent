<template>
  <div class="search-loading-state">
    <!-- Main Loading Display -->
    <div class="loading-container">
      <div class="flex items-start space-x-4 p-4 bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-lg">
        <!-- Animated Icon -->
        <div class="flex-shrink-0">
          <div class="relative">
            <div class="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
              <Search class="w-4 h-4 text-blue-600 dark:text-blue-400" />
            </div>
            <!-- Pulse Animation -->
            <div class="absolute inset-0 w-8 h-8 bg-blue-200 dark:bg-blue-800 rounded-full animate-ping opacity-75"></div>
          </div>
        </div>

        <!-- Loading Content -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center space-x-2 mb-2">
            <h4 class="text-sm font-medium text-blue-900 dark:text-blue-100">
              {{ loadingTitle }}
            </h4>
            <Badge variant="secondary" class="text-xs animate-pulse">
              {{ searchType }}
            </Badge>
          </div>

          <!-- Query Display -->
          <p class="text-sm text-blue-800 dark:text-blue-200 mb-3">
            <span class="font-medium">Searching for:</span> "{{ query }}"
          </p>

          <!-- Progress Steps -->
          <div class="space-y-2">
            <div
              v-for="(step, index) in progressSteps"
              :key="index"
              class="flex items-center space-x-2 text-xs"
            >
              <div class="flex-shrink-0">
                <CheckCircle
                  v-if="step.completed"
                  class="w-3 h-3 text-green-600 dark:text-green-400"
                />
                <div
                  v-else-if="step.active"
                  class="w-3 h-3 border-2 border-blue-600 dark:border-blue-400 rounded-full animate-spin border-t-transparent"
                ></div>
                <div
                  v-else
                  class="w-3 h-3 border-2 border-gray-300 dark:border-gray-600 rounded-full"
                ></div>
              </div>
              <span
                :class="[
                  step.completed ? 'text-green-700 dark:text-green-300' :
                  step.active ? 'text-blue-700 dark:text-blue-300' :
                  'text-gray-500 dark:text-gray-400'
                ]"
              >
                {{ step.label }}
              </span>
            </div>
          </div>

          <!-- Provider Info -->
          <div v-if="provider" class="mt-3 flex items-center space-x-2 text-xs text-blue-600 dark:text-blue-300">
            <Globe class="w-3 h-3" />
            <span>Using {{ provider }} provider</span>
            <span v-if="maxResults" class="text-gray-500">• Max {{ maxResults }} results</span>
          </div>

          <!-- Estimated Time -->
          <div class="mt-2 flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
            <Clock class="w-3 h-3" />
            <span>Estimated time: {{ estimatedTime }}</span>
          </div>
        </div>

        <!-- Cancel Button -->
        <div class="flex-shrink-0">
          <Button
            variant="ghost"
            size="sm"
            @click="$emit('cancel')"
            class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <X class="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>

    <!-- Additional Loading Indicators -->
    <div v-if="showDetailedProgress" class="detailed-progress mt-4">
      <div class="bg-muted/30 border rounded-lg p-3">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs font-medium text-muted-foreground">Search Progress</span>
          <span class="text-xs text-muted-foreground">{{ progressPercentage }}%</span>
        </div>

        <!-- Progress Bar -->
        <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
          <div
            class="bg-blue-600 h-1.5 rounded-full transition-all duration-500 ease-out"
            :style="{ width: `${progressPercentage}%` }"
          ></div>
        </div>

        <!-- Current Action -->
        <div class="mt-2 text-xs text-muted-foreground">
          {{ currentAction }}
        </div>
      </div>
    </div>

    <!-- Tips While Waiting -->
    <div v-if="showTips && tips.length > 0" class="loading-tips mt-4">
      <div class="bg-yellow-50 dark:bg-yellow-950/30 border border-yellow-200 dark:border-yellow-800 rounded-lg p-3">
        <div class="flex items-center space-x-2 mb-2">
          <Lightbulb class="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
          <span class="text-sm font-medium text-yellow-800 dark:text-yellow-200">Tip</span>
        </div>
        <p class="text-sm text-yellow-700 dark:text-yellow-300">
          {{ currentTip }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
	CheckCircle,
	Clock,
	Globe,
	Lightbulb,
	Search,
	X,
} from "lucide-vue-next";
import { computed, onMounted, onUnmounted, ref } from "vue";

// Props
interface Props {
	query: string;
	searchType?: string;
	provider?: string;
	maxResults?: number;
	showDetailedProgress?: boolean;
	showTips?: boolean;
	estimatedDuration?: number; // in seconds
}

const props = withDefaults(defineProps<Props>(), {
	searchType: "general",
	showDetailedProgress: false,
	showTips: true,
	estimatedDuration: 5,
});

// Emits
defineEmits<{
	cancel: [];
}>();

// State
const currentStepIndex = ref(0);
const startTime = ref(Date.now());
const currentTipIndex = ref(0);

// Computed
const loadingTitle = computed(() => {
	const titles = {
		general: "Searching the Web",
		academic: "Searching Academic Sources",
		code: "Finding Code Examples",
		news: "Searching Latest News",
		research: "Conducting Research",
	};
	return titles[props.searchType as keyof typeof titles] || "Searching";
});

const progressSteps = computed(() => [
	{
		label: "Initializing search",
		completed: currentStepIndex.value > 0,
		active: currentStepIndex.value === 0,
	},
	{
		label: "Querying search provider",
		completed: currentStepIndex.value > 1,
		active: currentStepIndex.value === 1,
	},
	{
		label: "Processing results",
		completed: currentStepIndex.value > 2,
		active: currentStepIndex.value === 2,
	},
	{
		label: "Formatting response",
		completed: currentStepIndex.value > 3,
		active: currentStepIndex.value === 3,
	},
]);

const progressPercentage = computed(() => {
	const elapsed = (Date.now() - startTime.value) / 1000;
	const progress = Math.min((elapsed / props.estimatedDuration) * 100, 95);
	return Math.round(progress);
});

const currentAction = computed(() => {
	const actions = [
		"Preparing search request...",
		"Connecting to search provider...",
		"Retrieving search results...",
		"Processing and ranking results...",
		"Finalizing response...",
	];
	return actions[currentStepIndex.value] || actions[0];
});

const estimatedTime = computed(() => {
	const remaining = Math.max(
		props.estimatedDuration - (Date.now() - startTime.value) / 1000,
		0,
	);
	return remaining > 1 ? `${Math.ceil(remaining)}s` : "Almost done...";
});

const tips = computed(() => [
	"Try using specific keywords for better results",
	"Academic searches work best with formal terminology",
	"Code searches can include programming language names",
	"Use quotes for exact phrase matching",
	"Recent news searches show the latest information",
]);

const currentTip = computed(() => {
	return tips.value[currentTipIndex.value] || tips.value[0];
});

// Methods
let stepInterval: NodeJS.Timeout | null = null;
let tipInterval: NodeJS.Timeout | null = null;

const simulateProgress = () => {
	stepInterval = setInterval(
		() => {
			if (currentStepIndex.value < progressSteps.value.length - 1) {
				currentStepIndex.value++;
			}
		},
		(props.estimatedDuration * 1000) / 4,
	);
};

const rotateTips = () => {
	if (props.showTips && tips.value.length > 1) {
		tipInterval = setInterval(() => {
			currentTipIndex.value = (currentTipIndex.value + 1) % tips.value.length;
		}, 3000);
	}
};

// Lifecycle
onMounted(() => {
	simulateProgress();
	rotateTips();
});

onUnmounted(() => {
	if (stepInterval) clearInterval(stepInterval);
	if (tipInterval) clearInterval(tipInterval);
});
</script>

<style scoped>
.search-loading-state {
  @apply w-full;
}

.loading-container {
  @apply animate-in fade-in-50 duration-300;
}

.detailed-progress {
  @apply animate-in slide-in-from-top-2 duration-300;
}

.loading-tips {
  @apply animate-in fade-in-50 duration-500;
}

/* Custom animations */
@keyframes pulse-slow {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse-slow {
  animation: pulse-slow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
