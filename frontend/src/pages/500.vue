<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Home, RefreshCw, AlertTriangle, Copy, Check } from "lucide-vue-next";

const router = useRouter();
const copied = ref(false);

// 错误详情（可以从路由参数或全局状态获取）
const errorDetails = ref({
	message: "服务器内部错误",
	code: "INTERNAL_SERVER_ERROR",
	timestamp: new Date().toISOString(),
	requestId: `req_${Math.random().toString(36).substr(2, 9)}`,
});

const goHome = () => {
	router.push("/");
};

const reload = () => {
	window.location.reload();
};

const copyErrorDetails = async () => {
	const details = `
错误信息: ${errorDetails.value.message}
错误代码: ${errorDetails.value.code}
时间戳: ${errorDetails.value.timestamp}
请求ID: ${errorDetails.value.requestId}
	`.trim();

	try {
		await navigator.clipboard.writeText(details);
		copied.value = true;
		setTimeout(() => {
			copied.value = false;
		}, 2000);
	} catch (err) {
		console.error("Failed to copy:", err);
	}
};
</script>

<template>
  <div class="min-h-screen bg-background flex items-center justify-center p-4">
    <Card class="w-full max-w-2xl">
      <CardHeader class="text-center space-y-4">
        <div class="flex justify-center">
          <div class="relative">
            <AlertTriangle class="h-24 w-24 text-destructive opacity-20" />
            <div class="absolute inset-0 flex items-center justify-center">
              <span class="text-6xl font-bold text-destructive">500</span>
            </div>
          </div>
        </div>
        <CardTitle class="text-3xl">服务器错误</CardTitle>
        <CardDescription class="text-lg">
          抱歉，服务器遇到了一个问题，我们正在努力修复
        </CardDescription>
      </CardHeader>
      <CardContent class="space-y-6">
        <Alert variant="destructive">
          <AlertTriangle class="h-4 w-4" />
          <AlertDescription>
            {{ errorDetails.message }}
          </AlertDescription>
        </Alert>

        <div class="bg-muted/50 rounded-lg p-4 space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="font-semibold text-sm">错误详情</h3>
            <Button
              @click="copyErrorDetails"
              variant="ghost"
              size="sm"
              class="h-8 px-2"
            >
              <component :is="copied ? Check : Copy" class="h-3 w-3 mr-1" />
              {{ copied ? "已复制" : "复制" }}
            </Button>
          </div>
          <div class="space-y-2 text-sm font-mono">
            <div class="flex justify-between">
              <span class="text-muted-foreground">错误代码:</span>
              <span class="font-semibold">{{ errorDetails.code }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-muted-foreground">时间戳:</span>
              <span>{{ new Date(errorDetails.timestamp).toLocaleString() }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-muted-foreground">请求ID:</span>
              <span>{{ errorDetails.requestId }}</span>
            </div>
          </div>
        </div>

        <div class="bg-muted/50 rounded-lg p-4 space-y-2">
          <h3 class="font-semibold text-sm">您可以尝试：</h3>
          <ul class="text-sm text-muted-foreground space-y-1 list-disc list-inside">
            <li>刷新页面重试</li>
            <li>检查网络连接</li>
            <li>稍后再试</li>
            <li>如果问题持续，请联系技术支持并提供上述错误详情</li>
          </ul>
        </div>

        <div class="flex flex-col sm:flex-row gap-3">
          <Button @click="reload" class="flex-1" size="lg">
            <RefreshCw class="h-4 w-4 mr-2" />
            刷新页面
          </Button>
          <Button @click="goHome" variant="outline" class="flex-1" size="lg">
            <Home class="h-4 w-4 mr-2" />
            返回首页
          </Button>
        </div>

        <div class="text-center text-sm text-muted-foreground">
          <p>我们已记录此错误，技术团队将尽快处理</p>
        </div>
      </CardContent>
    </Card>
  </div>
</template>
