import { useChat } from "@/hooks/useChat"
import { cn } from "@/lib/utils"

import { ChatInput } from "./ChatInput"
import { ChatMessageList } from "./ChatMessageList"

export function ChatWidget({ className }: { className?: string }) {
  const { messages, sendQuestion } = useChat()
  const isSending = messages.some((m) => m.status === "streaming")

  return (
    <div className={cn("flex min-h-0 flex-col", className)}>
      <ChatMessageList messages={messages} />
      <ChatInput onSend={sendQuestion} disabled={isSending} />
    </div>
  )
}
