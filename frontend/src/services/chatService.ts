import api from "@/lib/axios";
import type {
  AIPostGeneration,
  CompletePostReviewResponse,
  FeedbackPayload,
  GenerateImagesResponse,
  ImagesHistoryResponse,
  ImagesOnlyHistoryResponse,
  PostWithImage,
  PostsHistoryResponse,
  PremiumPostsResponse,
  RegeneratePostsResponse,
} from "@/types/api";

export async function getPremiumPosts(): Promise<PremiumPostsResponse> {
  const response = await api.get<PremiumPostsResponse>("/chat/premium-posts");
  return response.data;
}

export async function generatePremiumPosts(): Promise<PremiumPostsResponse> {
  const response = await api.post<PremiumPostsResponse>("/chat/premium-posts");
  return response.data;
}

export async function generateImages(postGenerationId: string): Promise<GenerateImagesResponse> {
  const response = await api.post<GenerateImagesResponse>("/chat/generate-images", {
    post_generation_id: postGenerationId,
  });
  return response.data;
}

export async function regenerateSelectedPosts(selectedIndexes: number[]): Promise<RegeneratePostsResponse> {
  const response = await api.post<RegeneratePostsResponse>("/chat/regenerate-selected-posts", {
    selected_indexes: selectedIndexes,
  });
  return response.data;
}

export async function completePostReview(): Promise<CompletePostReviewResponse> {
  const response = await api.post<CompletePostReviewResponse>("/chat/complete-post-review");
  return response.data;
}

export async function getImagesHistory(): Promise<ImagesHistoryResponse> {
  const response = await api.get<ImagesHistoryResponse>("/images/history");
  return response.data;
}

export async function getPostsHistory(): Promise<PostsHistoryResponse> {
  const response = await api.get<PostsHistoryResponse>("/posts/history");
  return response.data;
}

export async function getImagesOnlyHistory(): Promise<ImagesOnlyHistoryResponse> {
  const response = await api.get<ImagesOnlyHistoryResponse>("/images/only-history");
  return response.data;
}

export async function submitFeedback(payload: FeedbackPayload): Promise<void> {
  await api.post("/chat/feedback", payload);
}

export function mapLatestSessionImages(history: ImagesHistoryResponse): PostWithImage[] | null {
  const latestSession = history.sessions?.[0];
  if (!latestSession) return null;

  return latestSession.posts.map((post) => ({
    post_index: post.post_index,
    text: post.post_text,
    image_url: post.images?.[0]?.image_url ?? null,
  }));
}

export function shouldReviewPosts(postGeneration: AIPostGeneration): boolean {
  return !postGeneration.has_images && !postGeneration.posts_review_complete;
}
