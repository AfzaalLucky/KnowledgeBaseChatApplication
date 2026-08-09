import { useEffect, useRef } from "react"

import type { ChatMessage as ChatMessageType } from "@/types/chat"

import { ChatMessage } from "./ChatMessage"
import { TypingIndicator } from "./TypingIndicator"

export function ChatMessageList({ messages }: { messages: ChatMessageType[] }) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  return (
    <div className="flex-1 space-y-3 overflow-y-auto px-1 py-4">
      {messages.length === 0 ? (
        <p className="pt-12 text-center text-sm text-muted-foreground">
          Ask a question about your uploaded documents.
        </p>
      ) : (
        messages.map((message) =>
          message.role === "assistant" && message.status === "streaming" && !message.content ? (
            <TypingIndicator key={message.id} />
          ) : (
            <ChatMessage key={message.id} message={message} />
          ),
        )
      )}
      <div ref={bottomRef} />
    </div>
  )
}
