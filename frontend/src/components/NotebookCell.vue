<script setup lang="ts">
import type { CodeCell, NoteCell, ResultCell } from "@/utils/interface";
import { renderMarkdown } from "@/utils/markdown";
import type { OutputItem } from "@/utils/response";
import hljs from "highlight.js/lib/core";
import python from "highlight.js/lib/languages/python";
import { Check, ChevronDown, ChevronRight, Copy } from "lucide-vue-next";
import { computed, ref } from "vue";
import "highlight.js/styles/github.css";

// 注册Python语言支持
hljs.registerLanguage("python", python);

const props = defineProps<{
  cell: NoteCell;
}>();

const isCodeCollapsed = ref(false);
const isResultCollapsed = ref(false);
const isCopied = ref(false);

// 获取结果格式的CSS类
const getResultClass = (result: OutputItem) => {
  switch (result.res_type) {
    case "stdout":
      return "text-gray-600";
    case "stderr":
      return "text-orange-600";
    case "error":
      return "text-red-600";
    default:
      return "text-gray-800";
  }
};

// 判断结果是否为图片
const isImageResult = (result: OutputItem) => {
  return (
    result.res_type === "result" &&
    ["png", "jpeg", "svg"].includes(result.format as string)
  );
};

// 判断结果是否为LaTeX
const isLatexResult = (result: OutputItem) => {
  return result.res_type === "result" && result.format === "latex";
};

// 判断结果是否为JSON
const isJsonResult = (result: OutputItem) => {
  return result.res_type === "result" && result.format === "json";
};

// 格式化JSON显示
const formatJson = (jsonString: string) => {
  try {
    const parsed = JSON.parse(jsonString);
    return JSON.stringify(parsed, null, 2);
  } catch (e) {
    return jsonString;
  }
	try {
		const parsed = JSON.parse(jsonString);
		return JSON.stringify(parsed, null, 2);
	} catch (e) {
		return jsonString;
	}
};

// 渲染Markdown内容
const renderMarkdownContent = (content: string) => {
	return renderMarkdown(content);
};

// 类型守卫函数，用于区分单元格类型
const isCodeCell = (cell: NoteCell): cell is CodeCell => {
	return cell.type === "code";
};

const isResultCell = (cell: NoteCell): cell is ResultCell => {
	return cell.type === "result";
};

// 语法高亮
const highlightedCode = computed(() => {
	if (isCodeCell(props.cell)) {
		try {
			return hljs.highlight(props.cell.content, { language: "python" }).value;
		} catch (e) {
			return props.cell.content;
		}
	}
	return "";
});

// 复制代码
const copyCode = async () => {
	if (isCodeCell(props.cell)) {
		try {
			await navigator.clipboard.writeText(props.cell.content);
			isCopied.value = true;
			setTimeout(() => {
				isCopied.value = false;
			}, 2000);
		} catch (e) {
			console.error("Failed to copy code:", e);
		}
	}
};

// 切换折叠
const toggleCodeCollapse = () => {
	isCodeCollapsed.value = !isCodeCollapsed.value;
};

const toggleResultCollapse = () => {
	isResultCollapsed.value = !isResultCollapsed.value;
};

// 代码行数
const codeLines = computed(() => {
	if (isCodeCell(props.cell)) {
		return props.cell.content.split("\n").length;
	}
	return 0;
});

// 是否应该显示折叠按钮（代码超过10行）
const shouldShowCollapseButton = computed(() => {
	return codeLines.value > 10;
});
</script>

<template>
  <div :class="[
    'bg-white rounded-lg shadow-sm overflow-hidden transition-all duration-200',
    'border border-gray-200 hover:border-blue-300 hover:shadow-md',
    cell.type === 'code' ? 'code-cell' : 'result-cell'
  ]">
    <!-- 单元格头部 -->
    <div
      class="px-3 py-2 flex items-center justify-between bg-gradient-to-r from-gray-50 via-white to-gray-50 border-b border-gray-200">
      <div class="flex items-center space-x-2">
        <span :class="[
          'px-2 py-1 rounded text-xs font-semibold',
          cell.type === 'code' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'
        ]">
          {{ cell.type === 'code' ? '💻 Python Code' : '📊 Output' }}
        </span>
        <!-- 代码行数 -->
        <span v-if="cell.type === 'code' && codeLines > 0" class="text-xs text-gray-500">
          {{ codeLines }} {{ codeLines === 1 ? 'line' : 'lines' }}
        </span>
      </div>

      <!-- 操作按钮 -->
      <div class="flex items-center gap-2">
        <!-- 复制按钮（仅代码单元格） -->
        <button
          v-if="cell.type === 'code'"
          @click="copyCode"
          class="p-1.5 rounded hover:bg-gray-100 transition-colors group"
          :title="isCopied ? '已复制!' : '复制代码'"
        >
          <Check v-if="isCopied" class="w-4 h-4 text-green-600" />
          <Copy v-else class="w-4 h-4 text-gray-500 group-hover:text-blue-600" />
        </button>

        <!-- 折叠按钮 -->
        <button
          v-if="shouldShowCollapseButton || cell.type === 'result'"
          @click="cell.type === 'code' ? toggleCodeCollapse() : toggleResultCollapse()"
          class="p-1.5 rounded hover:bg-gray-100 transition-colors"
          :title="(cell.type === 'code' ? isCodeCollapsed : isResultCollapsed) ? '展开' : '折叠'"
        >
          <ChevronDown v-if="cell.type === 'code' ? !isCodeCollapsed : !isResultCollapsed" class="w-4 h-4 text-gray-500" />
          <ChevronRight v-else class="w-4 h-4 text-gray-500" />
        </button>
      </div>
    </div>

    <!-- 代码内容 -->
    <div class="relative">
      <!-- 代码单元格 -->
      <template v-if="isCodeCell(cell)">
        <div v-if="!isCodeCollapsed" class="relative group">
          <!-- 行号和代码 -->
          <div class="flex">
            <!-- 行号列 -->
            <div class="select-none bg-gray-50 px-3 py-4 text-right border-r border-gray-200">
              <div v-for="(_, index) in cell.content.split('\n')" :key="index"
                class="text-xs text-gray-400 leading-6 font-mono">
                {{ index + 1 }}
              </div>
            </div>
            <!-- 代码列 -->
            <div class="flex-1 p-4 overflow-x-auto bg-gray-50">
              <pre class="text-sm font-mono"><code v-html="highlightedCode" class="language-python"></code></pre>
            </div>
          </div>
        </div>
        <!-- 折叠状态 -->
        <div v-else class="px-4 py-3 bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors" @click="toggleCodeCollapse">
          <span class="text-xs text-gray-500 italic">{{ cell.content.split('\n')[0] }}...</span>
        </div>
      </template>

      <!-- 结果单元格 -->
      <template v-else-if="isResultCell(cell)">
        <div v-if="!isResultCollapsed" class="px-4 py-3 bg-gray-50">

          <!-- 遍历所有执行结果 -->
          <div v-for="(result, index) in cell.code_results" :key="index" class="mb-2 last:mb-0">
            <!-- 标准输出/错误 -->
            <template v-if="result.res_type === 'stdout' || result.res_type === 'stderr'">
              <div :class="['font-mono whitespace-pre-wrap text-sm', getResultClass(result)]">
                {{ result.msg }}
              </div>
            </template>

            <!-- 执行错误 -->
            <template v-else-if="result.res_type === 'error'">
              <div class="text-sm text-red-600 font-mono whitespace-pre-wrap">
                <div class="font-bold">{{ result.name }}: {{ result.value }}</div>
                <div>{{ result.traceback }}</div>
              </div>
            </template>

            <!-- 执行结果 - 图片 (PNG, JPEG, SVG) -->
            <template v-else-if="isImageResult(result)">
              <img :src="`data:image/${result.format};base64,${result.msg}`"
                   class="max-w-full rounded-lg shadow-sm" />
            </template>

            <!-- 执行结果 - HTML -->
            <template v-else-if="result.res_type === 'result' && result.format === 'html'">
              <div class="prose prose-sm max-w-none" v-html="result.msg || ''"></div>
            </template>

            <!-- 执行结果 - Markdown -->
            <template v-else-if="result.res_type === 'result' && result.format === 'markdown'">
              <div class="prose prose-sm max-w-none" v-html="renderMarkdownContent(result.msg || '')"></div>
            </template>

            <!-- 执行结果 - LaTeX -->
            <template v-else-if="isLatexResult(result)">
              <div class="katex-display" v-html="result.msg || ''"></div>
            </template>

            <!-- 执行结果 - JSON -->
            <template v-else-if="isJsonResult(result)">
              <pre class="text-sm bg-gray-50 p-2 rounded overflow-x-auto">{{ formatJson(result.msg || '') }}</pre>
            </template>

            <!-- 执行结果 - 默认文本 -->
            <template v-else>
              <div class="text-sm text-gray-600 font-mono whitespace-pre-wrap">
                {{ result.msg }}
              </div>
            </template>
          </div>
        </div>
        <!-- 折叠状态 -->
        <div v-else class="px-4 py-2 bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors" @click="toggleResultCollapse">
          <span class="text-xs text-gray-500 italic">{{ cell.code_results.length }} 条输出结果...</span>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
/* 代码样式 */
.code-cell pre {
  background-color: rgb(249 250 251);
  border-radius: 0.375rem;
  padding: 0.5rem;
}

.code-cell code {
  color: rgb(31 41 55);
}

/* 结果样式 */
.result-cell {
  margin-top: -0.25rem;
  border-top-left-radius: 0;
  border-top-right-radius: 0;
}
</style>
