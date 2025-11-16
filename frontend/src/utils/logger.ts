import { useLogStore } from "@/stores/log";
import type { LogLevel } from "@/types/log";

// Logger utility class for centralized logging
export class Logger {
	private static instance: Logger;
	private logStore: ReturnType<typeof useLogStore> | null = null;

	private constructor() {}

	static getInstance(): Logger {
		if (!Logger.instance) {
			Logger.instance = new Logger();
		}
		return Logger.instance;
	}

	// Initialize the logger with the log store
	init(logStore: ReturnType<typeof useLogStore>) {
		this.logStore = logStore;
	}

	// Log methods for different levels
	debug(message: string, source = "App", details?: any) {
		this.log("DEBUG", message, source, details);
	}

	info(message: string, source = "App", details?: any) {
		this.log("INFO", message, source, details);
	}

	warn(message: string, source = "App", details?: any) {
		this.log("WARN", message, source, details);
	}

	error(message: string, source = "App", details?: any) {
		this.log("ERROR", message, source, details);
	}

	fatal(message: string, source = "App", details?: any) {
		this.log("FATAL", message, source, details);
	}

	private log(level: LogLevel, message: string, source: string, details?: any) {
		if (!this.logStore) {
			console.warn("Logger not initialized with log store");
			return;
		}

		this.logStore.addLog({
			level,
			message,
			source,
			details,
		});

		// Also log to console for development
		if (import.meta.env.DEV) {
			const consoleMethod =
				level === "DEBUG"
					? "debug"
					: level === "INFO"
						? "info"
						: level === "WARN"
							? "warn"
							: "error";
			console[consoleMethod](`[${source}] ${message}`, details || "");
		}
	}
}

// Export singleton instance
export const logger = Logger.getInstance();

// Vue plugin for easy integration
export function createLoggerPlugin() {
	return {
		install(app: any) {
			const logStore = useLogStore();
			logger.init(logStore);

			// Make logger available globally
			app.config.globalProperties.$logger = logger;
			app.provide("logger", logger);
		},
	};
}

// Composable for using logger in components
export function useLogger() {
	return logger;
}
