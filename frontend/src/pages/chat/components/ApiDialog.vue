<script setup lang="ts">
import {
	saveApiConfig,
	validateApiKey,
	validateOpenalexEmail,
} from "@/apis/apiKeyApi";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectLabel,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";
import { useApiKeyStore } from "@/stores/apiKeys";
import {
	CheckCircle,
	ChevronDown,
	ChevronUp,
	Copy,
	Settings2,
	Sparkles,
	Wand2,
	XCircle,
} from "lucide-vue-next";
import { computed, onMounted, ref } from "vue";

const apiKeyStore = useApiKeyStore();

// 统一配置模式
const unifiedMode = ref(false);
const unifiedConfig = ref({
	apiKey: "",
	baseUrl: "",
	modelId: "",
	provider: "",
});

// 折叠状态管理
const collapsedAgents = ref<Record<string, boolean>>({
	coordinator: false,
	modeler: false,
	coder: false,
	writer: false,
});

const toggleAgentCollapse = (agentKey: string) => {
	collapsedAgents.value[agentKey] = !collapsedAgents.value[agentKey];
};

const toggleAllAgents = () => {
	const allCollapsed = Object.values(collapsedAgents.value).every((v) => v);
	for (const key of Object.keys(collapsedAgents.value)) {
		collapsedAgents.value[key] = !allCollapsed;
	}
};

// 本地表单数据
const form = ref<{
	coordinator: {
		apiKey: string;
		baseUrl: string;
		modelId: string;
		provider: string;
	};
	modeler: {
		apiKey: string;
		baseUrl: string;
		modelId: string;
		provider: string;
	};
	coder: { apiKey: string; baseUrl: string; modelId: string; provider: string };
	writer: {
		apiKey: string;
		baseUrl: string;
		modelId: string;
		provider: string;
	};
	openalex_email: string;
}>({
	coordinator: {
		apiKey: "",
		baseUrl: "",
		modelId: "",
		provider: "",
	},
	modeler: {
		apiKey: "",
		baseUrl: "",
		modelId: "",
		provider: "",
	},
	coder: {
		apiKey: "",
		baseUrl: "",
		modelId: "",
		provider: "",
	},
	writer: {
		apiKey: "",
		baseUrl: "",
		modelId: "",
		provider: "",
	},
	openalex_email: "",
});

// 验证状态
const validating = ref(false);
const validationResults = ref({
	coordinator: { valid: false, message: "" },
	modeler: { valid: false, message: "" },
	coder: { valid: false, message: "" },
	writer: { valid: false, message: "" },
	openalex_email: { valid: false, message: "" },
});

// 计算所有验证是否都通过
const allValid = computed(() => {
	return Object.values(validationResults.value).every((result) => result.valid);
});

// 模型配置列表
const modelConfigs = computed(() => [
	{ key: "coordinator", label: "协调者模型配置" },
	{ key: "modeler", label: "建模手模型配置" },
	{ key: "coder", label: "代码手模型配置" },
	{ key: "writer", label: "论文手模型配置" },
]);

// 从 store 加载数据到表单
const loadFromStore = () => {
	form.value.coordinator = { ...apiKeyStore.coordinatorConfig };
	form.value.modeler = { ...apiKeyStore.modelerConfig };
	form.value.coder = { ...apiKeyStore.coderConfig };
	form.value.writer = { ...apiKeyStore.writerConfig };
	form.value.openalex_email = apiKeyStore.openalexEmail;
};

// 保存表单数据到 store
const saveToStore = async () => {
	// 先保存到前端 store
	apiKeyStore.setCoordinatorConfig(form.value.coordinator);
	apiKeyStore.setModelerConfig(form.value.modeler);
	apiKeyStore.setCoderConfig(form.value.coder);
	apiKeyStore.setWriterConfig(form.value.writer);
	apiKeyStore.setOpenalexEmail(form.value.openalex_email);
	// 如果验证成功，也保存到后端设置
	if (allValid.value) {
		try {
			await saveApiConfig({
				coordinator: form.value.coordinator,
				modeler: form.value.modeler,
				coder: form.value.coder,
				writer: form.value.writer,
				openalex_email: form.value.openalex_email,
			});
		} catch (error) {
			console.error("保存配置到后端失败:", error);
		}
	}
};

// 组件挂载时加载数据
onMounted(() => {
	loadFromStore();
});

// 定义 emits
const emit = defineEmits<(e: "update:open", value: boolean) => void>();

// 定义 props
const props = defineProps<{ open: boolean }>();

// 更新 open 状态
const updateOpen = (value: boolean) => {
	emit("update:open", value);
};

// 保存并关闭
const saveAndClose = async () => {
	await saveToStore();
	updateOpen(false);
};

// 验证大模型 API Key
const validateModelApiKey = async (config: {
	apiKey: string;
	baseUrl: string;
	modelId: string;
}) => {
	if (!config.apiKey) {
		return { valid: false, message: "API Key 为空" };
	}

	if (!config.modelId) {
		return { valid: false, message: "Model ID 为空" };
	}

	try {
		// 调用后端验证接口
		const result = await validateApiKey({
			api_key: config.apiKey,
			base_url: config.baseUrl || "https://api.openai.com/v1",
			model_id: config.modelId,
		});

		return {
			valid: result.data.valid,
			message: result.data.message,
		};
	} catch (error) {
		return {
			valid: false,
			message: "✗ 验证失败: 无法连接到验证服务",
		};
	}
};

// 一键验证所有 API Keys
const validateAllApiKeys = async () => {
	validating.value = true;

	// 只清空验证结果，保留用户输入的数据
	validationResults.value = {
		coordinator: { valid: false, message: "" },
		modeler: { valid: false, message: "" },
		coder: { valid: false, message: "" },
		writer: { valid: false, message: "" },
		openalex_email: { valid: false, message: "" },
	};

	try {
		// 逐个验证各模型 API Keys，避免并发请求
		for (const config of modelConfigs.value) {
			const key = config.key as keyof typeof validationResults.value;
			const formKey = config.key as keyof typeof form.value;

			// 设置当前验证中状态
			validationResults.value[key] = { valid: false, message: "验证中..." };

			// 验证当前配置
			validationResults.value[key] = await validateModelApiKey(
				form.value[formKey] as {
					apiKey: string;
					baseUrl: string;
					modelId: string;
				},
			);

			// 每次验证后等待 1 秒，避免触发速率限制
			await new Promise((resolve) => setTimeout(resolve, 1000));
		}

		// 验证 OpenAlex Email
		validationResults.value.openalex_email = await validateOpenalexEmail({
			email: form.value.openalex_email,
		}).then((res) => res.data);
	} catch (error) {
		console.error("验证过程中发生错误:", error);
		// 显示全局错误
		for (const key of Object.keys(validationResults.value)) {
			if (
				!validationResults.value[key as keyof typeof validationResults.value]
					.message
			) {
				validationResults.value[key as keyof typeof validationResults.value] = {
					valid: false,
					message: "验证过程中发生未知错误",
				};
			}
		}
	} finally {
		validating.value = false;
	}
};

const resetAll = () => {
	form.value = {
		coordinator: { apiKey: "", baseUrl: "", modelId: "", provider: "" },
		modeler: { apiKey: "", baseUrl: "", modelId: "", provider: "" },
		coder: { apiKey: "", baseUrl: "", modelId: "", provider: "" },
		writer: { apiKey: "", baseUrl: "", modelId: "", provider: "" },
		openalex_email: "",
	};
	unifiedConfig.value = { apiKey: "", baseUrl: "", modelId: "", provider: "" };
};

// 应用统一配置到所有Agent
const applyUnifiedConfig = () => {
	if (!unifiedConfig.value.apiKey || !unifiedConfig.value.modelId) {
		return;
	}
	form.value.coordinator = { ...unifiedConfig.value };
	form.value.modeler = { ...unifiedConfig.value };
	form.value.coder = { ...unifiedConfig.value };
	form.value.writer = { ...unifiedConfig.value };
};

// 切换统一配置模式
const toggleUnifiedMode = () => {
	unifiedMode.value = !unifiedMode.value;
	if (unifiedMode.value && form.value.coordinator.apiKey) {
		// 如果开启统一模式且已有配置，使用coordinator的配置
		unifiedConfig.value = { ...form.value.coordinator };
	}
};

const providerCategories = {
	popular: {
		label: "🔥 热门推荐",
		providers: {
			DeepSeek: {
				url: "https://platform.deepseek.com/api_keys",
				key: "DeepSeek",
				baseUrl: "https://api.deepseek.com",
				modelId: "deepseek-chat",
				description: "高性价比的国产大模型",
			},
			硅基流动: {
				url: "https://cloud.siliconflow.cn/i/UIb4Enf4",
				key: "硅基流动",
				baseUrl: "https://api.siliconflow.cn",
				modelId: "deepseek-ai/DeepSeek-V3",
				description: "国内稳定访问",
			},
			OpenAI: {
				url: "https://platform.openai.com/api-keys",
				key: "OpenAI",
				baseUrl: "https://api.openai.com/v1",
				modelId: "gpt-4o",
				description: "GPT系列模型",
			},
			"302.AI": {
				url: "https://share.302.ai/UoTruU",
				key: "302.AI",
				baseUrl: "https://api.302.ai",
				modelId: "deepseek-chat",
				description: "一站式AI平台",
			},
		},
	},
	international: {
		label: "🌍 国际厂商",
		providers: {
			Anthropic: {
				url: "https://console.anthropic.com/",
				key: "Anthropic (Claude)",
				baseUrl: "https://api.anthropic.com",
				modelId: "claude-3-5-sonnet-20241022",
				description: "Claude系列模型",
			},
			"Google Gemini": {
				url: "https://aistudio.google.com/app/apikey",
				key: "Google Gemini",
				baseUrl: "https://generativelanguage.googleapis.com",
				modelId: "gemini/gemini-2.0-flash-exp",
				description: "Google最新模型",
			},
			xAI: {
				url: "https://console.x.ai/",
				key: "xAI (Grok)",
				baseUrl: "https://api.x.ai/v1",
				modelId: "grok-beta",
				description: "Grok系列模型",
			},
			"Mistral AI": {
				url: "https://console.mistral.ai/",
				key: "Mistral AI",
				baseUrl: "https://api.mistral.ai/v1",
				modelId: "mistral-large-latest",
				description: "欧洲开源模型",
			},
			Cohere: {
				url: "https://dashboard.cohere.com/api-keys",
				key: "Cohere",
				baseUrl: "https://api.cohere.ai",
				modelId: "command-r-plus",
				description: "企业级AI模型",
			},
		},
	},
	fast: {
		label: "⚡ 高速推理",
		providers: {
			Groq: {
				url: "https://console.groq.com/keys",
				key: "Groq",
				baseUrl: "https://api.groq.com/openai/v1",
				modelId: "llama-3.3-70b-versatile",
				description: "超快推理速度",
			},
			"Fireworks AI": {
				url: "https://fireworks.ai/api-keys",
				key: "Fireworks AI",
				baseUrl: "https://api.fireworks.ai/inference/v1",
				modelId: "accounts/fireworks/models/llama-v3p3-70b-instruct",
				description: "高性能推理",
			},
			"Together AI": {
				url: "https://api.together.xyz/settings/api-keys",
				key: "Together AI",
				baseUrl: "https://api.together.xyz/v1",
				modelId: "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
				description: "开源模型托管",
			},
		},
	},
	chinese: {
		label: "🇨🇳 国产模型",
		providers: {
			"Moonshot AI": {
				url: "https://platform.moonshot.cn/console/api-keys",
				key: "Moonshot AI (Kimi)",
				baseUrl: "https://api.moonshot.cn/v1",
				modelId: "moonshot-v1-8k",
				description: "Kimi长文本模型",
			},
			智谱AI: {
				url: "https://open.bigmodel.cn/usercenter/apikeys",
				key: "智谱AI (GLM)",
				baseUrl: "https://open.bigmodel.cn/api/paas/v4",
				modelId: "glm-4-plus",
				description: "GLM系列模型",
			},
			阿里通义: {
				url: "https://dashscope.console.aliyun.com/apiKey",
				key: "阿里通义",
				baseUrl: "https://dashscope.aliyuncs.com/api/v1",
				modelId: "qwen-plus",
				description: "通义千问",
			},
		},
	},
	aggregator: {
		label: "🔀 聚合平台",
		providers: {
			OpenRouter: {
				url: "https://openrouter.ai/keys",
				key: "OpenRouter",
				baseUrl: "https://openrouter.ai/api/v1",
				modelId: "anthropic/claude-3.5-sonnet",
				description: "多模型聚合",
			},
			"Perplexity AI": {
				url: "https://www.perplexity.ai/settings/api",
				key: "Perplexity AI",
				baseUrl: "https://api.perplexity.ai",
				modelId: "llama-3.1-sonar-large-128k-online",
				description: "在线搜索增强",
			},
			Sophnet: {
				url: "https://www.sophnet.com/#?code=AZBSFG",
				key: "Sophnet",
				baseUrl: "https://www.sophnet.com/api/open-apis",
				modelId: "DeepSeek-V3-Fast",
				description: "API聚合平台",
			},
		},
	},
	custom: {
		label: "⚙️ 自定义",
		providers: {
			"OpenAI 兼容": {
				url: "/",
				key: "OpenAI 兼容",
				baseUrl: "https://your-api-endpoint.com/v1",
				modelId: "your-model-id",
				description: "自定义兼容端点",
			},
		},
	},
};

// 扁平化的providers对象用于向后兼容
const providers = Object.values(providerCategories).reduce(
	(acc, category) => {
		return Object.assign(acc, category.providers);
	},
	{} as Record<
		string,
		{
			url: string;
			key: string;
			baseUrl: string;
			modelId: string;
			description: string;
		}
	>,
);

// 当供应商选择改变时，自动填写配置
const onProviderChange = (configKey: string, providerKey: string) => {
	const provider = providers[providerKey as keyof typeof providers];
	if (provider) {
		if (configKey === "unified") {
			// 统一配置模式
			unifiedConfig.value.provider = providerKey;
			unifiedConfig.value.baseUrl = provider.baseUrl;
			unifiedConfig.value.modelId = provider.modelId;
		} else {
			// 单独配置模式
			const formConfig =
				form.value[
					configKey as keyof Omit<typeof form.value, "openalex_email">
				];
			formConfig.provider = providerKey;
			formConfig.baseUrl = provider.baseUrl;
			formConfig.modelId = provider.modelId;

			// 清除之前的验证结果
			validationResults.value[
				configKey as keyof typeof validationResults.value
			] = {
				valid: false,
				message: "",
			};
		}
	}
};
</script>

<template>
  <Dialog :open="props.open" @update:open="updateOpen">
    <DialogContent class="max-w-3xl max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2 text-xl">
          <Settings2 class="w-5 h-5 text-blue-600" />
          API 配置
        </DialogTitle>
        <DialogDescription class="text-sm">
          为每个 Agent 配置合适的模型，或使用统一配置快速设置所有 Agent
          <a href="https://docs.litellm.ai/docs/providers" target="_blank"
            class="text-blue-600 hover:text-blue-800 underline ml-2">
            查看支持的提供商
          </a>
        </DialogDescription>
      </DialogHeader>

      <!-- 统一配置模式切换 -->
      <div class="flex items-center gap-3 p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
        <Wand2 class="w-5 h-5 text-blue-600" />
        <div class="flex-1">
          <h3 class="text-sm font-semibold text-gray-900">统一配置模式</h3>
          <p class="text-xs text-gray-600">为所有 Agent 使用相同的模型配置</p>
        </div>
        <Button
          @click="toggleUnifiedMode"
          :variant="unifiedMode ? 'default' : 'outline'"
          size="sm"
          class="transition-all"
        >
          {{ unifiedMode ? '已启用' : '启用' }}
        </Button>
      </div>

      <!-- 统一配置表单 -->
      <div v-if="unifiedMode" class="space-y-3 p-4 border-2 border-blue-300 rounded-lg bg-blue-50/50">
        <div class="flex items-center gap-2 mb-2">
          <Sparkles class="w-4 h-4 text-blue-600" />
          <h3 class="text-sm font-semibold text-gray-900">统一配置</h3>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div class="space-y-2">
            <Label class="text-xs text-gray-700 font-medium">提供商</Label>
            <div class="flex gap-2">
              <Select :model-value="unifiedConfig.provider"
                @update:model-value="(value: any) => value && onProviderChange('unified', String(value))">
                <SelectTrigger class="h-9 text-sm">
                  <SelectValue placeholder="选择提供商" />
                </SelectTrigger>
                <SelectContent class="max-h-[400px]">
                  <div v-for="(category, catKey) in providerCategories" :key="catKey">
                    <SelectLabel class="text-xs font-semibold text-gray-700 px-2 py-1 sticky top-0 bg-white">
                      {{ (category as any).label }}
                    </SelectLabel>
                    <SelectItem v-for="(provider, key) in (category as any).providers" :key="key" :value="key"
                      class="text-sm pl-2">
                      <div class="flex flex-col gap-0.5">
                        <span class="font-medium">{{ (provider as any).key }}</span>
                        <span class="text-xs text-gray-500">{{ (provider as any).description }}</span>
                      </div>
                    </SelectItem>
                  </div>
                </SelectContent>
              </Select>
              <a v-if="unifiedConfig.provider"
                :href="providers[unifiedConfig.provider as keyof typeof providers]?.url"
                target="_blank"
                class="flex items-center px-3 py-2 text-xs text-blue-600 hover:text-blue-800 underline border rounded-md hover:bg-blue-50">
                获取
              </a>
            </div>
          </div>

          <div class="space-y-2">
            <Label class="text-xs text-gray-700 font-medium">API Key</Label>
            <Input v-model.trim="unifiedConfig.apiKey" type="password"
              placeholder="请输入 API Key" class="h-9 text-sm" />
          </div>

          <div class="space-y-2">
            <Label class="text-xs text-gray-700 font-medium">Base URL</Label>
            <Input v-model.trim="unifiedConfig.baseUrl"
              placeholder="例如: https://api.openai.com" class="h-9 text-sm" />
          </div>

          <div class="space-y-2">
            <Label class="text-xs text-gray-700 font-medium">Model ID</Label>
            <Input v-model.trim="unifiedConfig.modelId"
              placeholder="例如: gpt-4" class="h-9 text-sm" />
          </div>
        </div>

        <Button @click="applyUnifiedConfig" class="w-full mt-2" size="sm">
          <Copy class="w-4 h-4 mr-2" />
          应用到所有 Agent
        </Button>
      </div>

      <div class="space-y-4 py-2" v-if="!unifiedMode">
        <!-- 全部展开/折叠按钮 -->
        <div class="flex justify-between items-center">
          <h3 class="text-sm font-semibold text-gray-800">Agent 配置</h3>
          <Button @click="toggleAllAgents" variant="ghost" size="sm" class="h-8 text-xs">
            <ChevronDown class="w-3.5 h-3.5 mr-1" />
            {{ Object.values(collapsedAgents).every(v => v) ? '全部展开' : '全部折叠' }}
          </Button>
        </div>

        <!-- Models Configurations -->
        <div v-for="config in modelConfigs" :key="config.key"
          class="border rounded-lg shadow-sm hover:shadow-md transition-all bg-gradient-to-br from-white to-gray-50 overflow-hidden">
          <!-- 可折叠的标题栏 -->
          <div
            @click="toggleAgentCollapse(config.key)"
            class="flex items-center gap-2 p-4 cursor-pointer hover:bg-gray-50 transition-colors"
          >
            <div :class="[
              'w-2 h-2 rounded-full',
              config.key === 'coordinator' ? 'bg-blue-500' :
              config.key === 'modeler' ? 'bg-green-500' :
              config.key === 'coder' ? 'bg-purple-500' : 'bg-orange-500'
            ]"></div>
            <h3 class="text-sm font-semibold text-gray-800 flex-1">{{ config.label }}</h3>
            <div v-if="validationResults[config.key as keyof typeof validationResults].valid"
              class="flex items-center gap-1 text-xs text-green-600">
              <CheckCircle class="w-3.5 h-3.5" />
              <span class="hidden sm:inline">已验证</span>
            </div>
            <ChevronDown v-if="!collapsedAgents[config.key]" class="w-4 h-4 text-gray-500 transition-transform" />
            <ChevronUp v-else class="w-4 h-4 text-gray-500 transition-transform" />
          </div>

          <!-- 可折叠的内容区 -->
          <div v-show="!collapsedAgents[config.key]" class="px-4 pb-4 space-y-3">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="space-y-1">
              <Label :for="`${config.key}-provider`" class="text-xs text-muted-foreground">提供商</Label>

              <div class="flex gap-2 items-center">
                <Select :model-value="(form as any)[config.key].provider"
                  @update:model-value="(value: any) => value && onProviderChange(config.key, String(value))">
                  <SelectTrigger class="w-full sm:w-[180px] h-9 text-sm">
                    <SelectValue placeholder="选择提供商" />
                  </SelectTrigger>
                  <SelectContent class="max-h-[400px]">
                    <div v-for="(category, catKey) in providerCategories" :key="catKey">
                      <SelectLabel class="text-xs font-semibold text-gray-700 px-2 py-1 sticky top-0 bg-white">
                        {{ category.label }}
                      </SelectLabel>
                      <SelectItem v-for="(provider, key) in category.providers" :key="key" :value="key"
                        class="text-sm pl-4">
                        <div class="flex flex-col gap-0.5">
                          <span class="font-medium">{{ (provider as any).key }}</span>
                          <span class="text-xs text-gray-500">{{ (provider as any).description }}</span>
                        </div>
                      </SelectItem>
                    </div>
                  </SelectContent>
                </Select>
                <div v-if="(form as any)[config.key].provider">
                  <a :href="providers[(form as any)[config.key].provider as keyof typeof providers]?.url"
                    target="_blank" class="text-blue-600 hover:text-blue-800 underline text-xs">
                    {{ providers[(form as any)[config.key].provider as keyof typeof providers]?.key }}
                  </a>
                </div>
              </div>
            </div>

            <div class="space-y-2">
              <Label :for="`${config.key}-api-key`" class="text-xs text-gray-700 font-medium">API Key</Label>
              <div class="relative">
                <Input :id="`${config.key}-api-key`" v-model.trim="(form as any)[config.key].apiKey" type="password"
                  placeholder="请输入 API Key" class="h-9 text-sm pr-10" />
                <div v-if="validationResults[config.key as keyof typeof validationResults].message"
                  class="absolute right-2 top-1/2 -translate-y-1/2">
                  <CheckCircle v-if="validationResults[config.key as keyof typeof validationResults].valid"
                    class="h-4 w-4 text-green-500" />
                  <XCircle v-else class="h-4 w-4 text-red-500" />
                </div>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="space-y-2">
              <Label :for="`${config.key}-base-url`" class="text-xs text-gray-700 font-medium">Base URL</Label>
              <Input :id="`${config.key}-base-url`" v-model.trim="(form as any)[config.key].baseUrl"
                placeholder="例如: https://api.openai.com" class="h-9 text-sm" />
            </div>
            <div class="space-y-2">
              <Label :for="`${config.key}-model-id`" class="text-xs text-gray-700 font-medium">Model ID</Label>
              <Input :id="`${config.key}-model-id`" v-model.trim="(form as any)[config.key].modelId"
                placeholder="例如: gpt-4" class="h-9 text-sm" />
            </div>
          </div>
          <div v-if="validationResults[config.key as keyof typeof validationResults].message" :class="[
            'text-xs px-3 py-2 rounded-md text-left border flex items-start gap-2',
            validationResults[config.key as keyof typeof validationResults].valid ?
              'bg-green-50 text-green-700 border-green-200' :
              'bg-red-50 text-red-700 border-red-200'
          ]">
            <CheckCircle v-if="validationResults[config.key as keyof typeof validationResults].valid"
              class="w-4 h-4 flex-shrink-0 mt-0.5" />
            <XCircle v-else class="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span class="flex-1">{{ validationResults[config.key as keyof typeof validationResults].message }}</span>
          </div>
          </div>
        </div>
      </div>



      <!-- OpenAlex Email配置 -->
      <div class="space-y-3 p-4 border rounded-lg bg-gradient-to-br from-purple-50 to-pink-50">
        <div class="flex items-center gap-2">
          <div class="w-2 h-2 rounded-full bg-purple-500"></div>
          <h3 class="text-sm font-semibold text-gray-800">文献访问</h3>
        </div>
        <div class="space-y-2">
          <Label :for="`openalex-email`" class="text-xs text-gray-700 font-medium">OpenAlex Email</Label>
          <div class="text-xs text-gray-600 mb-2">
            使用 email 注册账号从 <a href="https://openalex.org/" target="_blank"
              class="text-blue-600 hover:text-blue-800 underline font-medium">OpenAlex</a> 获取访问文献权利
          </div>
          <Input :id="`openalex-email`" v-model.trim="form.openalex_email" placeholder="请输入 OpenAlex Email"
            type="email" class="h-9 text-sm" />
          <div v-if="validationResults.openalex_email.message" :class="[
            'text-xs px-3 py-2 rounded-md text-left border flex items-start gap-2',
            validationResults.openalex_email.valid ?
              'bg-green-50 text-green-700 border-green-200' :
              'bg-red-50 text-red-700 border-red-200'
          ]">
            <CheckCircle v-if="validationResults.openalex_email.valid"
              class="w-4 h-4 flex-shrink-0 mt-0.5" />
            <XCircle v-else class="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span class="flex-1">{{ validationResults.openalex_email.message }}</span>
          </div>
        </div>
      </div>

      <!-- 底部操作按钮 -->
      <div class="flex flex-col sm:flex-row justify-between items-center gap-3 pt-4 border-t">
        <div class="flex flex-wrap items-center gap-2 w-full sm:w-auto">
          <Button @click="validateAllApiKeys" :disabled="validating"
            class="flex-1 sm:flex-none h-9 text-sm px-4"
            variant="secondary">
            <Sparkles :class="['w-4 h-4 mr-2', validating && 'animate-spin']" />
            {{ validating ? '验证中...' : '一键验证' }}
          </Button>
          <Button @click="resetAll" class="flex-1 sm:flex-none h-9 text-sm px-4" variant="outline">
            重置
          </Button>
        </div>
        <div class="flex space-x-2 w-full sm:w-auto">
          <Button variant="outline" @click="updateOpen(false)" class="flex-1 sm:flex-none h-9 text-sm px-4">
            取消
          </Button>
          <Button @click="saveAndClose" class="flex-1 sm:flex-none h-9 text-sm px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700">
            保存配置
          </Button>
        </div>
      </div>
    </DialogContent>
  </Dialog>
</template>
