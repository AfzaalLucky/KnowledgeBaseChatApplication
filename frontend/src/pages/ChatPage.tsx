import { ChatWidget } from "@/components/chat/ChatWidget"

export function ChatPage() {
  return (
    <div className="flex h-[calc(100dvh-9rem)] flex-col md:h-[calc(100dvh-7rem)]">
      <ChatWidget className="flex-1" />
    </div>
  )
}
