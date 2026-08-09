import { useCallback, useRef, useState } from "react"

import { streamMessage } from "@/api/chat"
import { ApiError } from "@/lib/api"
import type { ChatMessage } from "@/types/chat"

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const abortRef = useRef<AbortController | null>(null)

  const sendQuestion = useCallback(async (question: string) => {
    const trimmed = question.trim()
    if (!trimmed) return

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmed,
      status: "done",
    }
    const assistantId = crypto.randomUUID()
    const assistantMessage: ChatMessage = {
      id: assistantId,
      role: "assistant",
      content: "",
      status: "streaming",
    }

    setMessages((prev) => [...prev, userMessage, assistantMessage])

    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller

    let buffer = ""
    let flushScheduled = false
    const flush = () => {
      flushScheduled = false
      setMessages((prev) => prev.map((m) => (m.id === assistantId ? { ...m, content: buffer } : m)))
    }

    try {
      await streamMessage(
        trimmed,
        (token) => {
          buffer += token
          if (!flushScheduled) {
            flushScheduled = true
            requestAnimationFrame(flush)
          }
        },
        controller.signal,
      )
      flush()
      setMessages((prev) => prev.map((m) => (m.id === assistantId ? { ...m, status: "done" } : m)))
    } catch (err) {
      flush()
      if (err instanceof DOMException && err.name === "AbortError") return
      const message = err instanceof ApiError ? err.message : "Something went wrong. Please try again."
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId ? { ...m, content: m.content || message, status: "error" } : m,
        ),
      )
    }
  }, [])

  return { messages, sendQuestion }
}
