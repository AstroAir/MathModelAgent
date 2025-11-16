import { defineStore } from 'pinia';
import type { LogEntry } from '@/types/log';

interface LogState {
  logs: LogEntry[];
  maxLogs: number;
}

export const useLogStore = defineStore('log', {
  state: (): LogState => ({
    logs: [],
    maxLogs: 1000, // Default max logs
  }),
  actions: {
    addLog(log: Omit<LogEntry, 'id' | 'timestamp'>) {
      const newLog: LogEntry = {
        ...log,
        id: self.crypto.randomUUID(),
        timestamp: Date.now(),
      };

      this.logs.push(newLog);

      if (this.logs.length > this.maxLogs) {
        this.logs.shift();
      }
    },
    clearLogs() {
      this.logs = [];
    },
    setMaxLogs(max: number) {
      this.maxLogs = max;
    },
  },
});

