<script setup lang="ts">
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import { FileText, Info, Wand2 } from "lucide-vue-next";

const modelValue = defineModel({
	type: Boolean,
	default: false,
});
</script>

<template>
  <Dialog :open="modelValue" @update:open="modelValue = $event">
    <DialogContent class="sm:max-w-[520px]">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2">
          <Info class="w-5 h-5 text-primary" />
          <span>更多说明</span>
        </DialogTitle>
        <DialogDescription class="text-xs text-muted-foreground">
          这里汇总了运行结果文件的位置，以及如何修改 Markdown 模板和提示词，方便你二次开发与调试。
        </DialogDescription>
      </DialogHeader>

      <div class="space-y-4 text-sm">
        <section class="p-3 rounded-lg border bg-muted/40 space-y-2">
          <h3 class="text-xs font-semibold text-muted-foreground flex items-center gap-1.5">
            <FileText class="w-4 h-4 text-primary" />
            <span>运行结果文件位置</span>
          </h3>
          <p class="text-xs text-muted-foreground">
            每次任务运行产生的结果会保存在以下目录：
          </p>
          <div class="mt-1 font-mono text-[11px] sm:text-xs">
            <div class="inline-flex items-center gap-1.5 bg-background/80 px-2 py-1 rounded border border-dashed border-border/60">
              <span>backend/project/work_dir/xxx/*</span>
            </div>
          </div>
          <ul class="list-disc list-inside space-y-1 mt-2 text-xs">
            <li>
              <code>notebook.ipynb</code>：保存运行过程中产生的代码和中间过程
            </li>
            <li>
              <code>res.md</code>：保存最终运行产生的结果（Markdown 格式，适合直接用于文档/论文）
            </li>
          </ul>
        </section>

        <section class="p-3 rounded-lg border bg-muted/40 space-y-2">
          <h3 class="text-xs font-semibold text-muted-foreground flex items-center gap-1.5">
            <Wand2 class="w-4 h-4 text-primary" />
            <span>修改 Markdown 模板</span>
          </h3>
          <p class="text-xs text-muted-foreground">
            想调整最终报告的排版或结构（例如章节标题、段落顺序），可以编辑以下模板文件：
          </p>
          <div class="font-mono text-[11px] sm:text-xs bg-background/80 px-2 py-1 rounded border border-dashed border-border/60">
            backend/app/config/md_template.toml
          </div>
        </section>

        <section class="p-3 rounded-lg border bg-muted/40 space-y-2">
          <h3 class="text-xs font-semibold text-muted-foreground flex items-center gap-1.5">
            <Wand2 class="w-4 h-4 text-primary" />
            <span>自定义提示词（prompts）</span>
          </h3>
          <p class="text-xs text-muted-foreground">
            如果你希望调整 Agent 的行为或输出风格，可以在这里修改系统提示词定义：
          </p>
          <div class="font-mono text-[11px] sm:text-xs bg-background/80 px-2 py-1 rounded border border-dashed border-border/60">
            backend/app/core/prompts.py
          </div>
        </section>

        <p class="text-[11px] text-muted-foreground text-right">
          提示：修改上述文件后，建议重新启动后端服务，以确保更新生效。
        </p>
      </div>
    </DialogContent>
  </Dialog>
</template>
