import request from "@/utils/request";

/**
 * Fetches the configuration for a specific agent.
 * @param agentName - The name of the agent (e.g., 'modeler', 'coder').
 * @returns A promise that resolves to the agent's configuration.
 */
export const getAgentConfig = (agentName: string) => {
	return request.get(`/api/rate-limit/config/${agentName}`);
};

/**
 * Fetches the rate limit statistics for all agents.
 * @returns A promise that resolves to the statistics for all agents.
 */
export const getAllStats = () => {
	return request.get("/api/rate-limit/stats");
};

/**
 * Reloads the configuration on the backend.
 * @returns A promise that resolves when the configuration has been reloaded.
 */
export const reloadConfig = () => {
	return request.post("/api/rate-limit/reload-config");
};
