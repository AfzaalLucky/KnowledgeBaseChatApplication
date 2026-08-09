import * as ToastPrimitive from "@radix-ui/react-toast"
import { type VariantProps, cva } from "class-variance-authority"
import { XIcon } from "lucide-react"
import type { ComponentProps } from "react"

import { cn } from "@/lib/utils"

const ToastProvider = ToastPrimitive.Provider

function ToastViewport({ className, ...props }: ComponentProps<typeof ToastPrimitive.Viewport>) {
  return (
    <ToastPrimitive.Viewport
      className={cn(
        "fixed bottom-0 right-0 z-100 flex max-h-screen w-full flex-col gap-2 p-4 sm:max-w-sm",
        className,
      )}
      {...props}
    />
  )
}

const toastVariants = cva(
  "group relative flex w-full items-start justify-between gap-3 overflow-hidden rounded-lg border p-4 shadow-lg data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-80 data-[state=open]:slide-in-from-bottom-2",
  {
    variants: {
      variant: {
        default: "border-border bg-card text-card-foreground",
        destructive: "border-destructive/40 bg-destructive/10 text-destructive",
        success: "border-success/40 bg-success/10 text-success",
      },
    },
    defaultVariants: { variant: "default" },
  },
)

function Toast({
  className,
  variant,
  ...props
}: ComponentProps<typeof ToastPrimitive.Root> & VariantProps<typeof toastVariants>) {
  return <ToastPrimitive.Root className={cn(toastVariants({ variant, className }))} {...props} />
}

function ToastTitle({ className, ...props }: ComponentProps<typeof ToastPrimitive.Title>) {
  return <ToastPrimitive.Title className={cn("text-sm font-semibold", className)} {...props} />
}

function ToastDescription({ className, ...props }: ComponentProps<typeof ToastPrimitive.Description>) {
  return <ToastPrimitive.Description className={cn("text-sm opacity-90", className)} {...props} />
}

function ToastClose({ className, ...props }: ComponentProps<typeof ToastPrimitive.Close>) {
  return (
    <ToastPrimitive.Close
      className={cn("absolute top-2 right-2 rounded-md p-1 opacity-70 transition-opacity hover:opacity-100", className)}
      {...props}
    >
      <XIcon className="size-4" />
    </ToastPrimitive.Close>
  )
}

export { ToastProvider, ToastViewport, Toast, ToastTitle, ToastDescription, ToastClose }
