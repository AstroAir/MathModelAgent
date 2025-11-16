<template>
  <div class="theme-toggle-container">
    <!-- Simple Toggle Button -->
    <button
      v-if="variant === 'button'"
      @click="toggleTheme"
      class="theme-toggle-button"
      :class="themeButtonClasses"
      :aria-label="toggleAriaLabel"
      type="button"
    >
      <transition name="icon-fade" mode="out-in">
        <component :is="currentIcon" :size="iconSize" />
      </transition>
    </button>

    <!-- Switch Toggle -->
    <div v-else-if="variant === 'switch'" class="theme-toggle-switch-container">
      <label class="theme-toggle-switch" :aria-label="toggleAriaLabel">
        <input
          type="checkbox"
          :checked="isDark"
          @change="toggleTheme"
          class="sr-only"
        />
        <div class="switch-track" :class="switchTrackClasses">
          <div class="switch-thumb" :class="switchThumbClasses">
            <component :is="currentIcon" :size="12" />
          </div>
        </div>
      </label>
      <span v-if="showLabel" class="switch-label">
        {{ isDark ? 'Dark' : 'Light' }}
      </span>
    </div>

    <!-- Dropdown Menu -->
    <div v-else-if="variant === 'dropdown'" class="theme-toggle-dropdown">
      <button
        @click="toggleDropdown"
        class="dropdown-trigger"
        :class="dropdownTriggerClasses"
        :aria-label="'Current theme: ' + themeMode"
        :aria-expanded="isDropdownOpen"
        type="button"
      >
        <component :is="currentIcon" :size="iconSize" />
        <ChevronDown :size="14" class="ml-1 transition-transform" :class="{ 'rotate-180': isDropdownOpen }" />
      </button>

      <transition name="dropdown-fade">
        <div v-if="isDropdownOpen" class="dropdown-menu" :class="dropdownMenuClasses">
          <button
            v-for="option in themeOptions"
            :key="option.value"
            @click="selectTheme(option.value)"
            class="dropdown-item"
            :class="[dropdownItemClasses, { 'active': themeMode === option.value }]"
            type="button"
          >
            <component :is="option.icon" :size="16" />
            <span>{{ option.label }}</span>
            <Check v-if="themeMode === option.value" :size="14" class="ml-auto" />
          </button>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useTheme } from "@/composables/useTheme";
import type { ThemeMode } from "@/stores/theme";
import { Check, ChevronDown, Monitor, Moon, Sun } from "lucide-vue-next";
import { computed, onMounted, onUnmounted, ref } from "vue";

interface Props {
	variant?: "button" | "switch" | "dropdown";
	size?: "sm" | "md" | "lg";
	showLabel?: boolean;
	iconSize?: number;
}

const props = withDefaults(defineProps<Props>(), {
	variant: "button",
	size: "md",
	showLabel: false,
	iconSize: 20,
});

const { isDark, themeMode, toggleTheme, setTheme } = useTheme();

// Dropdown state
const isDropdownOpen = ref(false);

// Theme options for dropdown
const themeOptions = [
	{ value: "light" as ThemeMode, label: "Light", icon: Sun },
	{ value: "dark" as ThemeMode, label: "Dark", icon: Moon },
	{ value: "system" as ThemeMode, label: "System", icon: Monitor },
];

// Computed properties
const currentIcon = computed(() => {
	if (themeMode.value === "system") return Monitor;
	return isDark.value ? Moon : Sun;
});

const toggleAriaLabel = computed(() => {
	return `Switch to ${isDark.value ? "light" : "dark"} theme`;
});

// Size classes
const sizeClasses = computed(() => {
	const sizes = {
		sm: "h-8 w-8 text-sm",
		md: "h-10 w-10 text-base",
		lg: "h-12 w-12 text-lg",
	};
	return sizes[props.size];
});

// Button variant classes
const themeButtonClasses = computed(() => [
	sizeClasses.value,
	"inline-flex items-center justify-center rounded-lg border border-input bg-background",
	"hover:bg-accent hover:text-accent-foreground",
	"focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
	"transition-all duration-200 ease-in-out",
	"disabled:pointer-events-none disabled:opacity-50",
]);

// Switch variant classes
const switchTrackClasses = computed(() => [
	"relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
	"focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2",
	isDark.value ? "bg-primary" : "bg-input",
]);

const switchThumbClasses = computed(() => [
	"inline-flex h-5 w-5 items-center justify-center rounded-full bg-background shadow-lg",
	"transition-transform duration-200 ease-in-out",
	isDark.value ? "translate-x-5" : "translate-x-0",
]);

// Dropdown variant classes
const dropdownTriggerClasses = computed(() => [
	sizeClasses.value,
	"inline-flex items-center justify-center rounded-lg border border-input bg-background px-3",
	"hover:bg-accent hover:text-accent-foreground",
	"focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
	"transition-all duration-200 ease-in-out",
]);

const dropdownMenuClasses = computed(() => [
	"absolute top-full right-0 mt-2 w-48 rounded-md border bg-popover p-1 shadow-md z-50",
]);

const dropdownItemClasses = computed(() => [
	"flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-sm",
	"hover:bg-accent hover:text-accent-foreground",
	"focus-visible:outline-none focus-visible:bg-accent focus-visible:text-accent-foreground",
	"transition-colors duration-150",
]);

// Methods
const toggleDropdown = () => {
	isDropdownOpen.value = !isDropdownOpen.value;
};

const selectTheme = (mode: ThemeMode) => {
	setTheme(mode);
	isDropdownOpen.value = false;
};

// Close dropdown when clicking outside
const handleClickOutside = (event: Event) => {
	if (
		isDropdownOpen.value &&
		!event.target?.closest?.(".theme-toggle-dropdown")
	) {
		isDropdownOpen.value = false;
	}
};

onMounted(() => {
	document.addEventListener("click", handleClickOutside);
});

onUnmounted(() => {
	document.removeEventListener("click", handleClickOutside);
});
</script>

<style scoped>
.theme-toggle-container {
  @apply relative;
}

.theme-toggle-switch-container {
  @apply flex items-center gap-2;
}

.switch-label {
  @apply text-sm font-medium text-foreground;
}

.dropdown-menu {
  animation: dropdown-enter 0.15s ease-out;
}

@keyframes dropdown-enter {
  from {
    opacity: 0;
    transform: translateY(-4px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Transitions */
.icon-fade-enter-active,
.icon-fade-leave-active {
  transition: all 0.2s ease-in-out;
}

.icon-fade-enter-from {
  opacity: 0;
  transform: rotate(90deg) scale(0.8);
}

.icon-fade-leave-to {
  opacity: 0;
  transform: rotate(-90deg) scale(0.8);
}

.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: all 0.15s ease-out;
}

.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px) scale(0.95);
}

/* Active state for dropdown items */
.dropdown-item.active {
  @apply bg-accent text-accent-foreground;
}
</style>
