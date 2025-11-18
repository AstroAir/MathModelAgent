<script setup lang="ts">
import { Button } from "@/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { useProviderStore } from "@/stores/provider";
import { RefreshCw } from "lucide-vue-next";
import { storeToRefs } from "pinia";
import { computed, onMounted, onUnmounted } from "vue";
import ProviderCard from "./ProviderCard.vue";

const providerStore = useProviderStore();
const { agentSettings, agentStats, isLoading, isReloading } =
	storeToRefs(providerStore);

interface ProviderRateLimits {
	limits?: {
		rpm?: number;
		tpm?: number;
		rpd?: number;
	};
	current?: {
		rpm?: number;
		tpm?: number;
		rpd?: number;
		rpm_percentage?: number;
		tpm_percentage?: number;
		rpd_percentage?: number;
	};
}

interface ProviderConfig {
	name: string;
	model: string;
	priority?: number;
	healthy?: boolean;
	api_key_preview?: string;
	total_requests?: number;
	failure_count?: number;
	rate_limits?: ProviderRateLimits;
}

interface AgentConfig {
	rotation_strategy?: string;
	providers: ProviderConfig[];
}

interface AgentStats {
	providers: ProviderConfig[];
}

const typedAgentSettings = computed(() => {
	return agentSettings.value as Record<string, AgentConfig>;
});

const typedAgentStats = computed(() => {
	return agentStats.value as Record<string, AgentStats>;
});

let pollingInterval: number | undefined;

onMounted(() => {
	providerStore.fetchAllData();
	// Poll for stats every 30 seconds
	pollingInterval = window.setInterval(() => {
		providerStore.fetchStats();
	}, 30000);
});

onUnmounted(() => {
	if (pollingInterval) {
		clearInterval(pollingInterval);
	}
});

const getMergedProviders = (agentName: string) => {
	const config = typedAgentSettings.value[agentName];
	const stats = typedAgentStats.value[agentName];

	if (!config?.providers || !stats?.providers) {
		return [];
	}

	return config.providers.map((providerConfig) => {
		const providerStats = stats.providers.find(
			(ps) =>
				ps.name === providerConfig.name && ps.model === providerConfig.model,
		);
		return { ...providerConfig, ...providerStats };
	});
};

const agentNames = ["coordinator", "modeler", "coder", "writer"];
</script>

<template>
  <div>
    <Card>
      <CardHeader class="flex-row items-center justify-between">
        <div>
          <CardTitle>Provider Management</CardTitle>
          <CardDescription>
            Monitor and manage your LLM providers and API keys.
          </CardDescription>
        </div>
        <Button @click="providerStore.handleReloadConfig" :disabled="isReloading">
          <RefreshCw class="w-4 h-4 mr-2" :class="{ 'animate-spin': isReloading }" />
          Reload Config
        </Button>
      </CardHeader>
      <CardContent>
        <div v-if="isLoading" class="text-center py-8">
          <p>Loading provider settings...</p>
        </div>
        <div v-else class="space-y-8">
          <div v-for="agentName in agentNames" :key="agentName">
            <h3 class="text-lg font-semibold capitalize mb-4">{{ agentName }} Agent</h3>
            <div v-if="typedAgentSettings[agentName] && typedAgentSettings[agentName].providers.length > 0">
              <p class="text-sm text-muted-foreground mb-2">
                Rotation Strategy: <span class="font-medium">{{ typedAgentSettings[agentName].rotation_strategy }}</span>
              </p>
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <ProviderCard
                  v-for="provider in getMergedProviders(agentName)"
                  :key="provider.name"
                  :provider="provider"
                />
              </div>
            </div>
            <div v-else class="text-sm text-muted-foreground p-4 border rounded-lg">
              No providers configured for this agent.
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  </div>
</template>
