export type LogLevel = "DEBUG" | "INFO" | "WARN" | "ERROR" | "FATAL";

export interface LogEntry {
	id: string;
	timestamp: number;
	level: LogLevel;
	source: string; // module or component name
	message: string;
	details?: unknown; // For stack traces or other rich data
}
