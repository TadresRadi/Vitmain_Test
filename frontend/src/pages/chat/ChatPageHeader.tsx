import { Sparkles } from "lucide-react"
import { useTranslation } from "react-i18next"

export function ChatPageHeader() {
  const { t } = useTranslation()

  return (
    <div className="glass-dark border-b border-white/10 p-4 bg-black/40 backdrop-blur-md">
      <div className="max-w-7xl mx-auto flex items-center">
        <div className="flex items-center gap-3">
          <div>
            <h1 className="text-xl font-bold text-white flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-vitamin-base animate-pulse" />
              {t("chat.title", "Vitamin AI Premium Marketing Strategist")}
            </h1>
            <p className="text-xs text-white/50">
              {t("chat.activeAssistance", "Formulate high-conversion copy campaigns")}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
