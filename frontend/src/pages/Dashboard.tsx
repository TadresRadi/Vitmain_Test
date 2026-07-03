import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { Button } from "@/components/ui/button"
import { Download } from "lucide-react"
import DashboardLayout from "@/components/DashboardLayout"
import { useTranslation } from "react-i18next"
import { getDashboardContent } from "@/services/dashboardService"
import type { GeneratedImage, GeneratedPost } from "@/types/api"

export default function Dashboard() {
  const { t } = useTranslation()

  const [postsLoading, setPostsLoading] = useState(true)
  const [imagesLoading, setImagesLoading] = useState(true)
  const [postsError, setPostsError] = useState<string | null>(null)
  const [imagesError, setImagesError] = useState<string | null>(null)
  const [posts, setPosts] = useState<GeneratedPost[]>([])
  const [images, setImages] = useState<GeneratedImage[]>([])

  useEffect(() => {
    let isMounted = true

    getDashboardContent()
      .then(({ posts, images }) => {
        if (!isMounted) return
        setPosts(posts)
        setImages(images)
        setPostsLoading(false)
        setImagesLoading(false)
        setPostsError(null)
        setImagesError(null)
      })
      .catch((err) => {
        if (!isMounted) return
        console.error("Failed to fetch dashboard content:", err)
        setPostsLoading(false)
        setImagesLoading(false)
        setPostsError(t("dashboard.fetchError"))
        setImagesError(t("dashboard.fetchError"))
      })

    return () => {
      isMounted = false
    }
  }, [t])

  const handleDownloadImage = async (imageUrl: string, imageId: string) => {
    try {
      const response = await fetch(imageUrl)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `vitmain-ai-image-${imageId}.png`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error("Failed to download image:", error)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString(undefined, {
      year: "numeric",
      month: "long",
      day: "numeric",
    })
  }

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString(undefined, {
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* AI Generated Posts Section */}
        <Card>
          <CardHeader>
            <CardTitle>{t("dashboard.aiGeneratedPosts")}</CardTitle>
            <CardDescription>
              {postsLoading ? t("common.loading") : t("dashboard.aiGeneratedPostsDesc")}
            </CardDescription>
          </CardHeader>

          <CardContent>
            {postsLoading ? (
              <div className="space-y-4">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="space-y-2">
                    <Skeleton className="h-4 w-32 rounded" />
                    <Skeleton className="h-20 w-full rounded" />
                  </div>
                ))}
              </div>
            ) : postsError ? (
              <div className="text-center py-8 text-destructive text-sm">
                {postsError}
              </div>
            ) : posts.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground text-sm">
                {t("dashboard.noPosts")}
              </div>
            ) : (
              <div className="space-y-4">
                {posts.map((post, idx) => (
                  <motion.div
                    key={post.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className="rounded-xl border p-4 space-y-2"
                  >
                    <div className="flex justify-between items-center text-sm text-muted-foreground">
                      <span>{formatDate(post.created_at)}</span>
                      <span>{formatTime(post.created_at)}</span>
                    </div>
                    <div className="whitespace-pre-wrap text-sm leading-relaxed">
                      {post.post_text}
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* AI Generated Images Section */}
        <Card>
          <CardHeader>
            <CardTitle>{t("dashboard.aiGeneratedImages")}</CardTitle>
            <CardDescription>
              {imagesLoading ? t("common.loading") : t("dashboard.aiGeneratedImagesDesc")}
            </CardDescription>
          </CardHeader>

          <CardContent>
            {imagesLoading ? (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {Array.from({ length: 8 }).map((_, i) => (
                  <Skeleton key={i} className="aspect-square rounded-lg" />
                ))}
              </div>
            ) : imagesError ? (
              <div className="text-center py-8 text-destructive text-sm">
                {imagesError}
              </div>
            ) : images.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground text-sm">
                {t("dashboard.noImages")}
              </div>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {images.map((image, idx) => (
                  <motion.div
                    key={image.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: idx * 0.05 }}
                    className="group relative rounded-lg overflow-hidden border aspect-square"
                  >
                    <img
                      src={image.image_url}
                      alt={t("dashboard.generatedImage")}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-2">
                      <span className="text-white text-xs px-2">
                        {formatDate(image.created_at)}
                      </span>
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => handleDownloadImage(image.image_url, image.id)}
                        className="flex items-center gap-2"
                      >
                        <Download className="h-4 w-4" />
                        {t("dashboard.downloadImage")}
                      </Button>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
