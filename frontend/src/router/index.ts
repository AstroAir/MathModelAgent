// 封转路由
import { createRouter, createWebHistory } from "vue-router";
// 路由配置
// meau 需要登录后才能访问

const routes = [
	{
		path: "/",
		component: () => import("@/pages/index.vue"),
	},
	{
		path: "/login",
		component: () => import("@/pages/login/index.vue"),
	},
	{
		path: "/chat",
		component: () => import("@/pages/chat/index.vue"),
	},
	{
		path: "/task/:task_id",
		component: () => import("@/pages/task/index.vue"),
		props: true,
	},
	{
		path: "/history",
		component: () => import("@/pages/history/index.vue"),
	},
	{
		path: "/example/:id",
		component: () => import("@/pages/example/[id].vue"),
		props: true,
	},
	{
		path: "/settings",
		component: () => import("@/pages/settings/index.vue"),
	},
	{
		path: "/404",
		component: () => import("@/pages/404.vue"),
	},
	{
		path: "/500",
		component: () => import("@/pages/500.vue"),
	},
	{
		path: "/:pathMatch(.*)*",
		redirect: "/404",
	},
];

// 创建路由
const router = createRouter({
	history: createWebHistory(),
	routes,
});

// 路由守卫
// router.beforeEach((to, from, next) => {})

export default router;
