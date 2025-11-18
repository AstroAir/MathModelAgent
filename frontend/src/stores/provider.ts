import { getAgentConfig, getAllStats, reloadConfig } from "@/apis/providerApi";
import { useToast } from "@/components/ui/toast/use-toast";
import { defineStore } from "pinia";
import { ref } from "vue";

const AGENT_NAMES = ["coordinator", "modeler", "coder", "writer"];

export const useProviderStore = defineStore("provider", () => {
	const { toast } = useToast();
	const agentSettings = ref<Record<string, unknown>>({});
	const agentStats = ref<Record<string, unknown>>({});
	const isLoading = ref(false);
	const isReloading = ref(false);

	async function fetchAllData() {
		isLoading.value = true;
		try {
			await Promise.all([fetchConfigs(), fetchStats()]);
		} catch (error) {
			toast({
				title: "Error fetching provider data",
				description: (error as Error).message,
				variant: "destructive",
			});
		} finally {
			isLoading.value = false;
		}
	}

	async function fetchConfigs() {
		const configPromises = AGENT_NAMES.map((name) => getAgentConfig(name));
		const results = await Promise.all(configPromises);
		const newSettings: Record<string, unknown> = {};
		AGENT_NAMES.forEach((name, index) => {
			newSettings[name] = results[index].data;
		});
		agentSettings.value = newSettings;
	}

	async function fetchStats() {
		try {
			const response = await getAllStats();
			agentStats.value = response.data;
		} catch (error) {
			console.error("Failed to fetch provider stats:", error);
		}
	}

	async function handleReloadConfig() {
		isReloading.value = true;
		try {
			const response = await reloadConfig();
			const message =
				(response.data as { message?: string } | undefined)?.message ||
				"Configuration reloaded successfully.";
			toast({
				title: "Success",
				description: message,
			});
			// Refresh data after reloading
			await fetchAllData();
		} catch (error) {
			toast({
				title: "Error reloading configuration",
				description: (error as Error).message,
				variant: "destructive",
			});
		} finally {
			isReloading.value = false;
		}
	}

	return {
		agentSettings,
		agentStats,
		isLoading,
		isReloading,
		fetchAllData,
		fetchStats,
		handleReloadConfig,
	};
});
