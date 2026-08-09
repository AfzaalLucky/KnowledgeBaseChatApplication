import { apiFetch } from "@/lib/api"
import type { DocumentUploadResponse, KbDocument } from "@/types/document"

export function listDocuments(search?: string): Promise<KbDocument[]> {
  const query = search ? `?search=${encodeURIComponent(search)}` : ""
  return apiFetch<KbDocument[]>(`/api/documents${query}`)
}

export function getDocument(id: number): Promise<KbDocument> {
  return apiFetch<KbDocument>(`/api/documents/${id}`)
}

export function uploadDocument(file: File): Promise<DocumentUploadResponse> {
  const formData = new FormData()
  formData.append("file", file)
  return apiFetch<DocumentUploadResponse>("/api/documents", {
    method: "POST",
    body: formData,
  })
}

export function deleteDocument(id: number): Promise<void> {
  return apiFetch<void>(`/api/documents/${id}`, { method: "DELETE" })
}
