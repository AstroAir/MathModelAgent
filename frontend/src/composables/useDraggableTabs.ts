import Sortable from "sortablejs";
import { type Ref, onBeforeUnmount, onMounted, ref } from "vue";

export interface TabItem {
	value: string;
	label: string;
	icon?: any;
	disabled?: boolean;
}

export function useDraggableTabs(
	containerRef: Ref<HTMLElement | null>,
	tabs: Ref<TabItem[]>,
	onReorder?: (newOrder: TabItem[]) => void,
) {
	const sortableInstance = ref<Sortable | null>(null);
	const isDragging = ref(false);

	const initSortable = () => {
		if (!containerRef.value) return;

		sortableInstance.value = Sortable.create(containerRef.value, {
			animation: 200,
			draggable: '[data-draggable="true"]',
			handle: '[data-drag-handle="true"]',
			ghostClass: "sortable-ghost",
			chosenClass: "sortable-chosen",
			dragClass: "sortable-drag",
			forceFallback: true,
			fallbackTolerance: 3,

			onStart: () => {
				isDragging.value = true;
			},

			onEnd: (evt) => {
				isDragging.value = false;

				if (evt.oldIndex !== undefined && evt.newIndex !== undefined) {
					const newTabs = [...tabs.value];
					const [movedTab] = newTabs.splice(evt.oldIndex, 1);
					newTabs.splice(evt.newIndex, 0, movedTab);

					tabs.value = newTabs;
					onReorder?.(newTabs);
				}
			},
		});
	};

	const destroySortable = () => {
		if (sortableInstance.value) {
			sortableInstance.value.destroy();
			sortableInstance.value = null;
		}
	};

	onMounted(() => {
		// Small delay to ensure DOM is ready
		setTimeout(initSortable, 100);
	});

	onBeforeUnmount(() => {
		destroySortable();
	});

	return {
		isDragging,
		initSortable,
		destroySortable,
	};
}
