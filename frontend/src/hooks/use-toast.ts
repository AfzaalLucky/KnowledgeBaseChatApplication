import { useEffect, useState } from "react"

export type ToastVariant = "default" | "destructive" | "success"

export interface ToastItem {
  id: string
  title: string
  description?: string
  variant?: ToastVariant
}

type Listener = (toasts: ToastItem[]) => void

let toasts: ToastItem[] = []
const listeners = new Set<Listener>()

function emit() {
  for (const listener of listeners) listener(toasts)
}

function dismissToast(id: string) {
  toasts = toasts.filter((t) => t.id !== id)
  emit()
}

export function toast(item: Omit<ToastItem, "id">) {
  const id = crypto.randomUUID()
  toasts = [...toasts, { id, ...item }]
  emit()
  setTimeout(() => dismissToast(id), 5000)
  return id
}

export function useToast() {
  const [state, setState] = useState<ToastItem[]>(toasts)

  useEffect(() => {
    listeners.add(setState)
    return () => {
      listeners.delete(setState)
    }
  }, [])

  return { toasts: state, dismiss: dismissToast }
}
