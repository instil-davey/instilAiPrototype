import { AlertCircle, Inbox } from "lucide-react"

interface EmptyStateProps {
  title: string
  description: string
  icon?: "inbox" | "alert"
}

export function EmptyState({
  title,
  description,
  icon = "inbox",
}: EmptyStateProps) {
  const Icon = icon === "inbox" ? Inbox : AlertCircle

  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center animate-fade-in">
      <div className="rounded-full bg-muted p-6 mb-4">
        <Icon className="h-12 w-12 text-muted-foreground" />
      </div>
      <h3 className="text-lg font-semibold text-foreground mb-2">{title}</h3>
      <p className="text-sm text-muted-foreground max-w-md">{description}</p>
    </div>
  )
}
