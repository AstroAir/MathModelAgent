<script setup lang="ts">
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
	Tooltip,
	TooltipContent,
	TooltipProvider,
	TooltipTrigger,
} from "@/components/ui/tooltip";
import { CheckCircle, XCircle } from "lucide-vue-next";
import { computed } from "vue";

interface Provider {
	name: string;
	model?: string;
	priority?: number;
	healthy?: boolean;
	response_time?: number;
	uptime?: number;
	error_rate?: number;
	total_requests?: number;
	failure_count?: number;
	api_key_preview?: string;
	rate_limits?: {
		limits?: {
			rpm?: number;
			rpd?: number;
			tpm?: number;
			tpd?: number;
		};
		current?: {
			rpm?: number;
			rpd?: number;
			tpm?: number;
			tpd?: number;
			rpm_percentage?: number;
			rpd_percentage?: number;
			tpm_percentage?: number;
			tpd_percentage?: number;
		};
	};
}

const props = defineProps<{ provider: Provider }>();

const healthStatus = computed(() => {
	if (props.provider.healthy) {
		return { text: "Healthy", color: "bg-green-500", icon: CheckCircle };
	}
	return { text: "Unhealthy", color: "bg-red-500", icon: XCircle };
});

const formatPercentage = (value: number | undefined) => {
	if (value === null || value === undefined) return "N/A";
	return `${value.toFixed(1)}%`;
};
</script>

<template>
  <div class="p-4 border rounded-lg bg-card text-card-foreground shadow-sm">
    <div class="flex justify-between items-start mb-3">
      <div>
        <h4 class="font-semibold">{{ provider.name }}</h4>
        <p class="text-sm text-muted-foreground">{{ provider.model }}</p>
        <p class="text-xs text-muted-foreground">Priority: {{ provider.priority }}</p>
      </div>
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger>
            <Badge :class="healthStatus.color" class="text-white">
              <component :is="healthStatus.icon" class="h-3 w-3 mr-1" />
              {{ healthStatus.text }}
            </Badge>
          </TooltipTrigger>
          <TooltipContent>
            <p>Total Requests: {{ provider.total_requests }}</p>
            <p>Failures: {{ provider.failure_count }}</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    </div>

    <div class="space-y-3">
      <!-- RPM -->
      <div v-if="provider.rate_limits?.limits?.rpm">
        <div class="flex justify-between text-xs mb-1">
          <span class="font-medium">RPM</span>
          <span class="text-muted-foreground">
            {{ provider.rate_limits?.current?.rpm ?? 0 }} /
            {{ provider.rate_limits?.limits?.rpm }}
            ({{ formatPercentage(provider.rate_limits?.current?.rpm_percentage) }})
          </span>
        </div>
        <Progress :model-value="provider.rate_limits?.current?.rpm_percentage ?? 0" class="h-2" />
      </div>

      <!-- TPM -->
      <div v-if="provider.rate_limits?.limits?.tpm">
        <div class="flex justify-between text-xs mb-1">
          <span class="font-medium">TPM</span>
          <span class="text-muted-foreground">
            {{ provider.rate_limits?.current?.tpm ?? 0 }} /
            {{ provider.rate_limits?.limits?.tpm }}
            ({{ formatPercentage(provider.rate_limits?.current?.tpm_percentage) }})
          </span>
        </div>
        <Progress :model-value="provider.rate_limits?.current?.tpm_percentage ?? 0" class="h-2" />
      </div>

      <!-- RPD -->
      <div v-if="provider.rate_limits?.limits?.rpd">
        <div class="flex justify-between text-xs mb-1">
          <span class="font-medium">RPD</span>
          <span class="text-muted-foreground">
            {{ provider.rate_limits?.current?.rpd ?? 0 }} /
            {{ provider.rate_limits?.limits?.rpd }}
            ({{ formatPercentage(provider.rate_limits?.current?.rpd_percentage) }})
          </span>
        </div>
        <Progress :model-value="provider.rate_limits?.current?.rpd_percentage ?? 0" class="h-2" />
      </div>
    </div>

    <div class="mt-4 text-xs text-muted-foreground">
      <p>API Key: {{ provider.api_key_preview }}</p>
    </div>
  </div>
</template>
