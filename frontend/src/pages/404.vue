<script setup lang="ts">
import { Button } from "@/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { ArrowLeft, FileQuestion, Home, Search } from "lucide-vue-next";
import { useRouter } from "vue-router";

const router = useRouter();

const goHome = () => {
	router.push("/");
};

const goBack = () => {
	router.back();
};

const goToChat = () => {
	router.push("/chat");
};
</script>

<template>
  <div class="min-h-screen bg-background flex items-center justify-center p-4">
    <Card class="w-full max-w-2xl">
      <CardHeader class="text-center space-y-4">
        <div class="flex justify-center">
          <div class="relative">
            <FileQuestion class="h-24 w-24 text-muted-foreground opacity-20" />
            <div class="absolute inset-0 flex items-center justify-center">
              <span class="text-6xl font-bold text-primary">404</span>
            </div>
          </div>
        </div>
        <CardTitle class="text-3xl">页面未找到</CardTitle>
        <CardDescription class="text-lg">
          抱歉，您访问的页面不存在或已被移除
        </CardDescription>
      </CardHeader>
      <CardContent class="space-y-6">
        <div class="bg-muted/50 rounded-lg p-4 space-y-2">
          <h3 class="font-semibold text-sm">可能的原因：</h3>
          <ul class="text-sm text-muted-foreground space-y-1 list-disc list-inside">
            <li>您输入的网址有误</li>
            <li>该页面已被删除或移动</li>
            <li>链接已过期</li>
          </ul>
        </div>

        <div class="flex flex-col sm:flex-row gap-3">
          <Button @click="goHome" class="flex-1" size="lg">
            <Home class="h-4 w-4 mr-2" />
            返回首页
          </Button>
          <Button @click="goBack" variant="outline" class="flex-1" size="lg">
            <ArrowLeft class="h-4 w-4 mr-2" />
            返回上一页
          </Button>
          <Button @click="goToChat" variant="outline" class="flex-1" size="lg">
            <Search class="h-4 w-4 mr-2" />
            开始建模
          </Button>
        </div>

        <div class="text-center text-sm text-muted-foreground">
          <p>如果问题持续存在，请联系技术支持</p>
        </div>
      </CardContent>
    </Card>
  </div>
</template>
