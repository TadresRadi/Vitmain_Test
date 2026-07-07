import { useQuery } from '@tanstack/react-query';
import api from '@/lib/axios';

/**
 * Normalize paginated vs non-paginated API payload into array.
 */
function normalizeListPayload(payload: any): any[] {
  if (Array.isArray(payload)) return payload;
  if (payload && Array.isArray(payload.results)) return payload.results;
  return [];
}

export const useFeaturedProjects = () => {
  return useQuery({
    queryKey: ['featuredProjects'],
    queryFn: async () => {
      const response = await api.get('/portfolio/featured-projects/');
      return normalizeListPayload(response.data);
    },
    staleTime: 1000 * 60,
  });
};

export const useBrands = () => {
  return useQuery({
    queryKey: ['brands'],
    queryFn: async () => {
      const response = await api.get('/portfolio/brands/');
      return normalizeListPayload(response.data);
    },
    staleTime: 1000 * 60,
  });
};

export const useTeslaClientImages = () => {
  return useQuery({
    queryKey: ['teslaClientImages'],
    queryFn: async () => {
      const response = await api.get('/portfolio/tesla-client-images/');
      return normalizeListPayload(response.data);
    },
    staleTime: 1000 * 60,
  });
};