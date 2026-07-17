import { useQuery } from '@tanstack/react-query'
import api from '@/lib/axios'

export const useFeaturedProjects = () => {
  return useQuery({
    queryKey: ['featuredProjects'],
    queryFn: async () => {
      const response = await api.get('/portfolio/featured-projects/')
      return response.data
    },
  })
}

export const useBrands = () => {
  return useQuery({
    queryKey: ['brands'],
    queryFn: async () => {
      const response = await api.get('/portfolio/brands/')
      return response.data
    },
  })
}

export const useTeslaClientImages = () => {
  return useQuery({
    queryKey: ['teslaClientImages'],
    queryFn: async () => {
      const response = await api.get('/portfolio/tesla-client-images/')
      return response.data
    },
  })
}
