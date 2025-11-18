/**
 * History API Integration Tests
 */

import type {
	CreateTaskHistoryRequest,
	TaskHistoryItem,
} from "@/types/history";
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
	createTaskHistory,
	deleteTaskHistory,
	getTaskCount,
	getTaskHistory,
	getTaskHistoryList,
	toggleTaskPin,
	updateTaskHistory,
} from "../historyApi";

// Mock the request utility
vi.mock("@/utils/request", () => ({
	request: {
		get: vi.fn(),
		post: vi.fn(),
		patch: vi.fn(),
		delete: vi.fn(),
	},
}));

import { request } from "@/utils/request";

describe("History API", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	describe("getTaskHistoryList", () => {
		it("calls the correct endpoint without parameters", async () => {
			const mockResponse = { total: 0, tasks: [] };
			vi.mocked(request.get).mockResolvedValue(mockResponse);

			const result = await getTaskHistoryList();

			expect(request.get).toHaveBeenCalledWith("/history/tasks");
			expect(result).toEqual(mockResponse);
		});

		it("calls the correct endpoint with parameters", async () => {
			const mockResponse = { total: 1, tasks: [] };
			vi.mocked(request.get).mockResolvedValue(mockResponse);

			await getTaskHistoryList({ task_type: "custom", pinned_only: true });

			expect(request.get).toHaveBeenCalledWith(
				"/history/tasks?task_type=custom&pinned_only=true",
			);
		});
	});

	describe("getTaskHistory", () => {
		it("calls the correct endpoint with task ID", async () => {
			const mockTask: TaskHistoryItem = {
				task_id: "test_id",
				title: "Test Task",
				description: "Test Description",
				task_type: "custom",
				is_pinned: false,
				created_at: "2024-01-01T00:00:00Z",
				updated_at: "2024-01-01T00:00:00Z",
				status: "completed",
				file_count: 1,
			};
			vi.mocked(request.get).mockResolvedValue(mockTask);

			const result = await getTaskHistory("test_id");

			expect(request.get).toHaveBeenCalledWith("/history/tasks/test_id");
			expect(result).toEqual(mockTask);
		});
	});

	describe("createTaskHistory", () => {
		it("calls the correct endpoint with task data", async () => {
			const mockRequest: CreateTaskHistoryRequest = {
				task_id: "new_task",
				title: "New Task",
				description: "New Description",
				task_type: "custom",
				file_count: 2,
			};
			const mockResponse: TaskHistoryItem = {
				...mockRequest,
				is_pinned: false,
				created_at: "2024-01-01T00:00:00Z",
				updated_at: "2024-01-01T00:00:00Z",
				status: "completed",
			};
			vi.mocked(request.post).mockResolvedValue(mockResponse);

			const result = await createTaskHistory(mockRequest);

			expect(request.post).toHaveBeenCalledWith("/history/tasks", mockRequest);
			expect(result).toEqual(mockResponse);
		});
	});

	describe("updateTaskHistory", () => {
		it("calls the correct endpoint with update data", async () => {
			const updateData = { title: "Updated Title", status: "completed" };
			const mockResponse: TaskHistoryItem = {
				task_id: "test_id",
				title: "Updated Title",
				description: "Test Description",
				task_type: "custom",
				is_pinned: false,
				created_at: "2024-01-01T00:00:00Z",
				updated_at: "2024-01-01T00:00:00Z",
				status: "completed",
				file_count: 1,
			};
			vi.mocked(request.patch).mockResolvedValue(mockResponse);

			const result = await updateTaskHistory("test_id", updateData);

			expect(request.patch).toHaveBeenCalledWith(
				"/history/tasks/test_id",
				updateData,
			);
			expect(result).toEqual(mockResponse);
		});
	});

	describe("toggleTaskPin", () => {
		it("calls the correct endpoint for toggling pin", async () => {
			const mockResponse: TaskHistoryItem = {
				task_id: "test_id",
				title: "Test Task",
				description: "Test Description",
				task_type: "custom",
				is_pinned: true,
				created_at: "2024-01-01T00:00:00Z",
				updated_at: "2024-01-01T00:00:00Z",
				status: "completed",
				file_count: 1,
			};
			vi.mocked(request.post).mockResolvedValue(mockResponse);

			const result = await toggleTaskPin("test_id");

			expect(request.post).toHaveBeenCalledWith(
				"/history/tasks/test_id/toggle-pin",
			);
			expect(result).toEqual(mockResponse);
		});
	});

	describe("deleteTaskHistory", () => {
		it("calls the correct endpoint for deletion", async () => {
			const mockResponse = { success: true, message: "Task deleted" };
			vi.mocked(request.delete).mockResolvedValue(mockResponse);

			const result = await deleteTaskHistory("test_id");

			expect(request.delete).toHaveBeenCalledWith("/history/tasks/test_id");
			expect(result).toEqual(mockResponse);
		});
	});

	describe("getTaskCount", () => {
		it("calls the correct endpoint for task count", async () => {
			const mockResponse = { total: 10, custom: 7, example: 3 };
			vi.mocked(request.get).mockResolvedValue(mockResponse);

			const result = await getTaskCount();

			expect(request.get).toHaveBeenCalledWith("/history/tasks/count");
			expect(result).toEqual(mockResponse);
		});
	});
});
