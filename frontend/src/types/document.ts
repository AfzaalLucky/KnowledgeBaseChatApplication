export type DocumentStatus = "pending" | "processing" | "completed" | "failed"

export interface KbDocument {
  id: number
  filename: string
  file_type: string | null
  file_size_bytes: number | null
  status: DocumentStatus
  chunk_count: number | null
  error_message: string | null
  uploaded_at: string
  updated_at: string | null
}

export interface DocumentUploadResponse {
  id: number
  filename: string
  status: DocumentStatus
}
