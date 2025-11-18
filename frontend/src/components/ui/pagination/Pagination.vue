<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight, MoreHorizontal } from "lucide-vue-next";
import { computed } from "vue";

interface Props {
	currentPage: number;
	totalPages: number;
	totalItems: number;
	itemsPerPage: number;
	showSizeChanger?: boolean;
	pageSizeOptions?: number[];
}

interface Emits {
	(e: "update:currentPage", page: number): void;
	(e: "update:itemsPerPage", size: number): void;
}

const props = withDefaults(defineProps<Props>(), {
	showSizeChanger: true,
	pageSizeOptions: () => [10, 20, 50, 100],
});

const emit = defineEmits<Emits>();

const startItem = computed(() => {
	return (props.currentPage - 1) * props.itemsPerPage + 1;
});

const endItem = computed(() => {
	return Math.min(props.currentPage * props.itemsPerPage, props.totalItems);
});

const visiblePages = computed(() => {
	const pages: (number | string)[] = [];
	const total = props.totalPages;
	const current = props.currentPage;

	if (total <= 7) {
		// Show all pages if total is small
		for (let i = 1; i <= total; i++) {
			pages.push(i);
		}
	} else {
		// Always show first page
		pages.push(1);

		if (current > 4) {
			pages.push("...");
		}

		// Show pages around current
		const start = Math.max(2, current - 1);
		const end = Math.min(total - 1, current + 1);

		for (let i = start; i <= end; i++) {
			if (i !== 1 && i !== total) {
				pages.push(i);
			}
		}

		if (current < total - 3) {
			pages.push("...");
		}

		// Always show last page
		if (total > 1) {
			pages.push(total);
		}
	}

	return pages;
});

const goToPage = (page: number) => {
	if (page >= 1 && page <= props.totalPages && page !== props.currentPage) {
		emit("update:currentPage", page);
	}
};

const changePageSize = (size: number) => {
	emit("update:itemsPerPage", size);
	// Reset to first page when changing page size
	emit("update:currentPage", 1);
};
</script>

<template>
  <div class="flex items-center justify-between px-2">
    <div class="flex items-center space-x-6 lg:space-x-8">
      <div class="flex items-center space-x-2">
        <p class="text-sm font-medium">每页显示</p>
        <select
          v-if="showSizeChanger"
          :value="itemsPerPage"
          @change="changePageSize(Number(($event.target as HTMLSelectElement).value))"
          class="h-8 w-[70px] rounded-md border border-input bg-background px-3 py-1 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        >
          <option v-for="size in pageSizeOptions" :key="size" :value="size">
            {{ size }}
          </option>
        </select>
        <p class="text-sm font-medium">条</p>
      </div>
      <div class="flex w-[100px] items-center justify-center text-sm font-medium">
        第 {{ startItem }}-{{ endItem }} 条，共 {{ totalItems }} 条
      </div>
    </div>

    <div class="flex items-center space-x-2">
      <Button
        variant="outline"
        size="sm"
        :disabled="currentPage === 1"
        @click="goToPage(currentPage - 1)"
      >
        <ChevronLeft class="h-4 w-4" />
        <span class="sr-only">上一页</span>
      </Button>

      <div class="flex items-center space-x-1">
        <template v-for="page in visiblePages" :key="page">
          <Button
            v-if="typeof page === 'number'"
            :variant="page === currentPage ? 'default' : 'outline'"
            size="sm"
            class="w-8 h-8 p-0"
            @click="goToPage(page)"
          >
            {{ page }}
          </Button>
          <div
            v-else
            class="flex items-center justify-center w-8 h-8"
          >
            <MoreHorizontal class="h-4 w-4" />
          </div>
        </template>
      </div>

      <Button
        variant="outline"
        size="sm"
        :disabled="currentPage === totalPages"
        @click="goToPage(currentPage + 1)"
      >
        <ChevronRight class="h-4 w-4" />
        <span class="sr-only">下一页</span>
      </Button>
    </div>
  </div>
</template>
