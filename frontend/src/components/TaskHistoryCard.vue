<script setup lang="ts">
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuSeparator,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { TaskHistoryItem } from "@/types/history";
import { formatDistanceToNow } from "date-fns";
import { zhCN } from "date-fns/locale";
import {
	Calendar,
	ExternalLink,
	FileText,
	MoreVertical,
	Star,
	StarOff,
	Trash2,
} from "lucide-vue-next";

interface Props {
	task: TaskHistoryItem;
	showActions?: boolean;
}

interface Emits {
	(e: "toggle-pin", taskId: string): void;
	(e: "delete", taskId: string): void;
	(e: "navigate", taskId: string): void;
}

const props = withDefaults(defineProps<Props>(), {
	showActions: true,
});

const emit = defineEmits<Emits>();

const getStatusColor = (status: string) => {
	switch (status) {
		case "completed":
			return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300";
		case "processing":
			return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300";
		case "failed":
			return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300";
		default:
			return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300";
	}
};

const getStatusText = (status: string) => {
	switch (status) {
		case "completed":
			return "已完成";
		case "processing":
			return "处理中";
		case "failed":
			return "失败";
		default:
			return "未知";
	}
};

const formatDate = (dateString: string) => {
	try {
		return formatDistanceToNow(new Date(dateString), {
			addSuffix: true,
			locale: zhCN,
		});
	} catch {
		return dateString;
	}
};

const handleNavigate = () => {
	emit("navigate", props.task.task_id);
};

const handleTogglePin = (event: Event) => {
	event.stopPropagation();
	emit("toggle-pin", props.task.task_id);
};

const handleDelete = (event: Event) => {
	event.stopPropagation();
	emit("delete", props.task.task_id);
};
</script>

<template>
  <Card
    class="hover:shadow-md transition-shadow cursor-pointer"
    @click="handleNavigate"
  >
    <CardHeader class="pb-3">
      <div class="flex items-start justify-between">
        <div class="flex-1 min-w-0">
          <CardTitle class="text-lg mb-1 truncate">
            {{ task.title || '未命名任务' }}
          </CardTitle>
          <CardDescription class="line-clamp-2">
            {{ task.description }}
          </CardDescription>
        </div>

        <div class="flex items-center gap-2 ml-4">
          <Badge :class="getStatusColor(task.status)">
            {{ getStatusText(task.status) }}
          </Badge>

          <DropdownMenu v-if="showActions">
            <DropdownMenuTrigger as-child @click.stop>
              <Button variant="ghost" size="sm">
                <MoreVertical class="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem @click.stop="handleNavigate">
                <ExternalLink class="mr-2 h-4 w-4" />
                查看详情
              </DropdownMenuItem>
              <DropdownMenuItem @click.stop="handleTogglePin">
                <component
                  :is="task.is_pinned ? StarOff : Star"
                  class="mr-2 h-4 w-4"
                />
                {{ task.is_pinned ? '取消收藏' : '收藏' }}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                @click.stop="handleDelete"
                class="text-destructive"
              >
                <Trash2 class="mr-2 h-4 w-4" />
                删除
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </CardHeader>

    <CardContent class="pt-0">
      <div class="flex items-center justify-between text-sm text-muted-foreground">
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-1">
            <Calendar class="h-3 w-3" />
            {{ formatDate(task.updated_at) }}
          </div>
          <div class="flex items-center gap-1">
            <FileText class="h-3 w-3" />
            {{ task.file_count }} 个文件
          </div>
          <Badge variant="outline" class="text-xs">
            {{ task.task_type === 'custom' ? '自定义' : '示例' }}
          </Badge>
        </div>

        <div class="flex items-center gap-1">
          <Star
            v-if="task.is_pinned"
            class="h-4 w-4 text-yellow-500 fill-current"
          />
        </div>
      </div>
    </CardContent>
  </Card>
</template>
