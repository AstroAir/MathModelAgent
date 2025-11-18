/**
 * Theme optimization utilities for performance and visual improvements
 */

/**
 * Debounce function to prevent excessive theme updates
 */
export function debounce<T extends (...args: never[]) => void>(
	func: T,
	wait: number,
): (...args: Parameters<T>) => void {
	let timeout: NodeJS.Timeout | null = null;

	return (...args: Parameters<T>) => {
		if (timeout) {
			clearTimeout(timeout);
		}

		timeout = setTimeout(() => {
			func(...args);
		}, wait);
	};
}

/**
 * Optimize DOM elements for theme transitions
 */
export function optimizeElementsForTheme(
	elements?: NodeListOf<Element> | Element[],
) {
	const elementsToOptimize = elements || document.querySelectorAll("*");

	for (const element of Array.from(elementsToOptimize)) {
		if (element instanceof HTMLElement) {
			element.classList.add("theme-optimized");
		}
	}
}

/**
 * Remove theme optimization classes after transition
 */
export function cleanupThemeOptimization(delay = 300) {
	setTimeout(() => {
		const optimizedElements = document.querySelectorAll(".theme-optimized");
		for (const element of Array.from(optimizedElements)) {
			element.classList.remove("theme-optimized");
		}
	}, delay);
}

/**
 * Preload theme assets to prevent loading delays
 */
export function preloadThemeAssets() {
	// Preload any theme-specific images or assets
	const themeAssets: string[] = [
		// Add any theme-specific assets here
	];

	for (const asset of themeAssets) {
		const link = document.createElement("link");
		link.rel = "preload";
		link.href = asset;
		link.as = "image";
		document.head.appendChild(link);
	}
}

/**
 * Detect if user prefers reduced motion
 */
export function prefersReducedMotion(): boolean {
	return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

/**
 * Apply theme with performance optimizations
 */
export function applyThemeOptimized(themeApplyFn: () => void) {
	// Optimize elements before theme change
	optimizeElementsForTheme();

	// Apply theme
	themeApplyFn();

	// Cleanup optimization classes
	cleanupThemeOptimization();
}

/**
 * Monitor theme performance
 */
export class ThemePerformanceMonitor {
	private startTime = 0;

	start() {
		this.startTime = performance.now();
	}

	end(operation: string) {
		const endTime = performance.now();
		const duration = endTime - this.startTime;

		if (duration > 16) {
			// More than one frame at 60fps
			console.warn(`Theme ${operation} took ${duration.toFixed(2)}ms (> 16ms)`);
		}

		return duration;
	}
}

/**
 * Batch DOM updates for better performance
 */
export function batchDOMUpdates(updates: (() => void)[]) {
	// Use requestAnimationFrame for smooth updates
	requestAnimationFrame(() => {
		for (const update of updates) {
			update();
		}
	});
}

/**
 * Create a theme-aware media query listener
 */
export function createThemeMediaQueryListener(
	callback: (isDark: boolean) => void,
) {
	const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

	const handler = (e: MediaQueryListEvent) => {
		callback(e.matches);
	};

	mediaQuery.addEventListener("change", handler);

	// Return cleanup function
	return () => {
		mediaQuery.removeEventListener("change", handler);
	};
}

/**
 * Ensure theme accessibility standards
 */
export function validateThemeAccessibility(theme: "light" | "dark") {
	const root = document.documentElement;
	const computedStyle = getComputedStyle(root);

	// Get color values
	const background = computedStyle.getPropertyValue("--background");
	const foreground = computedStyle.getPropertyValue("--foreground");

	// Basic contrast validation (simplified)
	// In a real implementation, you'd use a proper contrast ratio calculation
	console.log(
		`Theme: ${theme}, Background: ${background}, Foreground: ${foreground}`,
	);

	// You could implement actual contrast ratio checking here
	// and warn if accessibility standards aren't met
}

/**
 * Handle theme switching with error recovery
 */
export function safeThemeSwitch(
	themeApplyFn: () => void,
	fallbackFn?: () => void,
) {
	try {
		applyThemeOptimized(themeApplyFn);
	} catch (error) {
		console.error("Theme switching failed:", error);

		if (fallbackFn) {
			try {
				fallbackFn();
			} catch (fallbackError) {
				console.error("Theme fallback failed:", fallbackError);
				// Reset to system default
				document.documentElement.classList.remove("light", "dark");
			}
		}
	}
}
