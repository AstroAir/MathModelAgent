<script setup lang="ts">
import {
	Sidebar,
	SidebarContent,
	SidebarFooter,
	SidebarGroup,
	SidebarGroupContent,
	SidebarGroupLabel,
	SidebarHeader,
	SidebarMenu,
	SidebarMenuButton,
	SidebarMenuItem,
} from "@/components/ui/sidebar";
import NavUser from "@/components/NavUser.vue";
import { Home, MessageSquare, Settings, History } from "lucide-vue-next";
import { useRouter } from "vue-router";

const router = useRouter();

const menuItems = [
	{ icon: Home, label: "首页", path: "/" },
	{ icon: MessageSquare, label: "对话", path: "/chat" },
	{ icon: History, label: "历史记录", path: "/history" },
	{ icon: Settings, label: "设置", path: "/settings" },
];

const navigateTo = (path: string) => {
	router.push(path);
};
</script>

<template>
  <Sidebar>
    <SidebarHeader>
      <div class="flex items-center gap-2 px-4 py-3">
        <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          M
        </div>
        <div class="flex flex-col">
          <span class="text-sm font-semibold">MathModelAgent</span>
          <span class="text-xs text-muted-foreground">智能建模助手</span>
        </div>
      </div>
    </SidebarHeader>

    <SidebarContent>
      <SidebarGroup>
        <SidebarGroupLabel>导航</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="item in menuItems" :key="item.path">
              <SidebarMenuButton @click="navigateTo(item.path)">
                <component :is="item.icon" class="h-4 w-4" />
                <span>{{ item.label }}</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>

    <SidebarFooter>
      <NavUser />
    </SidebarFooter>
  </Sidebar>
</template>
