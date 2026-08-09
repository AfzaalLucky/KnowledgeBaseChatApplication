export type ChatRole = "user" | "assistant"
export type MessageStatus = "sending" | "streaming" | "done" | "error"

export interface SourceChunk {
  document: string
  page: number
  text: string
}

export interface ChatMessage {
  id: string
  role: ChatRole
  content: string
  sources?: SourceChunk[]
  status: MessageStatus
}
