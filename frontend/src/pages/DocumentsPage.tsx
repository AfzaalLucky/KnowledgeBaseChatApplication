import { useState } from "react"

import { DocumentList } from "@/components/documents/DocumentList"
import { DocumentSearchBar } from "@/components/documents/DocumentSearchBar"
import { DocumentUploadDialog } from "@/components/documents/DocumentUploadDialog"
import { ErrorBanner } from "@/components/ui/error-banner"
import { Skeleton } from "@/components/ui/skeleton"
import { useDocuments } from "@/hooks/useDocuments"
import { getErrorMessage } from "@/lib/errors"

export function DocumentsPage() {
  const [search, setSearch] = useState("")
  const { data, isLoading, isError, error, refetch } = useDocuments(search)

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-semibold">Documents</h1>
          <p className="text-sm text-muted-foreground">Upload and manage your knowledge base.</p>
        </div>
        <DocumentUploadDialog />
      </div>

      <DocumentSearchBar value={search} onChange={setSearch} />

      {isError ? (
        <ErrorBanner message={getErrorMessage(error)} onRetry={refetch} />
      ) : isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      ) : data && data.length > 0 ? (
        <DocumentList documents={data} />
      ) : (
        <div className="flex flex-col items-center gap-3 rounded-lg border border-dashed border-border py-16 text-center">
          <p className="text-muted-foreground">No documents yet — upload one to get started.</p>
          <DocumentUploadDialog />
        </div>
      )}
    </div>
  )
}
