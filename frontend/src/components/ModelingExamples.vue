<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { Sparkles } from "lucide-vue-next";
import { ref } from "vue";
import { useRouter } from "vue-router";

import { exampleAPI } from "@/apis/commonApi";
import mcmCupC from "@/assets/example/2024高教杯C题.png";
import wuyiCupC from "@/assets/example/2025五一杯C题.png";
// 导入图片资源
import huashuCupC from "@/assets/example/华数杯2023年C题.png";

// 定义样例类型
interface ModelingExample {
	id: number;
	title: string;
	source: string;
	description: string;
	tags: string[];
	problemText: string;
	image: string;
	category: string;
}

// 定义emit
const emit = defineEmits<{
	"example-selected": [];
}>();

const router = useRouter();
const examples = ref<ModelingExample[]>([
	{
		id: 1,
		title: "母亲身心健康对婴儿成长的影响",
		source: "2023华数杯C题",
		description:
			"研究母亲身心健康对婴儿成长的影响，建立预测模型分析婴儿成长情况",
		tags: ["分类问题", "成长", "健康"],
		problemText: "给定母亲身心健康数据，建立一个预测模型，预测婴儿成长情况。",
		image: huashuCupC,
		category: "数据分析",
	},
	{
		id: 2,
		title: "社交媒体平台用户分析问题",
		source: "2025五一杯C题",
		description: "分析社交媒体平台用户行为特征，构建用户画像模型进行精准分析",
		tags: ["社交媒体", "用户行为"],
		problemText: "分析社交媒体平台用户行为特征，构建用户画像模型。",
		image: wuyiCupC,
		category: "行为分析",
	},
	{
		id: 3,
		title: "农作物的种植策略",
		source: "2024高教杯C题",
		description: "研究农作物的种植策略，建立优化模型使得农作物产量最大化",
		tags: ["种植策略", "农作物", "生长"],
		problemText:
			"研究农作物的种植策略，建立一个优化模型，使得农作物产量最大化。",
		image: mcmCupC,
		category: "优化问题",
	},
]);

// 选择样例并跳转到任务创建步骤
const selectExample = async (example: ModelingExample) => {
	const res = await exampleAPI(example.id.toString(), example.source);
	const task_id = res?.data?.task_id;
	emit("example-selected");
	router.push(`/task/${task_id}`);
};
</script>

<template>
  <div class="w-full">
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5 md:gap-6">
      <div
        v-for="(example, index) in examples"
        :key="example.id"
        class="example-card group relative bg-card rounded-2xl border border-border overflow-hidden hover:shadow-2xl hover:border-primary/50 transition-all duration-500 cursor-pointer"
        :style="{ animationDelay: `${index * 100}ms` }"
        @click="selectExample(example)"
      >
        <div class="absolute inset-0 bg-gradient-to-br from-primary/10 via-accent/10 to-secondary/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

        <div class="relative h-44 sm:h-48 overflow-hidden bg-gradient-to-br from-muted to-background">
          <img
            :src="example.image"
            :alt="example.title"
            class="w-full h-full object-cover object-top group-hover:scale-110 transition-transform duration-700 ease-out"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

          <div class="absolute top-3 right-3 px-2.5 py-1 bg-background/80 backdrop-blur-sm rounded-full text-xs font-medium text-foreground shadow-sm">
            {{ example.category }}
          </div>

          <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0">
            <Button variant="secondary" size="sm" class="shadow-lg hover:shadow-xl backdrop-blur-sm bg-background/80">
              <Sparkles class="w-3.5 h-3.5 mr-1.5" />
              开始使用
            </Button>
          </div>
        </div>

        <div class="relative p-4 sm:p-5">
          <div class="mb-3">
            <h3 class="text-base sm:text-lg font-semibold text-foreground line-clamp-2 mb-1.5 group-hover:text-primary transition-colors duration-300">
              {{ example.title }}
            </h3>
            <p class="text-xs text-primary font-medium mb-2">{{ example.source }}</p>
          </div>

          <p class="text-sm text-muted-foreground line-clamp-2 mb-4">
            {{ example.description }}
          </p>

          <div class="flex flex-wrap gap-1.5">
            <span
              v-for="tag in example.tags"
              :key="tag"
              class="px-2.5 py-1 bg-muted text-muted-foreground rounded-lg text-xs font-medium hover:bg-accent hover:text-accent-foreground transition-colors duration-200"
            >
              {{ tag }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.example-card {
  animation: fadeInUp 0.6s ease-out forwards;
  opacity: 0;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.example-card:hover {
  transform: translateY(-4px);
}
</style>
