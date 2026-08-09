import { SendIcon } from "lucide-react"
import { useState } from "react"
import type { FormEvent, KeyboardEvent } from "react"

import { Button } from "@/components/ui/button"

const MAX_LENGTH = 2000

interface ChatInputProps {
  onSend: (question: string) => void
  disabled?: boolean
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState("")

  const submit = (e?: FormEvent) => {
    e?.preventDefault()
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setValue("")
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <form onSubmit={submit} className="flex items-end gap-2 border-t border-border pt-3">
      <div className="flex-1">
        <textarea
          value={value}
          onChange={(e) => setValue(e.target.value.slice(0, MAX_LENGTH))}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question..."
          rows={1}
          disabled={disabled}
          className="w-full resize-none rounded-md border border-input bg-background px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-50"
        />
        <p className="mt-1 text-right text-xs text-muted-foreground">
          {value.length}/{MAX_LENGTH}
        </p>
      </div>
      <Button type="submit" size="icon" disabled={disabled || !value.trim()} aria-label="Send message">
        <SendIcon className="size-4" />
      </Button>
    </form>
  )
}
