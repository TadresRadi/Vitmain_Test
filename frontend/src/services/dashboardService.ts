import { getImagesOnlyHistory, getPostsHistory } from '@/services/chatService'
import type { GeneratedImage, GeneratedPost } from '@/types/api'

export interface DashboardContent {
  posts: GeneratedPost[]
  images: GeneratedImage[]
}

export async function getDashboardContent(): Promise<DashboardContent> {
  const [postsHistory, imagesHistory] = await Promise.all([
    getPostsHistory(),
    getImagesOnlyHistory(),
  ])

  return {
    posts: postsHistory.posts ?? [],
    images: imagesHistory.images ?? [],
  }
}
