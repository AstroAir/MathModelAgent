import { useToast } from '@/components/ui/toast';

export function useErrorHandler() {
  const { toast } = useToast();

  const handleError = (error: any, context: string) => {
    console.error(`[${context}]`, error);

    const message = error?.response?.data?.detail
      || error?.response?.data?.message
      || error?.message
      || '操作失败，请稍后重试';

    toast({
      title: context,
      description: message,
      variant: 'destructive',
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
