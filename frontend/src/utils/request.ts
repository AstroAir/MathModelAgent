// src/utils/request.js
import axios from "axios";
import { toast } from "@/components/ui/toast";
// import { message } from 'antd' // 或其他UI库的消息提示组件

// 创建axios实例
const service = axios.create({
	baseURL: import.meta.env.VITE_API_BASE_URL, // 从环境变量获取基础URL
	timeout: 10000, // 请求超时时间
});

// 请求拦截器
service.interceptors.request.use(
	(config) => {
		// 在发送请求之前做些什么
		// 例如：如果有token，添加到请求头
		// const token = localStorage.getItem('token')
		// if (token) {
		//   config.headers['Authorization'] = `Bearer ${token}`
		// }
		return config;
	},
	(error) => {
		// 对请求错误做些什么
		console.log(error); // for debug
		return Promise.reject(error);
	},
);

// 响应拦截器
service.interceptors.response.use(
	(response) => {
		// 对响应数据做点什么
		return response;
	},
	(error) => {
		// 对响应错误做全局处理（仅网络错误或服务器错误时提示）
		const status = error?.response?.status as number | undefined;
		const detail =
			(error?.response?.data &&
				((error.response.data as any).detail || (error.response.data as any).message)) ||
			(error?.message as string | undefined);
		const description =
			detail || (status ? `请求失败，状态码：${status}` : "请求失败，请检查网络连接");

		// 仅在没有显式处理的情况下进行全局提示：网络错误或 5xx
		if (!status || status >= 500) {
			toast({
				title: "请求异常",
				description,
				variant: "destructive",
			});
		}

		return Promise.reject(error);
	},
);

export default service;
