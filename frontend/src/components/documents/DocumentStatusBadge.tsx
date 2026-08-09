import { Badge } from "@/components/ui/badge"
import { Spinner } from "@/components/ui/spinner"
import type { DocumentStatus } from "@/types/document"

const VARIANTS: Record<DocumentStatus, "secondary" | "warning" | "success" | "destructive"> = {
  pending: "secondary",
  processing: "warning",
  completed: "success",
  failed: "destructive",
}

export function DocumentStatusBadge({ status }: { status: DocumentStatus }) {
  return (
    <Badge variant={VARIANTS[status]}>
      {status === "processing" ? <Spinner className="size-3" /> : null}
      {status}
    </Badge>
  )
}
