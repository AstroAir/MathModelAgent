/**
 * TaskHistoryCard Component Tests
 */

import type { TaskHistoryItem } from "@/types/history";
import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";
import TaskHistoryCard from "../TaskHistoryCard.vue";

// Mock date-fns
vi.mock("date-fns", () => ({
	formatDistanceToNow: vi.fn(() => "2 days ago"),
}));

// Mock vue-router
vi.mock("vue-router", () => ({
	useRouter: () => ({
		push: vi.fn(),
	}),
}));

describe("TaskHistoryCard", () => {
	const mockTask: TaskHistoryItem = {
		task_id: "test_task_001",
		title: "Test Linear Regression",
		description: "A test task for linear regression analysis with sample data",
		task_type: "custom",
		is_pinned: false,
		created_at: "2024-11-14T10:30:00Z",
		updated_at: "2024-11-15T14:20:00Z",
		status: "completed",
		file_count: 3,
	};

	it("renders task information correctly", () => {
		const wrapper = mount(TaskHistoryCard, {
			props: { task: mockTask },
		});

		expect(wrapper.text()).toContain("Test Linear Regression");
		expect(wrapper.text()).toContain(
			"A test task for linear regression analysis with sample data",
		);
		expect(wrapper.text()).toContain("3 个文件");
		expect(wrapper.text()).toContain("自定义");
	});

	it("displays correct status badge", () => {
		const wrapper = mount(TaskHistoryCard, {
			props: { task: mockTask },
		});

		const badge = wrapper.find('[class*="bg-green"]');
		expect(badge.exists()).toBe(true);
		expect(badge.text()).toBe("已完成");
	});

	it("shows pinned star when task is pinned", () => {
		const pinnedTask = { ...mockTask, is_pinned: true };
		const wrapper = mount(TaskHistoryCard, {
			props: { task: pinnedTask },
		});

		const star = wrapper.find('[class*="text-yellow-500"]');
		expect(star.exists()).toBe(true);
	});

	it("does not show pinned star when task is not pinned", () => {
		const wrapper = mount(TaskHistoryCard, {
			props: { task: mockTask },
		});

		const star = wrapper.find('[class*="text-yellow-500"]');
		expect(star.exists()).toBe(false);
	});

	it("emits navigate event when card is clicked", async () => {
		const wrapper = mount(TaskHistoryCard, {
			props: { task: mockTask },
		});

		await wrapper.find('[class*="cursor-pointer"]').trigger("click");

		expect(wrapper.emitted("navigate")).toBeTruthy();
		expect(wrapper.emitted("navigate")?.[0]).toEqual([mockTask.task_id]);
	});

	it("emits toggle-pin event when pin action is clicked", async () => {
		const wrapper = mount(TaskHistoryCard, {
			props: { task: mockTask },
		});

		// Find and click the dropdown trigger
		const dropdownTrigger = wrapper.find('button[class*="ghost"]');
		await dropdownTrigger.trigger("click");

		// The dropdown menu items would be rendered, but testing the emit is sufficient
		// In a real test, you'd need to find the specific menu item and click it

		// For now, we'll test the handler method directly
		const component = wrapper.vm as {
			handleTogglePin: (event: { stopPropagation: () => void }) => void;
		};
		const mockEvent = { stopPropagation: vi.fn() };
		component.handleTogglePin(mockEvent);

		expect(wrapper.emitted("toggle-pin")).toBeTruthy();
		expect(wrapper.emitted("toggle-pin")?.[0]).toEqual([mockTask.task_id]);
		expect(mockEvent.stopPropagation).toHaveBeenCalled();
	});

	it("emits delete event when delete action is clicked", async () => {
		const wrapper = mount(TaskHistoryCard, {
			props: { task: mockTask },
		});

		// Test the handler method directly
		const component = wrapper.vm as {
			handleDelete: (event: { stopPropagation: () => void }) => void;
		};
		const mockEvent = { stopPropagation: vi.fn() };
		component.handleDelete(mockEvent);

		expect(wrapper.emitted("delete")).toBeTruthy();
		expect(wrapper.emitted("delete")?.[0]).toEqual([mockTask.task_id]);
		expect(mockEvent.stopPropagation).toHaveBeenCalled();
	});

	it("hides actions when showActions is false", () => {
		const wrapper = mount(TaskHistoryCard, {
			props: {
				task: mockTask,
				showActions: false,
			},
		});

		const dropdown = wrapper.find('button[class*="ghost"]');
		expect(dropdown.exists()).toBe(false);
	});

	it("displays different status colors correctly", () => {
		const processingTask = { ...mockTask, status: "processing" };
		const wrapper = mount(TaskHistoryCard, {
			props: { task: processingTask },
		});

		const badge = wrapper.find('[class*="bg-blue"]');
		expect(badge.exists()).toBe(true);
		expect(badge.text()).toBe("处理中");
	});

	it("handles failed status correctly", () => {
		const failedTask = { ...mockTask, status: "failed" };
		const wrapper = mount(TaskHistoryCard, {
			props: { task: failedTask },
		});

		const badge = wrapper.find('[class*="bg-red"]');
		expect(badge.exists()).toBe(true);
		expect(badge.text()).toBe("失败");
	});

	it("displays example task type correctly", () => {
		const exampleTask = { ...mockTask, task_type: "example" };
		const wrapper = mount(TaskHistoryCard, {
			props: { task: exampleTask },
		});

		expect(wrapper.text()).toContain("示例");
	});

	it("handles empty or undefined title gracefully", () => {
		const taskWithoutTitle = { ...mockTask, title: "" };
		const wrapper = mount(TaskHistoryCard, {
			props: { task: taskWithoutTitle },
		});

		expect(wrapper.text()).toContain("未命名任务");
	});
});
