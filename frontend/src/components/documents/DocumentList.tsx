import { Trash2Icon } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { toast } from "@/hooks/use-toast"
import { useDeleteDocument } from "@/hooks/useDeleteDocument"
import { getErrorMessage } from "@/lib/errors"
import { formatBytes, formatDate } from "@/lib/format"
import type { KbDocument } from "@/types/document"

import { DocumentStatusBadge } from "./DocumentStatusBadge"

export function DocumentList({ documents }: { documents: KbDocument[] }) {
  const del = useDeleteDocument()

  const handleDelete = async (doc: KbDocument) => {
    if (!window.confirm(`Delete "${doc.filename}"? This cannot be undone.`)) return
    try {
      await del.mutateAsync(doc.id)
      toast({ title: "Document deleted", description: doc.filename })
    } catch (err) {
      toast({ title: "Delete failed", description: getErrorMessage(err), variant: "destructive" })
    }
  }

  return (
    <>
      <div className="hidden md:block">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Filename</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Size</TableHead>
              <TableHead>Uploaded</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Chunks</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {documents.map((doc) => (
              <TableRow key={doc.id}>
                <TableCell className="max-w-64 truncate font-medium">{doc.filename}</TableCell>
                <TableCell className="text-muted-foreground uppercase">{doc.file_type ?? "—"}</TableCell>
                <TableCell>{formatBytes(doc.file_size_bytes)}</TableCell>
                <TableCell>{formatDate(doc.uploaded_at)}</TableCell>
                <TableCell title={doc.error_message ?? undefined}>
                  <DocumentStatusBadge status={doc.status} />
                </TableCell>
                <TableCell>{doc.chunk_count ?? "—"}</TableCell>
                <TableCell className="text-right">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDelete(doc)}
                    aria-label={`Delete ${doc.filename}`}
                  >
                    <Trash2Icon className="size-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <div className="grid gap-3 md:hidden">
        {documents.map((doc) => (
          <div key={doc.id} className="rounded-lg border border-border p-4">
            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0">
                <p className="truncate font-medium">{doc.filename}</p>
                <p className="text-xs text-muted-foreground">
                  {doc.file_type?.toUpperCase()} · {formatBytes(doc.file_size_bytes)} · {formatDate(doc.uploaded_at)}
                </p>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => handleDelete(doc)}
                aria-label={`Delete ${doc.filename}`}
              >
                <Trash2Icon className="size-4" />
              </Button>
            </div>
            <div className="mt-3 flex items-center justify-between">
              <DocumentStatusBadge status={doc.status} />
              <span className="text-xs text-muted-foreground">{doc.chunk_count ?? "—"} chunks</span>
            </div>
            {doc.status === "failed" && doc.error_message ? (
              <p className="mt-2 text-xs text-destructive">{doc.error_message}</p>
            ) : null}
          </div>
        ))}
      </div>
    </>
  )
}
