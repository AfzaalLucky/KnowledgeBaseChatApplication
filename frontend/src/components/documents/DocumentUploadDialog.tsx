import { zodResolver } from "@hookform/resolvers/zod"
import { UploadIcon } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { toast } from "@/hooks/use-toast"
import { useUploadDocument } from "@/hooks/useUploadDocument"
import { getErrorMessage } from "@/lib/errors"

const ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt"]
const MAX_UPLOAD_MB = 25

const uploadSchema = z.object({
  file: z
    .instanceof(FileList)
    .refine((list) => list.length === 1, "Choose a file to upload")
    .refine(
      (list) => ALLOWED_EXTENSIONS.some((ext) => list[0]?.name.toLowerCase().endsWith(ext)),
      `Only ${ALLOWED_EXTENSIONS.join(", ")} files are supported`,
    )
    .refine(
      (list) => (list[0]?.size ?? 0) <= MAX_UPLOAD_MB * 1024 * 1024,
      `File exceeds ${MAX_UPLOAD_MB}MB limit`,
    ),
})

type UploadForm = z.infer<typeof uploadSchema>

export function DocumentUploadDialog() {
  const [open, setOpen] = useState(false)
  const upload = useUploadDocument()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<UploadForm>({ resolver: zodResolver(uploadSchema) })

  const onSubmit = async (data: UploadForm) => {
    const file = data.file[0]
    try {
      await upload.mutateAsync(file)
      toast({
        title: "Upload started",
        description: `${file.name} is being processed.`,
        variant: "success",
      })
      reset()
      setOpen(false)
    } catch (err) {
      toast({ title: "Upload failed", description: getErrorMessage(err), variant: "destructive" })
    }
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        setOpen(next)
        if (!next) reset()
      }}
    >
      <DialogTrigger asChild>
        <Button>
          <UploadIcon className="size-4" />
          Upload document
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Upload a document</DialogTitle>
          <DialogDescription>PDF, DOCX, or TXT — up to {MAX_UPLOAD_MB}MB.</DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
          <input
            type="file"
            accept={ALLOWED_EXTENSIONS.join(",")}
            {...register("file")}
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm file:mr-3 file:rounded-md file:border-0 file:bg-secondary file:px-3 file:py-1.5 file:text-sm file:font-medium"
          />
          {errors.file ? <p className="text-sm text-destructive">{errors.file.message}</p> : null}
          <DialogFooter>
            <Button type="submit" disabled={upload.isPending}>
              {upload.isPending ? "Uploading…" : "Upload"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
