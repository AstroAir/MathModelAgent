<script setup lang="ts">
import {
	getAllFilesDownloadUrl,
	getFileContent,
	getFileDownloadUrl,
	getFiles,
} from "@/apis/filesApi";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
	Sheet,
	SheetContent,
	SheetDescription,
	SheetHeader,
	SheetTitle,
	SheetTrigger,
} from "@/components/ui/sheet";
import { useToast } from "@/components/ui/toast/use-toast";
import {
	Tooltip,
	TooltipContent,
	TooltipProvider,
	TooltipTrigger,
} from "@/components/ui/tooltip";
import {
	Archive,
	ArrowUpDown,
	Download,
	Eye,
	File,
	FileText,
	Files,
	Folder,
	LayoutGrid,
	List,
	RefreshCw,
	Search,
} from "lucide-vue-next";
import { computed, onUnmounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const taskId = route.params.task_id;

const { toast } = useToast();

// 文件列表相关
const fileListVisible = ref(false);
const fileList = ref<any[]>([]);
const loadingFiles = ref(false);
const downloadingFile = ref<string | null>(null);
const downloadingAll = ref(false);

// 搜索和过滤
const searchQuery = ref("");
const viewMode = ref<"compact" | "detailed">("detailed"); // 显示模式
const sortBy = ref<"name" | "size" | "time">("name"); // 排序方式
const sortOrder = ref<"asc" | "desc">("asc"); // 排序顺序

// 文件预览
const previewVisible = ref(false);
const previewFile = ref<any>(null);
const previewContent = ref("");
const loadingPreview = ref(false);

// 图片缩放
const imageZoom = ref(100); // 缩放百分比
const MIN_ZOOM = 10;
const MAX_ZOOM = 500;

// 图片拖动
const isDragging = ref(false);
const dragStart = ref({ x: 0, y: 0 });
const imagePosition = ref({ x: 0, y: 0 });
const showThumbnail = ref(false); // 是否显示缩略图导航

// 缩略图拖动
const isThumbnailDragging = ref(false);
const thumbnailDragStart = ref({ x: 0, y: 0 });
const imageContainerRef = ref<HTMLElement | null>(null);
const imageRef = ref<HTMLImageElement | null>(null);

// 图像信息
const imageNaturalSize = ref({ width: 0, height: 0 });
const imageFitZoom = ref(100); // 适应窗口的缩放比例
const showKeyboardHelp = ref(true); // 显示快捷键提示
let helpTimeout: number | null = null;

// 获取文件扩展名
const getFileExtension = (fileName: string) => {
	return fileName.split(".").pop()?.toLowerCase() || "";
};

// 解析CSV内容为表格数据
const parseCSV = (content: string) => {
	const lines = content.split("\n").filter((line) => line.trim());
	if (lines.length === 0) return { headers: [], rows: [] };

	const headers = lines[0].split(",").map((h) => h.trim());
	const rows = lines
		.slice(1)
		.map((line) => line.split(",").map((cell) => cell.trim()));

	return { headers, rows };
};

const openFolder = async () => {
	console.log("openFolder", taskId);
	try {
		loadingFiles.value = true;
		const res = await getFiles(taskId as string);
		console.log(res);

		if (res.data) {
			fileList.value = Array.isArray(res.data) ? res.data : [res.data];
			fileListVisible.value = true;
		} else {
			toast({
				title: "获取文件列表失败",
				description: "无法获取工作区文件列表",
				variant: "destructive",
			});
		}
	} catch (error) {
		console.error("获取文件列表失败:", error);
		toast({
			title: "错误",
			description: "获取文件列表时出现错误",
			variant: "destructive",
		});
	} finally {
		loadingFiles.value = false;
	}
};

// 获取文件图标
const getFileIcon = (fileName: string) => {
	const ext = fileName.split(".").pop()?.toLowerCase();
	const textExts = ["txt", "md", "json", "csv", "xml", "yml", "yaml"];

	if (textExts.includes(ext || "")) {
		return FileText;
	}
	return File;
};

// 获取文件大小格式化
const formatFileSize = (size: number | undefined) => {
	if (!size) return "";

	const units = ["B", "KB", "MB", "GB"];
	let unitIndex = 0;
	let fileSize = size;

	while (fileSize >= 1024 && unitIndex < units.length - 1) {
		fileSize /= 1024;
		unitIndex++;
	}

	return `${fileSize.toFixed(1)} ${units[unitIndex]}`;
};

// 下载单个文件
const downloadSingleFile = async (filename: string) => {
	try {
		downloadingFile.value = filename;
		const res = await getFileDownloadUrl(taskId as string, filename);
		if (res.data?.download_url) {
			// 创建隐藏的链接元素并触发下载
			const link = document.createElement("a");
			link.href = res.data.download_url;
			link.download = filename;
			link.target = "_blank";
			document.body.appendChild(link);
			link.click();
			document.body.removeChild(link);

			toast({
				title: "下载成功",
				description: `文件 ${filename} 开始下载`,
			});
		} else {
			throw new Error("获取下载链接失败");
		}
	} catch (error) {
		console.error("下载文件失败:", error);
		toast({
			title: "下载失败",
			description: `下载文件 ${filename} 时出现错误`,
			variant: "destructive",
		});
	} finally {
		downloadingFile.value = null;
	}
};

// 下载所有文件
const downloadAll = async () => {
	try {
		downloadingAll.value = true;
		const res = await getAllFilesDownloadUrl(taskId as string);
		if (res.data?.download_url) {
			// 创建隐藏的链接元素并触发下载
			const link = document.createElement("a");
			link.href = res.data.download_url;
			link.download = `task_${taskId}_files.zip`;
			link.target = "_blank";
			document.body.appendChild(link);
			link.click();
			document.body.removeChild(link);

			toast({
				title: "下载成功",
				description: "所有文件压缩包开始下载",
			});
		} else {
			throw new Error("获取下载链接失败");
		}
	} catch (error) {
		console.error("下载所有文件失败:", error);
		toast({
			title: "下载失败",
			description: "下载所有文件时出现错误",
			variant: "destructive",
		});
	} finally {
		downloadingAll.value = false;
	}
};

// 判断文件是否可预览
const isPreviewable = (fileName: string) => {
	const ext = fileName.split(".").pop()?.toLowerCase();
	const previewableExts = [
		"txt",
		"md",
		"json",
		"csv",
		"xml",
		"yml",
		"yaml",
		"py",
		"js",
		"ts",
		"vue",
		"html",
		"css",
		"log",
		"png",
		"jpg",
		"jpeg",
		"gif",
		"bmp",
		"webp",
		"svg", // 支持图片
	];
	return previewableExts.includes(ext || "");
};

// 预览文件
const previewFileContent = async (file: any) => {
	const fileName = file.name || file.filename || "";
	if (!isPreviewable(fileName)) {
		toast({
			title: "不支持预览",
			description: "该文件类型不支持在线预览",
			variant: "destructive",
		});
		return;
	}

	// 检查文件大小
	const fileSize = file.size || 0;
	const MAX_PREVIEW_SIZE = 5 * 1024 * 1024; // 5MB

	if (fileSize > MAX_PREVIEW_SIZE) {
		const confirmPreview = confirm(
			`文件较大 (${formatFileSize(fileSize)})，预览可能较慢。是否继续？`,
		);
		if (!confirmPreview) {
			return;
		}
	}

	try {
		loadingPreview.value = true;
		previewFile.value = file;
		previewVisible.value = true;
		previewContent.value = ""; // 清空之前的内容

		// 调用后端API获取文件内容
		const res = await getFileContent(taskId as string, fileName);

		if (res.data?.content !== undefined) {
			previewContent.value = res.data.content;

			// 保存图片信息到 previewFile
			if (res.data.is_image) {
				previewFile.value.is_image = true;
				previewFile.value.mime_type = res.data.mime_type;
			}

			// 如果内容被截断，显示提示
			if (res.data.truncated) {
				toast({
					title: "提示",
					description: "文件过大，仅显示部分内容",
					variant: "default",
				});
			}
		} else {
			throw new Error("获取文件内容失败");
		}
	} catch (error: any) {
		console.error("预览文件失败:", error);
		const errorMsg =
			error.response?.data?.detail || error.message || "未知错误";
		toast({
			title: "预览失败",
			description: `预览文件 ${fileName} 时出现错误: ${errorMsg}`,
			variant: "destructive",
		});
		previewVisible.value = false;
		previewContent.value = "";
	} finally {
		loadingPreview.value = false;
	}
};

// 过滤和排序后的文件列表
const filteredAndSortedFiles = computed(() => {
	let result = [...fileList.value];

	// 搜索过滤
	if (searchQuery.value) {
		const query = searchQuery.value.toLowerCase();
		result = result.filter((file) => {
			const fileName = (file.name || file.filename || "").toLowerCase();
			return fileName.includes(query);
		});
	}

	// 排序
	result.sort((a, b) => {
		let compareResult = 0;

		if (sortBy.value === "name") {
			const nameA = (a.name || a.filename || "").toLowerCase();
			const nameB = (b.name || b.filename || "").toLowerCase();
			compareResult = nameA.localeCompare(nameB);
		} else if (sortBy.value === "size") {
			compareResult = (a.size || 0) - (b.size || 0);
		} else if (sortBy.value === "time") {
			const timeA = new Date(a.modified_time || 0).getTime();
			const timeB = new Date(b.modified_time || 0).getTime();
			compareResult = timeA - timeB;
		}

		return sortOrder.value === "asc" ? compareResult : -compareResult;
	});

	return result;
});

// 切换排序顺序
const toggleSortOrder = () => {
	sortOrder.value = sortOrder.value === "asc" ? "desc" : "asc";
};

// 获取排序标签
const getSortLabel = () => {
	const labels = {
		name: "名称",
		size: "大小",
		time: "时间",
	};
	return labels[sortBy.value];
};

// 图片缩放控制
const zoomIn = () => {
	if (imageZoom.value < MAX_ZOOM) {
		imageZoom.value = Math.min(imageZoom.value + 10, MAX_ZOOM);
		// 放大超过100%时显示缩略图
		if (imageZoom.value > 100) {
			showThumbnail.value = true;
			// 应用边界限制
			setTimeout(() => {
				imagePosition.value = clampImagePosition(
					imagePosition.value.x,
					imagePosition.value.y,
				);
			}, 0);
		}
	}
};

const zoomOut = () => {
	if (imageZoom.value > MIN_ZOOM) {
		imageZoom.value = Math.max(imageZoom.value - 10, MIN_ZOOM);
		// 缩小到100%或以下时，重置位置并隐藏缩略图
		if (imageZoom.value <= 100) {
			imagePosition.value = { x: 0, y: 0 };
			showThumbnail.value = false;
		} else {
			// 应用边界限制
			setTimeout(() => {
				imagePosition.value = clampImagePosition(
					imagePosition.value.x,
					imagePosition.value.y,
				);
			}, 0);
		}
	}
};

const resetZoom = () => {
	imageZoom.value = 100;
	imagePosition.value = { x: 0, y: 0 };
	showThumbnail.value = false;
};

// 适应窗口大小
const fitToWindow = () => {
	if (!imageContainerRef.value || !imageRef.value) return;

	const container = imageContainerRef.value;
	const containerRect = container.getBoundingClientRect();
	const naturalWidth = imageNaturalSize.value.width;
	const naturalHeight = imageNaturalSize.value.height;

	if (naturalWidth === 0 || naturalHeight === 0) return;

	// 计算适应容器的缩放比例 (留出padding)
	const padding = 32; // 8px * 4 (p-4)
	const scaleX = (containerRect.width - padding) / naturalWidth;
	const scaleY = (containerRect.height - padding) / naturalHeight;
	const fitScale = Math.min(scaleX, scaleY, 1); // 不超过100%

	imageFitZoom.value = Math.round(fitScale * 100);
	imageZoom.value = imageFitZoom.value;
	imagePosition.value = { x: 0, y: 0 };
	showThumbnail.value = false;
};

// 实际大小 (100%)
const actualSize = () => {
	imageZoom.value = 100;
	imagePosition.value = { x: 0, y: 0 };
	showThumbnail.value = false;
};

// 双击重置到适应窗口
const handleDoubleClick = () => {
	if (imageZoom.value === imageFitZoom.value) {
		actualSize();
	} else {
		fitToWindow();
	}
};

// 图像加载完成后初始化
const handleImageLoad = () => {
	if (!imageRef.value) return;

	imageNaturalSize.value = {
		width: imageRef.value.naturalWidth,
		height: imageRef.value.naturalHeight,
	};

	// 默认适应窗口
	fitToWindow();
};

// 鼠标滚轮缩放
const handleWheel = (e: WheelEvent) => {
	// 图片预览区域直接响应滚轮进行缩放
	e.preventDefault();
	e.stopPropagation();

	if (e.deltaY < 0) {
		zoomIn();
	} else {
		zoomOut();
	}
};

// 计算拖动边界限制
const clampImagePosition = (x: number, y: number) => {
	if (!imageContainerRef.value || !imageRef.value || imageZoom.value <= 100) {
		return { x: 0, y: 0 };
	}

	const container = imageContainerRef.value;
	const img = imageRef.value;

	const containerRect = container.getBoundingClientRect();
	const imgRect = img.getBoundingClientRect();

	// 计算可拖动的最大范围
	const maxX = (imgRect.width - containerRect.width) / 2;
	const maxY = (imgRect.height - containerRect.height) / 2;

	// 限制拖动范围
	return {
		x: Math.max(-maxX, Math.min(maxX, x)),
		y: Math.max(-maxY, Math.min(maxY, y)),
	};
};

// 图片拖动处理
const handleMouseDown = (e: MouseEvent) => {
	if (imageZoom.value > 100) {
		isDragging.value = true;
		dragStart.value = {
			x: e.clientX - imagePosition.value.x,
			y: e.clientY - imagePosition.value.y,
		};
		e.preventDefault();
	}
};

const handleMouseMove = (e: MouseEvent) => {
	if (isDragging.value) {
		const newPosition = {
			x: e.clientX - dragStart.value.x,
			y: e.clientY - dragStart.value.y,
		};
		imagePosition.value = clampImagePosition(newPosition.x, newPosition.y);
	}
};

const handleMouseUp = () => {
	isDragging.value = false;
};

const handleMouseLeave = () => {
	isDragging.value = false;
};

// 缩略图拖动处理
const handleThumbnailMouseDown = (e: MouseEvent) => {
	isThumbnailDragging.value = true;
	thumbnailDragStart.value = {
		x: e.clientX,
		y: e.clientY,
	};
	e.preventDefault();
	e.stopPropagation();
};

const handleThumbnailMouseMove = (e: MouseEvent) => {
	if (!isThumbnailDragging.value || !imageContainerRef.value || !imageRef.value)
		return;

	const img = imageRef.value;

	// 计算图片的尺寸
	const imgRect = img.getBoundingClientRect();

	// 计算缩略图尺寸 (144px = w-36)
	const thumbnailSize = 144;

	// 计算鼠标在缩略图中移动的距离
	const deltaX = e.clientX - thumbnailDragStart.value.x;
	const deltaY = e.clientY - thumbnailDragStart.value.y;

	// 将缩略图中的移动距离转换为主图中的移动距离
	// 缩略图显示的是整个图片，所以移动比例是 (图片实际宽度 / 缩略图宽度)
	const scaleX = imgRect.width / thumbnailSize;
	const scaleY = imgRect.height / thumbnailSize;

	// 更新图片位置 (注意方向相反)
	const newPosition = {
		x: imagePosition.value.x - deltaX * scaleX,
		y: imagePosition.value.y - deltaY * scaleY,
	};
	imagePosition.value = clampImagePosition(newPosition.x, newPosition.y);

	// 更新拖动起点
	thumbnailDragStart.value = {
		x: e.clientX,
		y: e.clientY,
	};

	e.preventDefault();
	e.stopPropagation();
};

const handleThumbnailMouseUp = () => {
	isThumbnailDragging.value = false;
};

// 计算缩略图中可视区域的位置和大小
const getThumbnailViewportStyle = () => {
	if (!imageContainerRef.value || !imageRef.value) {
		return {
			width: "100%",
			height: "100%",
			left: "50%",
			top: "50%",
			transform: "translate(-50%, -50%)",
		};
	}

	const container = imageContainerRef.value;
	const img = imageRef.value;

	const containerRect = container.getBoundingClientRect();
	const imgRect = img.getBoundingClientRect();

	// 计算可视区域在整个图片中的比例
	const visibleWidthRatio = containerRect.width / imgRect.width;
	const visibleHeightRatio = containerRect.height / imgRect.height;

	// 可视区域在缩略图中的尺寸
	const viewportWidth = Math.min(100, visibleWidthRatio * 100);
	const viewportHeight = Math.min(100, visibleHeightRatio * 100);

	// 计算图片中心相对于容器中心的偏移
	const imgCenterX = imgRect.left + imgRect.width / 2;
	const imgCenterY = imgRect.top + imgRect.height / 2;
	const containerCenterX = containerRect.left + containerRect.width / 2;
	const containerCenterY = containerRect.top + containerRect.height / 2;

	// 偏移量
	const offsetX = containerCenterX - imgCenterX;
	const offsetY = containerCenterY - imgCenterY;

	// 转换为缩略图中的偏移百分比
	const thumbnailOffsetX = -(offsetX / imgRect.width) * 100;
	const thumbnailOffsetY = -(offsetY / imgRect.height) * 100;

	return {
		width: `${viewportWidth}%`,
		height: `${viewportHeight}%`,
		left: `${50 + thumbnailOffsetX}%`,
		top: `${50 + thumbnailOffsetY}%`,
		transform: "translate(-50%, -50%)",
	};
};

// 键盘快捷键
const handleKeydown = (e: KeyboardEvent) => {
	if (!previewVisible.value || !previewFile.value?.is_image) return;

	if (e.key === "+" || e.key === "=") {
		e.preventDefault();
		zoomIn();
	} else if (e.key === "-" || e.key === "_") {
		e.preventDefault();
		zoomOut();
	} else if (e.key === "0") {
		e.preventDefault();
		actualSize();
	} else if (e.key === "1") {
		e.preventDefault();
		fitToWindow();
	} else if (e.key === "r" || e.key === "R") {
		e.preventDefault();
		resetZoom();
	} else if (e.key === "Escape") {
		previewVisible.value = false;
	} else if (
		e.key === "ArrowLeft" ||
		e.key === "ArrowRight" ||
		e.key === "ArrowUp" ||
		e.key === "ArrowDown"
	) {
		if (imageZoom.value > 100) {
			e.preventDefault();
			const step = 50;
			const delta = {
				ArrowLeft: { x: step, y: 0 },
				ArrowRight: { x: -step, y: 0 },
				ArrowUp: { x: 0, y: step },
				ArrowDown: { x: 0, y: -step },
			}[e.key] || { x: 0, y: 0 };

			const newPosition = {
				x: imagePosition.value.x + delta.x,
				y: imagePosition.value.y + delta.y,
			};
			imagePosition.value = clampImagePosition(newPosition.x, newPosition.y);
		}
	}
};

// 监听预览对话框的打开/关闭，重置缩放
watch(previewVisible, (newValue) => {
	if (newValue) {
		resetZoom();
		// 添加键盘监听
		document.addEventListener("keydown", handleKeydown);
		// 显示快捷键提示，3秒后自动隐藏
		showKeyboardHelp.value = true;
		if (helpTimeout) clearTimeout(helpTimeout);
		helpTimeout = window.setTimeout(() => {
			showKeyboardHelp.value = false;
		}, 3000);
	} else {
		// 移除键盘监听
		document.removeEventListener("keydown", handleKeydown);
		if (helpTimeout) {
			clearTimeout(helpTimeout);
			helpTimeout = null;
		}
	}
});

onUnmounted(() => {
	document.removeEventListener("keydown", handleKeydown);
});
</script>

<template>
  <Sheet v-model:open="fileListVisible">
    <SheetTrigger asChild>
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger as-child>
            <Button @click="openFolder()" :disabled="loadingFiles" class="flex gap-2" size="icon">
              <RefreshCw v-if="loadingFiles" class="w-4 h-4 animate-spin" />
              <Files v-else class="w-4 h-4" />
              <Folder v-else class="w-4 h-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>工作区文件</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>

    </SheetTrigger>
    <SheetContent side="right" class="w-[400px] sm:w-[540px] flex flex-col">
      <SheetHeader class="space-y-3">
        <SheetTitle class="flex items-center justify-between mr-5">
          <span>工作区文件</span>
          <div class="flex items-center gap-1">
            <!-- 显示模式切换 -->
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger as-child>
                  <Button
                    @click="viewMode = viewMode === 'detailed' ? 'compact' : 'detailed'"
                    size="sm"
                    variant="ghost"
                    class="h-7 w-7 p-0"
                  >
                    <LayoutGrid v-if="viewMode === 'detailed'" class="w-4 h-4" />
                    <List v-else class="w-4 h-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{{ viewMode === 'detailed' ? '紧凑视图' : '详细视图' }}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>

            <!-- 下载所有文件 -->
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger as-child>
                  <Button
                    @click="downloadAll"
                    :disabled="downloadingAll || fileList.length === 0"
                    size="sm"
                    variant="ghost"
                    class="h-7 w-7 p-0"
                  >
                    <RefreshCw v-if="downloadingAll" class="w-4 h-4 animate-spin" />
                    <Archive v-else class="w-4 h-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>下载全部文件</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </SheetTitle>
        <SheetDescription>
          运行的结果和产生在<span class="font-mono">backend/project/work_dir/{{ taskId }}/*</span> 目录下
        </SheetDescription>

        <!-- 搜索和排序工具栏 -->
        <div class="flex gap-2 pt-2">
          <div class="relative flex-1">
            <Search class="absolute left-2.5 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <Input
              v-model="searchQuery"
              placeholder="搜索文件..."
              class="pl-8 h-9 text-sm"
            />
          </div>

          <!-- 排序下拉菜单 -->
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <Button size="sm" variant="outline" class="h-9 gap-1">
                <ArrowUpDown class="w-3.5 h-3.5" />
                <span class="text-sm">{{ getSortLabel() }}</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem @click="sortBy = 'name'">
                <span :class="sortBy === 'name' ? 'font-semibold' : ''">按名称</span>
              </DropdownMenuItem>
              <DropdownMenuItem @click="sortBy = 'size'">
                <span :class="sortBy === 'size' ? 'font-semibold' : ''">按大小</span>
              </DropdownMenuItem>
              <DropdownMenuItem @click="sortBy = 'time'">
                <span :class="sortBy === 'time' ? 'font-semibold' : ''">按时间</span>
              </DropdownMenuItem>
              <DropdownMenuItem @click="toggleSortOrder">
                <span>{{ sortOrder === 'asc' ? '升序 ↑' : '降序 ↓' }}</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </SheetHeader>

      <!-- 文件列表 -->
      <div class="flex-1 mt-4 overflow-hidden">
        <ScrollArea class="h-full">
          <div v-if="filteredAndSortedFiles.length === 0" class="text-center py-8 text-gray-500">
            {{ fileList.length === 0 ? '暂无文件' : '未找到匹配的文件' }}
          </div>
          <div v-else :class="viewMode === 'detailed' ? 'space-y-2' : 'space-y-1'">
            <!-- 详细视图 -->
            <template v-if="viewMode === 'detailed'">
              <div v-for="(file, index) in filteredAndSortedFiles" :key="index"
                class="flex items-center gap-3 p-3 rounded-lg border hover:bg-gray-50 transition-colors">
                <component :is="getFileIcon(file.name || file.filename || '')"
                  class="w-5 h-5 text-gray-600 flex-shrink-0" />
                <div class="flex-1 min-w-0">
                  <div class="font-medium text-sm truncate">
                    {{ file.name || file.filename || 'Unknown' }}
                  </div>
                  <div class="text-xs text-gray-500 flex gap-2">
                    <span v-if="file.size">{{ formatFileSize(file.size) }}</span>
                    <span v-if="file.modified_time">{{ new Date(file.modified_time).toLocaleDateString() }}</span>
                    <span v-if="file.type">{{ file.type }}</span>
                  </div>
                </div>
                <div class="flex gap-1 flex-shrink-0">
                  <!-- 预览按钮 -->
                  <TooltipProvider v-if="isPreviewable(file.name || file.filename || '')">
                    <Tooltip>
                      <TooltipTrigger as-child>
                        <Button
                          @click="previewFileContent(file)"
                          size="sm"
                          variant="ghost"
                          class="h-8 w-8 p-0"
                        >
                          <Eye class="w-4 h-4" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>预览文件</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>

                  <!-- 下载按钮 -->
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger as-child>
                        <Button
                          @click="downloadSingleFile(file.name || file.filename || '')"
                          :disabled="downloadingFile === (file.name || file.filename || '')"
                          size="sm"
                          variant="ghost"
                          class="h-8 w-8 p-0"
                        >
                          <RefreshCw v-if="downloadingFile === (file.name || file.filename || '')"
                            class="w-4 h-4 animate-spin" />
                          <Download v-else class="w-4 h-4" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>下载文件</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
              </div>
            </template>

            <!-- 紧凑视图 -->
            <template v-else>
              <div v-for="(file, index) in filteredAndSortedFiles" :key="index"
                class="flex items-center gap-2 px-2 py-1.5 rounded hover:bg-gray-50 transition-colors text-sm">
                <component :is="getFileIcon(file.name || file.filename || '')"
                  class="w-4 h-4 text-gray-600 flex-shrink-0" />
                <div class="flex-1 min-w-0 truncate">
                  {{ file.name || file.filename || 'Unknown' }}
                </div>
                <span v-if="file.size" class="text-xs text-gray-500 flex-shrink-0">
                  {{ formatFileSize(file.size) }}
                </span>
                <div class="flex gap-1 flex-shrink-0">
                  <Button
                    v-if="isPreviewable(file.name || file.filename || '')"
                    @click="previewFileContent(file)"
                    size="sm"
                    variant="ghost"
                    class="h-6 w-6 p-0"
                  >
                    <Eye class="w-3 h-3" />
                  </Button>
                  <Button
                    @click="downloadSingleFile(file.name || file.filename || '')"
                    :disabled="downloadingFile === (file.name || file.filename || '')"
                    size="sm"
                    variant="ghost"
                    class="h-6 w-6 p-0"
                  >
                    <RefreshCw v-if="downloadingFile === (file.name || file.filename || '')"
                      class="w-3 h-3 animate-spin" />
                    <Download v-else class="w-3 h-3" />
                  </Button>
                </div>
              </div>
            </template>
          </div>
        </ScrollArea>
      </div>
    </SheetContent>
  </Sheet>

  <!-- 文件预览对话框 -->
  <Dialog v-model:open="previewVisible">
    <DialogContent class="max-w-5xl max-h-[85vh] flex flex-col">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2">
          <component :is="getFileIcon(previewFile?.name || previewFile?.filename || '')"
            class="w-5 h-5 text-gray-600" />
          <span class="truncate max-w-md">{{ previewFile?.name || previewFile?.filename || 'Unknown' }}</span>
        </DialogTitle>
        <DialogDescription class="flex items-center justify-between">
          <div>
            文件预览 - {{ formatFileSize(previewFile?.size) }}
            <span v-if="previewContent && !previewFile?.is_image" class="ml-2 text-gray-500">
              ({{ previewContent.split('\n').length }} 行)
            </span>
            <span v-if="previewFile?.is_image && imageNaturalSize.width > 0" class="ml-2 text-gray-500">
              ({{ imageNaturalSize.width }} × {{ imageNaturalSize.height }} | {{ imageZoom }}%)
            </span>
          </div>
          <!-- 图片缩放控制 -->
          <div v-if="previewFile?.is_image" class="flex items-center gap-1">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger as-child>
                  <Button @click="fitToWindow" size="sm" variant="outline" class="h-7 px-2 text-xs">
                    适应
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>适应窗口 (1)</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger as-child>
                  <Button @click="actualSize" size="sm" variant="outline" class="h-7 px-2 text-xs">
                    100%
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>实际大小 (0)</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
            <div class="w-px h-5 bg-gray-300 mx-1"></div>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger as-child>
                  <Button @click="zoomOut" size="sm" variant="outline" class="h-7 w-7 p-0">
                    <span class="text-lg font-bold">-</span>
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>缩小 (-)</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger as-child>
                  <Button @click="resetZoom" size="sm" variant="outline" class="h-7 px-2 text-xs min-w-[3rem]">
                    {{ imageZoom }}%
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>重置 (R) | 双击图像可在适应/实际大小间切换</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger as-child>
                  <Button @click="zoomIn" size="sm" variant="outline" class="h-7 w-7 p-0">
                    <span class="text-lg font-bold">+</span>
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>放大 (+) | 滚轮也可缩放</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </DialogDescription>
      </DialogHeader>

      <div class="flex-1 overflow-hidden min-h-0">
        <!-- 图片预览使用独立容器，不使用ScrollArea以避免滚轮冲突 -->
        <div v-if="previewFile && previewFile.is_image && previewContent"
             class="h-full">
          <!-- 加载中 -->
          <div v-if="loadingPreview" class="flex items-center justify-center py-12 h-full">
            <RefreshCw class="w-8 h-8 animate-spin text-gray-400" />
          </div>

          <!-- 图片预览 -->
          <div v-else
               ref="imageContainerRef"
               class="relative flex items-center justify-center p-4 bg-gray-100 overflow-hidden h-full"
               @wheel.prevent="handleWheel"
               @mousemove="handleMouseMove"
               @mouseup="handleMouseUp"
               @mouseleave="handleMouseLeave">
            <img
              ref="imageRef"
              :src="`data:${previewFile.mime_type || 'image/png'};base64,${previewContent}`"
              :alt="previewFile?.name || previewFile?.filename"
              :style="{
                transform: imageZoom > 100
                  ? `translate(${imagePosition.x}px, ${imagePosition.y}px) scale(${imageZoom / 100})`
                  : `scale(${imageZoom / 100})`,
                transformOrigin: 'center',
                transition: isDragging ? 'none' : 'transform 0.2s ease',
                cursor: imageZoom > 100 ? (isDragging ? 'grabbing' : 'grab') : 'default',
                maxWidth: imageZoom <= 100 ? '100%' : 'none',
                maxHeight: imageZoom <= 100 ? '100%' : 'none',
                objectFit: 'contain'
              }"
              class="rounded-lg shadow-lg select-none"
              draggable="false"
              @mousedown="handleMouseDown"
              @dblclick="handleDoubleClick"
              @load="handleImageLoad"
            />

            <!-- 快捷键提示 -->
            <Transition
              enter-active-class="transition-all duration-300"
              enter-from-class="opacity-0 translate-y-2"
              enter-to-class="opacity-100 translate-y-0"
              leave-active-class="transition-all duration-300"
              leave-from-class="opacity-100 translate-y-0"
              leave-to-class="opacity-0 translate-y-2">
              <div v-show="showKeyboardHelp"
                   class="absolute top-4 right-4 bg-black bg-opacity-70 text-white text-xs rounded-lg p-2.5 z-10 max-w-xs backdrop-blur-sm">
                <div class="flex items-center justify-between mb-1.5">
                  <div class="font-semibold">快捷键</div>
                  <button @click="showKeyboardHelp = false"
                          class="text-white hover:text-gray-300 transition-colors ml-2"
                          aria-label="关闭">×</button>
                </div>
                <div class="space-y-0.5 text-[11px]">
                  <div><kbd class="bg-white bg-opacity-20 px-1 rounded">+/-</kbd> 缩放 | <kbd class="bg-white bg-opacity-20 px-1 rounded">滚轮</kbd> 缩放</div>
                  <div><kbd class="bg-white bg-opacity-20 px-1 rounded">0</kbd> 实际大小 | <kbd class="bg-white bg-opacity-20 px-1 rounded">1</kbd> 适应窗口</div>
                  <div><kbd class="bg-white bg-opacity-20 px-1 rounded">R</kbd> 重置 | <kbd class="bg-white bg-opacity-20 px-1 rounded">双击</kbd> 切换</div>
                  <div><kbd class="bg-white bg-opacity-20 px-1 rounded">方向键</kbd> 平移(放大时)</div>
                </div>
              </div>
            </Transition>

            <!-- 快捷键帮助按钮 -->
            <button v-show="!showKeyboardHelp"
                    @click="showKeyboardHelp = true"
                    class="absolute top-4 right-4 bg-black bg-opacity-50 hover:bg-opacity-70 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center z-10 transition-all"
                    aria-label="显示快捷键">？</button>

            <!-- 缩略图导航 -->
            <Transition
              enter-active-class="transition-all duration-200"
              enter-from-class="opacity-0 scale-90"
              enter-to-class="opacity-100 scale-100"
              leave-active-class="transition-all duration-200"
              leave-from-class="opacity-100 scale-100"
              leave-to-class="opacity-0 scale-90">
              <div v-show="showThumbnail && imageZoom > 100"
                   class="absolute bottom-4 left-4 bg-white border-2 rounded-lg shadow-xl p-1.5 z-10 select-none"
                   :class="isThumbnailDragging ? 'border-blue-500 shadow-2xl' : 'border-gray-300'"
                   @mousemove="handleThumbnailMouseMove"
                   @mouseup="handleThumbnailMouseUp"
                   @mouseleave="handleThumbnailMouseUp">
                <div class="relative w-36 h-36 overflow-hidden rounded bg-gray-50 transition-all"
                     :class="isThumbnailDragging ? 'cursor-grabbing' : 'cursor-grab'"
                     @mousedown="handleThumbnailMouseDown">
                  <img
                    :src="`data:${previewFile.mime_type || 'image/png'};base64,${previewContent}`"
                    :alt="previewFile?.name || previewFile?.filename"
                    class="w-full h-full object-contain pointer-events-none"
                  />
                  <!-- 可视区域指示器 -->
                  <div
                    class="absolute border-2 rounded-sm transition-colors"
                    :class="isThumbnailDragging ? 'border-blue-700 bg-blue-500 bg-opacity-30' : 'border-blue-600 bg-blue-400 bg-opacity-25'"
                    :style="getThumbnailViewportStyle()"
                    @mousedown.stop="handleThumbnailMouseDown">
                  </div>
                </div>
                <div class="text-xs text-center mt-1 font-medium"
                     :class="isThumbnailDragging ? 'text-blue-700' : 'text-gray-600'">
                  {{ imageZoom }}% · 拖动导航
                </div>
              </div>
            </Transition>
          </div>
        </div>

        <!-- 其他文件类型使用ScrollArea -->
        <ScrollArea v-else class="h-full">
          <!-- 加载中 -->
          <div v-if="loadingPreview" class="flex items-center justify-center py-12">
            <RefreshCw class="w-8 h-8 animate-spin text-gray-400" />
          </div>

          <!-- CSV 表格视图 -->
          <div v-else-if="getFileExtension(previewFile?.name || previewFile?.filename || '') === 'csv' && previewContent"
               class="p-4">
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg">
                <thead class="bg-gray-50">
                  <tr>
                    <th v-for="(header, index) in parseCSV(previewContent).headers"
                        :key="index"
                        class="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase tracking-wider border-b border-gray-200">
                      {{ header }}
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="(row, rowIndex) in parseCSV(previewContent).rows"
                      :key="rowIndex"
                      :class="rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'">
                    <td v-for="(cell, cellIndex) in row"
                        :key="cellIndex"
                        class="px-4 py-2 text-sm text-gray-900 border-b border-gray-200">
                      {{ cell }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- JSON 格式化视图 -->
          <div v-else-if="getFileExtension(previewFile?.name || previewFile?.filename || '') === 'json' && previewContent"
               class="p-4">
            <pre class="text-sm font-mono bg-gray-50 p-4 rounded-lg overflow-x-auto">{{
              (() => {
                try {
                  return JSON.stringify(JSON.parse(previewContent), null, 2)
                } catch {
                  return previewContent
                }
              })()
            }}</pre>
          </div>

          <!-- 普通文本视图 -->
          <pre v-else class="text-sm font-mono bg-gray-50 p-4 rounded-lg overflow-x-auto whitespace-pre-wrap break-words">{{ previewContent }}</pre>
        </ScrollArea>
      </div>

      <div class="flex justify-between items-center pt-4 border-t">
        <div class="text-xs text-gray-500">
          <span v-if="previewContent">
            字符数: {{ previewContent.length.toLocaleString() }}
          </span>
        </div>
        <div class="flex gap-2">
          <Button
            @click="downloadSingleFile(previewFile?.name || previewFile?.filename || '')"
            size="sm"
            class="gap-2"
          >
            <Download class="w-4 h-4" />
            下载文件
          </Button>
          <Button
            @click="previewVisible = false"
            size="sm"
            variant="outline"
          >
            关闭
          </Button>
        </div>
      </div>
    </DialogContent>
  </Dialog>
</template>
