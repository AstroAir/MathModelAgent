<script setup lang="ts">
import { saveApiConfig } from "@/apis/apiKeyApi";
import {
	type UploadProgressCallback,
	submitModelingTask,
} from "@/apis/submitModelingApi";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
	Select,
	SelectContent,
	SelectGroup,
	SelectItem,
	SelectLabel,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/components/ui/toast";
import { useApiKeyStore } from "@/stores/apiKeys";
import { useTaskStore } from "@/stores/task";
import { FileArchive, FileUp, FolderUp } from "lucide-vue-next";
import { Rocket } from "lucide-vue-next";
import { ref } from "vue";
import { useRouter } from "vue-router";
import type FileConfirmDialog from "./FileConfirmDialog.vue";

const taskStore = useTaskStore();
const { toast } = useToast();
const apiKeyStore = useApiKeyStore();
const currentStep = ref(1);
const fileConfirmDialog = ref<InstanceType<typeof FileConfirmDialog> | null>(
	null,
);
const fileUploaded = ref(true);

// 表单数据
const uploadedFiles = ref<File[]>([]);
const question = ref("");
const selectedOptions = ref({
	template: "国赛",
	language: "自动检测",
	format: "Markdown",
});

const selectConfig = [
	{
		key: "模板",
		label: "选择模板",
		options: ["国赛", "美赛"],
	},
	{
		key: "语言",
		label: "选择语言",
		options: ["自动检测", "中文", "英文"],
	},
	{
		key: "格式",
		label: "选择格式",
		options: ["Markdown", "LaTeX"],
	},
];

// 添加状态控制
const showUploadSuccess = ref(false);

// 提交任务
const showSubmitSuccess = ref(false);

const taskId = ref<string | null>(null);

// 上传进度状态
const uploadProgress = ref(0);
const isUploading = ref(false);

// 添加 fileInput 的类型声明
const fileInput = ref<HTMLInputElement | null>(null);
const folderInput = ref<HTMLInputElement | null>(null);

const nextStep = () => {
	if (currentStep.value < 2) currentStep.value++;
};

const prevStep = () => {
	if (currentStep.value > 1) currentStep.value--;
};

// 修改文件上传处理
const handleFileUpload = (event: Event) => {
	const input = event.target as HTMLInputElement;
	if (input.files && input.files.length > 0) {
		uploadedFiles.value = Array.from(input.files);
		fileUploaded.value = true;
		showUploadSuccess.value = true; // 显示提示
		setTimeout(() => {
			showUploadSuccess.value = false; // 3秒后自动隐藏
		}, 1000);
	}
};

// 处理文件夹上传
const handleFolderUpload = (event: Event) => {
	const input = event.target as HTMLInputElement;
	if (input.files && input.files.length > 0) {
		uploadedFiles.value = Array.from(input.files);
		fileUploaded.value = true;
		showUploadSuccess.value = true;
		setTimeout(() => {
			showUploadSuccess.value = false;
		}, 1000);
	}
};

const router = useRouter();

const handleSubmit = async () => {
	try {
		if (apiKeyStore.isEmpty) {
			toast({
				title: "请先配置 API Key",
				description: "在侧边栏 -> 头像 -> API Key 中配置 API Key",
				variant: "destructive",
			});
			return;
		}

		// 保存 API Key
		await saveApiConfig({
			coordinator: apiKeyStore.coordinatorConfig,
			modeler: apiKeyStore.modelerConfig,
			coder: apiKeyStore.coderConfig,
			writer: apiKeyStore.writerConfig,
			openalex_email: apiKeyStore.openalexEmail,
		});

		if (uploadedFiles.value.length === 0) {
			if (!fileConfirmDialog.value) return;

			const shouldContinue = await fileConfirmDialog.value.openConfirmDialog();

			if (!shouldContinue) {
				toast({
					title: "请先上传文件",
					description: "请先上传文件",
					variant: "destructive",
				});
				return;
			}
		}
		console.log(selectedOptions.value);
		console.log(question.value);
		console.log(uploadedFiles.value);

		// Map template and language
		const templateMap: Record<string, string> = {
			国赛: "CHINA",
			美赛: "AMERICAN",
		};
		const languageMap: Record<string, string> = {
			自动检测: "auto",
			中文: "zh",
			英文: "en",
		};

		// 重置上传进度
		uploadProgress.value = 0;
		isUploading.value = true;

		const onUploadProgress: UploadProgressCallback = (progress: number) => {
			uploadProgress.value = progress;
		};

		const response = await submitModelingTask(
			{
				ques_all: question.value,
				comp_template: templateMap[selectedOptions.value.template] || "CHINA",
				format_output: selectedOptions.value.format,
				language: languageMap[selectedOptions.value.language] || "zh",
			},
			uploadedFiles.value,
			onUploadProgress,
		);

		isUploading.value = false;

		taskId.value = response?.data?.task_id ?? null;
		taskStore.addUserMessage(question.value);

		showSubmitSuccess.value = true;
		setTimeout(() => {
			showSubmitSuccess.value = false; // 3秒后自动隐藏
		}, 3000);
		router.push(`/task/${taskId.value}`);
		toast({
			title: "任务提交成功",
			description: `任务提交成功，编号为：${taskId.value}`,
		});
	} catch (error) {
		isUploading.value = false;
		uploadProgress.value = 0;
		console.error("任务提交失败:", error);
		toast({
			title: "任务提交失败",
			description: "请检查 API Key 是否正确",
			variant: "destructive",
		});
	}
};
</script>

<template>
  <div class="w-full max-w-2xl mx-auto relative">
    <!-- 进度指示器 -->
    <div class="mb-8">
      <div class="flex items-center justify-center gap-2 mb-4">
        <div :class="['step-indicator', currentStep >= 1 ? 'active' : '']">
          <span class="step-number">1</span>
          <span class="step-label">上传文件</span>
        </div>
        <div class="step-divider" :class="currentStep >= 2 ? 'active' : ''"></div>
        <div :class="['step-indicator', currentStep >= 2 ? 'active' : '']">
          <span class="step-number">2</span>
          <span class="step-label">输入问题</span>
        </div>
      </div>
    </div>

    <!-- 使用 Alert 组件 -->
    <Transition name="fade">
      <div v-if="showUploadSuccess" class="fixed top-4 right-4 z-50">
        <Alert>
          <Rocket class="h-4 w-4" />
          <AlertTitle>文件上传成功！</AlertTitle>
          <AlertDescription>
            已成功上传 {{ uploadedFiles.length }} 个文件，请继续下一步操作。
          </AlertDescription>
        </Alert>
      </div>
    </Transition>

    <Transition name="fade">
      <div v-if="showSubmitSuccess" class="fixed top-4 right-4 z-50">
        <Alert>
          <Rocket class="h-4 w-4" />
          <AlertTitle>任务提交成功！</AlertTitle>
          <AlertDescription>
            任务提交成功，编号为：{{ taskId }}。
          </AlertDescription>
        </Alert>
      </div>
    </Transition>

    <div class="border-2 border-border rounded-2xl shadow-lg bg-card">
      <!-- Step 1: File Upload -->
      <div v-if="currentStep === 1" class="p-8">
        <div class="mb-4">
          <h3 class="text-xl font-semibold text-foreground flex items-center gap-2">
            <FileUp class="w-5 h-5 text-primary" />
            上传数据文件
          </h3>
          <p class="text-sm text-muted-foreground mt-1">上传您的数据集文件，支持多种格式</p>
        </div>

        <!-- 上传方式选项卡 -->
        <div class="flex gap-2 mb-4">
          <Button
            variant="outline"
            size="sm"
            @click="() => fileInput?.click()"
            class="flex-1 h-12 hover:bg-accent hover:border-primary/50 transition-all"
          >
            <FileUp class="w-4 h-4 mr-2" />
            上传文件
          </Button>
          <Button
            variant="outline"
            size="sm"
            @click="() => folderInput?.click()"
            class="flex-1 h-12 hover:bg-accent hover:border-primary/50 transition-all"
          >
            <FolderUp class="w-4 h-4 mr-2" />
            上传文件夹
          </Button>
        </div>

        <div
          class="border-2 border-dashed border-border rounded-xl p-10 text-center hover:border-primary/50 hover:bg-accent/50 transition-all duration-300">
          <input
            type="file"
            ref="fileInput"
            class="hidden"
            @change="handleFileUpload"
            accept=".txt,.csv,.xlsx,.xls,.json,.xml,.zip,.rar,.7z,.tar,.tar.gz"
            multiple
          >
          <input
            type="file"
            ref="folderInput"
            class="hidden"
            @change="handleFolderUpload"
            webkitdirectory
            multiple
          >
          <div class="mx-auto w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center transition-transform duration-300">
            <FileArchive class="w-8 h-8 text-primary" />
          </div>
          <div class="mt-4">
            <p class="text-lg font-semibold text-foreground">拖拽文件/文件夹到此处</p>
            <p class="text-sm text-muted-foreground mt-2">
              支持 .txt, .csv, .xlsx, .zip, .rar 等格式
            </p>
            <p class="text-xs text-muted-foreground/80 mt-1">
              可以上传单个文件、多个文件、文件夹或压缩包
            </p>
            <div v-if="uploadedFiles.length > 0" class="mt-4 p-4 bg-green-500/10 rounded-lg border border-green-500/20">
              <p class="text-sm font-medium text-green-600 mb-2">已选择 {{ uploadedFiles.length }} 个文件</p>
              <ul class="text-xs text-green-600/80 space-y-1">
                <li v-for="(file, index) in uploadedFiles" :key="index" class="flex items-center gap-2">
                  <span class="w-1.5 h-1.5 bg-green-500 rounded-full"></span>
                  <span class="truncate">{{ file.name }}</span>
                  <span class="text-muted-foreground ml-auto">({{ (file.size / 1024).toFixed(1) }} KB)</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
        <div class="mt-6 flex justify-end">
          <Button :disabled="!fileUploaded" @click="nextStep" class="px-6 shadow-md hover:shadow-lg transition-all">
            下一步 →
          </Button>
        </div>
      </div>

      <!-- Step 2: Question Input -->
      <div v-if="currentStep === 2" class="p-8">
        <div class="mb-4">
          <h3 class="text-xl font-semibold text-foreground flex items-center gap-2">
            ✏️ 输入问题描述
          </h3>
          <p class="text-sm text-muted-foreground mt-1">请粘贴完整的题目内容，包括背景和所有小问</p>
        </div>

        <div class="space-y-6">
          <div class="space-y-2">
            <label class="text-sm font-medium text-foreground">题目内容</label>
            <Textarea
              v-model="question"
              placeholder="请粘贴 PDF 中的完整题目背景和多个小问..."
              class="min-h-[160px] resize-none border-2 focus:border-primary transition-colors"
            />
          </div>

          <div class="space-y-3">
            <label class="text-sm font-medium text-foreground">配置选项</label>
            <div class="grid grid-cols-3 gap-4">
              <div v-for="item in selectConfig" :key="item.key" class="space-y-2">
                <label class="text-xs text-muted-foreground">{{ item.label }}</label>
                <Select v-model="selectedOptions[item.key.toLowerCase() as keyof typeof selectedOptions]"
                  :defaultValue="item.options[0].toLowerCase()">
                  <SelectTrigger class="h-10 border-2 hover:border-primary/50 transition-colors">
                    <SelectValue :placeholder="item.label" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectGroup>
                      <SelectLabel>{{ item.key }}</SelectLabel>
                      <SelectItem v-for="option in item.options" :key="option" :value="option.toLowerCase()">
                        {{ option }}
                      </SelectItem>
                    </SelectGroup>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
        </div>

        <!-- 上传进度条 -->
        <div v-if="isUploading" class="mt-6 space-y-3">
          <div class="flex items-center justify-between text-sm">
            <span class="font-medium text-foreground">上传进度</span>
            <span class="text-muted-foreground">{{ uploadProgress }}%</span>
          </div>
          <div class="w-full bg-muted rounded-full h-2.5 overflow-hidden">
            <div
              class="bg-gradient-to-r from-blue-500 to-primary h-2.5 rounded-full transition-all duration-300 ease-out"
              :style="{ width: `${uploadProgress}%` }"
            >
            </div>
          </div>
          <p class="text-xs text-muted-foreground text-center">
            正在上传文件，请稍候...
          </p>
        </div>

        <div class="mt-8 flex justify-between items-center">
          <Button variant="outline" @click="prevStep" class="px-6" :disabled="isUploading">
            ← 上一步
          </Button>
          <Button @click="handleSubmit" class="px-8 shadow-md hover:shadow-lg transition-all" :disabled="isUploading">
            <span v-if="isUploading">上传中...</span>
            <span v-else>🚀 开始分析</span>
          </Button>
        </div>
      </div>
    </div>
  </div>
  <FileConfirmDialog ref="fileConfirmDialog" />
</template>

<style scoped>
/* 进度指示器样式 */
.step-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  position: relative;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 16px;
  background: hsl(var(--muted));
  color: hsl(var(--muted-foreground));
  border: 3px solid hsl(var(--muted));
  transition: all 0.3s ease;
}

.step-label {
  font-size: 14px;
  font-weight: 500;
  color: hsl(var(--muted-foreground));
  transition: all 0.3s ease;
}

.step-indicator.active .step-number {
  background: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
  border-color: hsl(var(--primary));
  box-shadow: 0 4px 12px hsla(var(--primary), 0.3);
}

.step-indicator.active .step-label {
  color: hsl(var(--foreground));
  font-weight: 600;
}

.step-divider {
  width: 60px;
  height: 3px;
  background: hsl(var(--muted));
  transition: all 0.3s ease;
  margin: 0 -8px;
  align-self: center;
  margin-top: -24px;
}

.step-divider.active {
  background: hsl(var(--primary));
}

/* 淡入淡出动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
