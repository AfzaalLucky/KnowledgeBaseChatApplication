import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

import { cn } from "@/lib/utils"
import type { ChatMessage as ChatMessageType } from "@/types/chat"

export function ChatMessage({ message }: { message: ChatMessageType }) {
  const isUser = message.role === "user"

  return (
    <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[80%] rounded-2xl px-4 py-2.5 text-sm",
          isUser ? "bg-primary text-primary-foreground whitespace-pre-wrap" : "bg-muted text-foreground",
          message.status === "error" && "border border-destructive/40 text-destructive",
        )}
      >
        {isUser ? (
          message.content
        ) : (
          <div
            className={cn(
              "prose prose-sm dark:prose-invert max-w-none break-words",
              "prose-p:my-1.5 first:prose-p:mt-0 last:prose-p:mb-0",
              "prose-headings:my-2 prose-ul:my-1.5 prose-ol:my-1.5 prose-li:my-0.5",
              "prose-pre:my-2 prose-pre:bg-background/60 prose-code:before:content-none prose-code:after:content-none",
              "prose-code:rounded prose-code:bg-background/60 prose-code:px-1 prose-code:py-0.5",
              "prose-blockquote:my-2 prose-a:text-primary",
            )}
          >
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  )
}
