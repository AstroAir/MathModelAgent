<script setup lang="ts">
import { type TaskLog, getTaskLogs, getTaskStatus } from "@/apis/commonApi";
import {
	getAllFilesDownloadUrl,
	getFileContent,
	getFiles,
} from "@/apis/filesApi";
import type { FileInfo } from "@/apis/filesApi";
import AgentWorkflowStatus from "@/components/AgentWorkflowStatus.vue";
import AppSidebar from "@/components/AppSidebar.vue";
import ServiceStatus from "@/components/ServiceStatus.vue";
import StepTimeline from "@/components/StepTimeline.vue";
import TaskCostCard from "@/components/TaskCostCard.vue";
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
	SidebarInset,
	SidebarProvider,
	SidebarTrigger,
} from "@/components/ui/sidebar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/components/ui/toast";
import FileSheet from "@/pages/task/components/FileSheet.vue";
import { useTaskStore } from "@/stores/task";
import type { Message, StepMessage } from "@/utils/response";
import { formatDistanceToNow } from "date-fns";
import { zhCN } from "date-fns/locale";
import {
	AlertCircle,
	ArrowLeft,
	Calendar,
	CheckCircle2,
	Clock,
	Download,
	FileText,
	Loader2,
	PlayCircle,
	XCircle,
} from "lucide-vue-next";
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();
const taskId = route.params.task_id as string;

const taskStore = useTaskStore();
const { toast } = useToast();

// Files and results state
const taskFiles = ref<FileInfo[]>([]);
const loadingFiles = ref(false);
const selectedFile = ref<FileInfo | null>(null);
const filePreviewContent = ref<string>("");
const loadingPreview = ref(false);

// Logs state
const taskLogs = ref<TaskLog[]>([]);
const loadingLogs = ref(false);
const logsPollingInterval = ref<number | null>(null);

// 定义 AgentStatus 接口
interface AgentStatus {
	name: string;
	status: "pending" | "running" | "completed" | "error";
	icon: string;
	description: string;
}

const taskStatus = ref<"pending" | "running" | "completed" | "failed">(
	"pending",
);
const taskProgress = ref(0);
const taskStartTime = ref<Date | null>(null);
const taskEndTime = ref<Date | null>(null);

// 工作流状态数据（基于实时消息动态计算）
const agentStatuses = computed<AgentStatus[]>(() => {
	const msgs = taskStore.messages;
	const hasCoderProcessing = msgs.some(
		(m: Message) =>
			m.msg_type === "step" &&
			m.agent_type === "CoderAgent" &&
			m.status === "processing",
	);
	const hasCoderCompleted = msgs.some(
		(m: Message) =>
			m.msg_type === "step" &&
			m.agent_type === "CoderAgent" &&
			m.status === "completed",
	);
	const hasWriterProcessing = msgs.some(
		(m: Message) =>
			m.msg_type === "step" &&
			m.agent_type === "WriterAgent" &&
			m.status === "processing",
	);
	const hasWriterCompleted = msgs.some(
		(m: Message) =>
			m.msg_type === "step" &&
			m.agent_type === "WriterAgent" &&
			m.status === "completed",
	);

	const modelerDone =
		hasCoderProcessing ||
		hasCoderCompleted ||
		hasWriterProcessing ||
		hasWriterCompleted;

	const modelerStatus: AgentStatus["status"] = modelerDone
		? "completed"
		: msgs.length > 0
			? "running"
			: "pending";

	const coderStatus: AgentStatus["status"] = hasCoderCompleted
		? "completed"
		: hasCoderProcessing
			? "running"
			: "pending";

	const writerStatus: AgentStatus["status"] = hasWriterCompleted
		? "completed"
		: hasWriterProcessing
			? "running"
			: "pending";

	return [
		{
			name: "建模智能体",
			status: modelerStatus,
			icon: "🧮",
			description: "问题分析和数学建模",
		},
		{
			name: "代码智能体",
			status: coderStatus,
			icon: "💻",
			description: "代码生成和执行",
		},
		{
			name: "写作智能体",
			status: writerStatus,
			icon: "✍️",
			description: "论文生成",
		},
	];
});

// 步骤时间线数据（从实时 Step 消息映射）
const mapStepStatus = (status?: string): StepMessage["status"] => {
	if (status === "processing" || status === "completed" || status === "failed") {
		return status;
	}
	return "processing";
};

const stepMessages = computed<StepMessage[]>(() => {
	return taskStore.messages
		.filter((msg: Message) => msg.msg_type === "step")
		.map((msg: Message) => ({
			id: msg.id,
			step: "",
			status: mapStepStatus(msg.status),
			content: msg.content ?? "",
			timestamp: msg.timestamp,
			step_name: msg.step_name,
			agent_type: msg.agent_type,
			step_type: msg.step_type,
			details: msg.details,
		}));
});

// 获取状态图标
const getStatusIcon = (status: string) => {
	switch (status) {
		case "running":
			return Loader2;
		case "completed":
			return CheckCircle2;
		case "failed":
			return XCircle;
		case "pending":
			return AlertCircle;
		default:
			return PlayCircle;
	}
};

// 获取状态文本
const getStatusText = (status: string) => {
	switch (status) {
		case "running":
			return "运行中";
		case "completed":
			return "已完成";
		case "failed":
			return "失败";
		case "pending":
			return "等待中";
		default:
			return "未知";
	}
};

// 获取状态变体
const getStatusVariant = (
	status: string,
): "default" | "secondary" | "destructive" | "outline" => {
	switch (status) {
		case "running":
			return "default";
		case "completed":
			return "secondary";
		case "failed":
			return "destructive";
		default:
			return "outline";
	}
};

// 计算任务持续时间
const taskDuration = computed(() => {
	if (!taskStartTime.value) return "未开始";
	const endTime = taskEndTime.value || new Date();
	const duration = endTime.getTime() - taskStartTime.value.getTime();
	const seconds = Math.floor(duration / 1000);
	const minutes = Math.floor(seconds / 60);
	const hours = Math.floor(minutes / 60);

	if (hours > 0) {
		return `${hours}小时${minutes % 60}分钟`;
	}
	if (minutes > 0) {
		return `${minutes}分钟${seconds % 60}秒`;
	}
	return `${seconds}秒`;
});

// 格式化时间
const formatTime = (date: Date | null) => {
	if (!date) return "未知";
	return formatDistanceToNow(date, { addSuffix: true, locale: zhCN });
};

// 返回历史记录
const goBack = () => {
	router.push("/history");
};

// 下载所有结果
const handleDownloadResults = () => {
	try {
		const downloadUrl = getAllFilesDownloadUrl(taskId);
		window.open(downloadUrl, "_blank");
		toast({
			title: "开始下载",
			description: "正在打包下载所有文件...",
		});
	} catch (error) {
		console.error("下载失败:", error);
		toast({
			title: "下载失败",
			description: "无法下载文件,请稍后重试",
			variant: "destructive",
		});
	}
};

// 加载任务文件列表
const loadTaskFiles = async () => {
	loadingFiles.value = true;
	try {
		const response = await getFiles(taskId);
		taskFiles.value = response.data || [];
	} catch (error) {
		console.error("加载文件列表失败:", error);
		taskFiles.value = [];
	} finally {
		loadingFiles.value = false;
	}
};

// 预览文件
const previewFile = async (file: FileInfo) => {
	selectedFile.value = file;
	loadingPreview.value = true;
	filePreviewContent.value = "";

	try {
		const response = await getFileContent(taskId, file.name);
		const data = response.data;

		if (data.is_image) {
			filePreviewContent.value = `<img src="data:${data.mime_type};base64,${data.content}" alt="${data.filename}" class="max-w-full h-auto" />`;
		} else {
			filePreviewContent.value = data.content || "文件内容为空";
		}
	} catch (error) {
		console.error("预览文件失败:", error);
		filePreviewContent.value = "无法加载文件预览";
	} finally {
		loadingPreview.value = false;
	}
};

// 加载任务日志
const loadTaskLogs = async () => {
	loadingLogs.value = true;
	try {
		const response = await getTaskLogs(taskId);
		taskLogs.value = response.data?.logs || [];
	} catch (error) {
		console.error("加载日志失败:", error);
		taskLogs.value = [];
	} finally {
		loadingLogs.value = false;
	}
};

// 开始轮询日志（任务运行时）
const startLogsPolling = () => {
	// 立即加载一次
	loadTaskLogs();
	// 每5秒轮询一次
	logsPollingInterval.value = window.setInterval(() => {
		if (taskStatus.value === "running") {
			loadTaskLogs();
		}
	}, 5000);
};

// 停止轮询日志
const stopLogsPolling = () => {
	if (logsPollingInterval.value) {
		clearInterval(logsPollingInterval.value);
		logsPollingInterval.value = null;
	}
};

// 格式化日志级别颜色
const getLogLevelClass = (level: string) => {
	switch (level.toUpperCase()) {
		case "ERROR":
			return "text-red-500";
		case "WARNING":
		case "WARN":
			return "text-yellow-500";
		case "SUCCESS":
			return "text-green-500";
		default:
			return "text-muted-foreground";
	}
};

// 加载任务数据并建立 WebSocket 连接
const statusPollingInterval = ref<number | null>(null);

const checkTaskStatus = async () => {
	try {
		const response = await getTaskStatus(taskId);
		const status = response.data?.status;
		if (status === "completed" || status === "failed") {
			taskStatus.value = status;
			if (statusPollingInterval.value)
				clearInterval(statusPollingInterval.value);
			// Final load of data
			loadTaskFiles();
			loadTaskLogs();
		} else if (status === "running") {
			taskStatus.value = "running";
		}
	} catch (error) {
		console.error("Failed to get task status:", error);
		if (statusPollingInterval.value) clearInterval(statusPollingInterval.value);
	}
};

onMounted(() => {
	taskProgress.value = 0;
	taskStartTime.value = new Date();

	// Check status immediately and then poll
	checkTaskStatus();
	statusPollingInterval.value = window.setInterval(checkTaskStatus, 3000);

	taskStore.connectWebSocket(taskId);
	loadTaskFiles();
	startLogsPolling();

	// Stop polling once WebSocket is connected and has messages
	const unwatch = watch(
		() => taskStore.messages,
		(messages) => {
			if (messages.length > 0 && statusPollingInterval.value) {
				clearInterval(statusPollingInterval.value);
				unwatch(); // Stop watching
			}
		},
		{ deep: true },
	);
});

// 根据实时消息更新任务进度和状态
watch(
	() => taskStore.messages,
	(msgs) => {
		const list = msgs;
		const completedSystem = list.some(
			(m: Message) =>
				m.msg_type === "system" &&
				typeof m.content === "string" &&
				m.content.includes("任务处理完成"),
		);
		if (completedSystem) {
			taskStatus.value = "completed";
			taskProgress.value = 100;
			taskEndTime.value = new Date();
			// 任务完成后重新加载文件列表和日志
			loadTaskFiles();
			loadTaskLogs();
			stopLogsPolling();
			return;
		}

		const stepMsgs = list.filter((m: Message) => m.msg_type === "step");
		if (stepMsgs.length > 0) {
			const completedSteps = stepMsgs.filter(
				(m: Message) => m.status === "completed",
			).length;
			const totalSteps = stepMsgs.length;
			const percent = Math.round((completedSteps / totalSteps) * 100);
			taskProgress.value = Math.min(Math.max(percent, 0), 100);
		}
	},
	{ deep: true },
);

onBeforeUnmount(() => {
	taskStore.closeWebSocket();
	stopLogsPolling();
});
</script>

<template>
  <SidebarProvider>
    <AppSidebar />
    <SidebarInset>
      <header class="flex h-14 sm:h-16 shrink-0 items-center gap-2 px-3 sm:px-4 border-b border-border bg-background/80 backdrop-blur-sm sticky top-0 z-10">
        <SidebarTrigger class="-ml-1" />
        <div class="flex justify-between w-full gap-2 items-center">
          <div class="flex items-center gap-2">
            <Button variant="ghost" size="icon" @click="goBack" class="h-8 w-8">
              <ArrowLeft class="h-4 w-4" />
            </Button>
            <h1 class="text-lg font-semibold">任务详情</h1>
            <Badge :variant="getStatusVariant(taskStatus)" class="ml-2">
              <component :is="getStatusIcon(taskStatus)"
                :class="['h-3 w-3 mr-1', taskStatus === 'running' ? 'animate-spin' : '']" />
              {{ getStatusText(taskStatus) }}
            </Badge>
          </div>
          <div class="flex items-center gap-2">
            <ServiceStatus />
            <FileSheet />
          </div>
        </div>
      </header>

      <main class="flex-1 p-4 overflow-y-auto">
        <div class="max-w-7xl mx-auto space-y-6">
          <!-- 任务概览卡片 -->
          <Card>
            <CardHeader>
              <div class="flex items-start justify-between">
                <div class="space-y-1">
                  <CardTitle>任务概览</CardTitle>
                  <CardDescription>
                    任务 ID: <span class="font-mono text-foreground">{{ taskId }}</span>
                  </CardDescription>
                </div>
                <div class="flex gap-2">
                  <Button variant="outline" size="sm" @click="handleDownloadResults">
                    <Download class="h-4 w-4 mr-2" />
                    下载结果
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="space-y-2">
                  <div class="flex items-center text-sm text-muted-foreground">
                    <Calendar class="h-4 w-4 mr-2" />
                    开始时间
                  </div>
                  <div class="text-sm font-medium">
                    {{ formatTime(taskStartTime) }}
                  </div>
                </div>
                <div class="space-y-2">
                  <div class="flex items-center text-sm text-muted-foreground">
                    <Clock class="h-4 w-4 mr-2" />
                    持续时间
                  </div>
                  <div class="text-sm font-medium">
                    {{ taskDuration }}
                  </div>
                </div>
                <div class="space-y-2">
                  <div class="flex items-center text-sm text-muted-foreground">
                    <FileText class="h-4 w-4 mr-2" />
                    进度
                  </div>
                  <div class="flex items-center gap-2">
                    <div class="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                      <div
                        class="h-full bg-primary transition-all duration-300"
                        :style="{ width: `${taskProgress}%` }"
                      />
                    </div>
                    <span class="text-sm font-medium">{{ taskProgress }}%</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- 成本统计卡片 -->
          <TaskCostCard :task-id="taskId" />

          <!-- 工作流状态 -->
          <Card>
            <CardHeader>
              <CardTitle>工作流状态</CardTitle>
              <CardDescription>查看各个智能体的执行状态</CardDescription>
            </CardHeader>
            <CardContent>
              <AgentWorkflowStatus :agents="agentStatuses" />
            </CardContent>
          </Card>

          <!-- 详细信息标签页 -->
          <Tabs default-value="timeline" class="w-full">
            <TabsList class="grid w-full grid-cols-3">
              <TabsTrigger value="timeline">执行时间线</TabsTrigger>
              <TabsTrigger value="logs">执行日志</TabsTrigger>
              <TabsTrigger value="results">结果预览</TabsTrigger>
            </TabsList>

            <TabsContent value="timeline" class="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>执行时间线</CardTitle>
                  <CardDescription>查看任务执行的详细步骤</CardDescription>
                </CardHeader>
                <CardContent>
                  <StepTimeline :steps="stepMessages" />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="logs" class="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>执行日志</CardTitle>
                  <CardDescription>查看任务执行过程中的详细日志</CardDescription>
                </CardHeader>
                <CardContent>
                  <div class="space-y-2 font-mono text-sm bg-muted p-4 rounded-lg max-h-96 overflow-y-auto">
                    <div v-if="loadingLogs && taskLogs.length === 0" class="text-muted-foreground text-center py-8">
                      <Loader2 class="h-6 w-6 mx-auto animate-spin" />
                      <p class="mt-2">正在加载日志...</p>
                    </div>
                    <div v-else-if="taskLogs.length === 0" class="text-muted-foreground text-center py-8">
                      暂无详细执行日志
                    </div>
                    <div v-else v-for="(log, index) in taskLogs" :key="index" :class="getLogLevelClass(log.level)">
                      <span class="text-muted-foreground/60 mr-2">[{{ new Date(log.timestamp).toLocaleString('zh-CN') }}]</span>
                      <span class="font-semibold mr-1">[{{ log.level }}]</span>
                      <span>{{ log.message }}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="results" class="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>结果预览</CardTitle>
                  <CardDescription>查看任务生成的结果文件</CardDescription>
                </CardHeader>
                <CardContent>
                  <div v-if="loadingFiles" class="text-center py-12">
                    <Loader2 class="h-12 w-12 mx-auto mb-4 animate-spin text-primary" />
                    <p class="text-muted-foreground">加载文件列表中...</p>
                  </div>
                  <div v-else-if="taskFiles.length === 0" class="text-center py-12 text-muted-foreground">
                    <FileText class="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>暂无结果文件</p>
                  </div>
                  <div v-else class="space-y-4">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div class="space-y-2">
                        <h4 class="text-sm font-semibold">文件列表</h4>
                        <div class="space-y-1 max-h-96 overflow-y-auto">
                          <button
                            v-for="file in taskFiles"
                            :key="file.name"
                            @click="previewFile(file)"
                            :class="[
                              'w-full text-left px-3 py-2 rounded-md text-sm transition-colors',
                              selectedFile?.name === file.name ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'
                            ]"
                          >
                            <div class="flex items-center justify-between">
                              <span class="truncate">{{ file.name }}</span>
                              <span class="text-xs opacity-70">{{ file.file_type }}</span>
                            </div>
                          </button>
                        </div>
                      </div>
                      <div class="space-y-2">
                        <h4 class="text-sm font-semibold">文件预览</h4>
                        <div class="border rounded-lg p-4 bg-muted/50 min-h-[300px] max-h-96 overflow-auto">
                          <div v-if="!selectedFile" class="text-center text-muted-foreground py-12">
                            点击左侧文件查看预览
                          </div>
                          <div v-else-if="loadingPreview" class="text-center py-12">
                            <Loader2 class="h-8 w-8 mx-auto animate-spin text-primary" />
                          </div>
                          <div v-else>
                            <div v-if="selectedFile.file_type === 'png' || selectedFile.file_type === 'jpg' || selectedFile.file_type === 'jpeg' || selectedFile.file_type === 'gif'"
                              v-html="filePreviewContent"
                              class="text-center"
                            />
                            <pre v-else class="whitespace-pre-wrap text-xs font-mono">{{ filePreviewContent }}</pre>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </SidebarInset>
  </SidebarProvider>
</template>
