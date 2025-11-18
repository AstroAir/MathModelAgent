import { useToast } from "@/components/ui/toast";

interface ErrorResponse {
	detail?: string;
	message?: string;
}

interface ApiError {
	response?: {
		data?: ErrorResponse;
	};
	message?: string;
}

export function useErrorHandler() {
	const { toast } = useToast();

	const handleError = (error: unknown, context: string) => {
		console.error(`[${context}]`, error);

		const apiError = error as ApiError;
		const message =
			apiError?.response?.data?.detail ||
			apiError?.response?.data?.message ||
			apiError?.message ||
			"操作失败，请稍后重试";

		toast({
			title: context,
			description: message,
			variant: "destructive",
		});
	};

	const handleSuccess = (title: string, description?: string) => {
		toast({
			title,
			description,
		});
	};

	return {
		handleError,
		handleSuccess,
	};
}
