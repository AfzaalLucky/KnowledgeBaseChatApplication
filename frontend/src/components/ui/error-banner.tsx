import { AlertTriangleIcon, RotateCwIcon } from "lucide-react"

import { Button } from "@/components/ui/button"

interface ErrorBannerProps {
  message: string
  onRetry?: () => void
}

export function ErrorBanner({ message, onRetry }: ErrorBannerProps) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
      <div className="flex items-center gap-2">
        <AlertTriangleIcon className="size-4 shrink-0" />
        <span>{message}</span>
      </div>
      {onRetry ? (
        <Button variant="outline" size="sm" onClick={onRetry} className="shrink-0">
          <RotateCwIcon className="size-3.5" />
          Retry
        </Button>
      ) : null}
    </div>
  )
}
