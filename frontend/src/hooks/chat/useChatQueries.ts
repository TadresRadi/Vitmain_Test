import { useQuery } from '@tanstack/react-query';
import api from '@/lib/axios';

export const useChatSession = () => {
  return useQuery({
    queryKey: ['chatSession'],
    queryFn: async () => {
      const res = await api.get('/chat/premium-posts');
      return res.data;
    },
    retry: 1,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useImagesHistory = () => {
  return useQuery({
    queryKey: ['imagesHistory'],
    queryFn: async () => {
      const res = await api.get('/images/history');
      return res.data;
    },
    retry: 1,
  });
};
