<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { getTaskTracking, type TaskTrackingResponse } from '@/apis/commonApi';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, DollarSign, Zap, TrendingUp } from 'lucide-vue-next';
import { useToast } from '@/components/ui/toast';

const props = defineProps<{
	taskId: string;
}>();

const { toast } = useToast();
const tracking = ref<TaskTrackingResponse | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);

const totalTokens = computed(() => {
	if (!tracking.value?.token_usage) return 0;
	return Object.values(tracking.value.token_usage)
		.reduce((sum, usage) => sum + usage.total_tokens, 0);
});

const hasData = computed(() => {
	return tracking.value && tracking.value.token_usage &&
		Object.keys(tracking.value.token_usage).length > 0;
});

const loadTracking = async () => {
	loading.value = true;
	error.value = null;
	try {
		const response = await getTaskTracking(props.taskId);
		tracking.value = response.data;

		if (tracking.value.error) {
			error.value = tracking.value.error;
		}
	} catch (err: any) {
		error.value = '加载成本统计失败';
		console.error('Failed to load tracking:', err);
		toast({
			title: '加载失败',
			description: error.value,
			variant: 'destructive',
		});
	} finally {
		loading.value = false;
	}
};

onMounted(() => {
	loadTracking();
});
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle class="flex items-center gap-2">
        <DollarSign class="h-5 w-5 text-primary" />
        成本统计
      </CardTitle>
      <CardDescription>Token 使用和费用明细</CardDescription>
    </CardHeader>
    <CardContent>
      <!-- 加载状态 -->
      <div v-if="loading" class="text-center py-8">
        <Loader2 class="h-8 w-8 mx-auto animate-spin text-primary" />
        <p class="text-sm text-muted-foreground mt-2">加载统计数据中...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="text-center py-8">
        <div class="text-destructive mb-2">{{ error }}</div>
        <button
          @click="loadTracking"
          class="text-sm text-primary hover:underline"
        >
          重试
        </button>
      </div>

      <!-- 无数据状态 -->
      <div v-else-if="!hasData" class="text-center py-8 text-muted-foreground">
        <TrendingUp class="h-12 w-12 mx-auto mb-2 opacity-50" />
        <p>暂无统计数据</p>
        <p class="text-xs mt-1">任务完成后将显示详细统计</p>
      </div>

      <!-- 数据展示 -->
      <div v-else class="space-y-4">
        <!-- 总览卡片 -->
        <div class="grid grid-cols-2 gap-4">
          <div class="p-4 bg-muted rounded-lg">
            <div class="text-sm text-muted-foreground mb-1">总 Token</div>
            <div class="text-2xl font-bold">
              {{ totalTokens.toLocaleString() }}
            </div>
          </div>
          <div class="p-4 bg-primary/10 rounded-lg">
            <div class="text-sm text-muted-foreground mb-1">总费用</div>
            <div class="text-2xl font-bold text-primary">
              ${{ tracking.total_cost.toFixed(4) }}
            </div>
          </div>
        </div>

        <!-- 各 Agent 明细 -->
        <div class="space-y-2">
          <div class="text-sm font-semibold text-foreground">各智能体使用情况</div>
          <div
            v-for="(usage, agent) in tracking.token_usage"
            :key="agent"
            class="flex items-center justify-between p-3 bg-muted/50 rounded-lg hover:bg-muted transition-colors"
          >
            <div class="flex items-center gap-2">
              <Zap class="h-4 w-4 text-primary flex-shrink-0" />
              <span class="font-medium text-sm">{{ agent }}</span>
            </div>
            <div class="flex items-center gap-3 text-sm">
              <Badge variant="outline" class="font-mono">
                {{ usage.total_tokens.toLocaleString() }} tokens
              </Badge>
              <span class="font-semibold text-primary min-w-[80px] text-right">
                ${{ usage.cost.toFixed(4) }}
              </span>
            </div>
          </div>
        </div>

        <!-- 刷新按钮 -->
        <div class="pt-2 border-t">
          <button
            @click="loadTracking"
            :disabled="loading"
            class="w-full py-2 text-sm text-muted-foreground hover:text-foreground transition-colors disabled:opacity-50"
          >
            {{ loading ? '刷新中...' : '刷新数据' }}
          </button>
        </div>
      </div>
    </CardContent>
  </Card>
</template>
