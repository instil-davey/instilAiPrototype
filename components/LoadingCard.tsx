import { cn } from "@/lib/utils"

interface LoadingCardProps {
  delay?: number
}

export function LoadingCard({ delay = 0 }: LoadingCardProps) {
  return (
    <div
      className={cn(
        "rounded-xl border bg-card p-6 animate-fade-in opacity-0"
      )}
      style={{
        animationDelay: `${delay}ms`,
        animationFillMode: "forwards",
      }}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="h-10 w-10 rounded-lg bg-muted animate-pulse" />
        <div className="h-6 w-16 rounded-full bg-muted animate-pulse" />
      </div>
      <div className="space-y-3">
        <div className="h-8 w-24 bg-muted animate-pulse rounded" />
        <div className="h-4 w-32 bg-muted animate-pulse rounded" />
        <div className="h-3 w-full bg-muted animate-pulse rounded" />
      </div>
    </div>
  )
}

export function LoadingSegmentCard({ delay = 0 }: LoadingCardProps) {
  return (
    <div
      className={cn(
        "rounded-xl border bg-card p-6 animate-fade-in opacity-0"
      )}
      style={{
        animationDelay: `${delay}ms`,
        animationFillMode: "forwards",
      }}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="h-10 w-10 rounded-lg bg-muted animate-pulse" />
        <div className="text-right">
          <div className="h-7 w-16 bg-muted animate-pulse rounded mb-1" />
          <div className="h-3 w-20 bg-muted animate-pulse rounded" />
        </div>
      </div>
      <div className="mb-4 space-y-2">
        <div className="h-5 w-32 bg-muted animate-pulse rounded" />
        <div className="h-4 w-full bg-muted animate-pulse rounded" />
      </div>
      <div className="grid grid-cols-2 gap-3 pt-4 border-t border-border/50">
        <div className="space-y-2">
          <div className="h-3 w-20 bg-muted animate-pulse rounded" />
          <div className="h-5 w-24 bg-muted animate-pulse rounded" />
        </div>
        <div className="space-y-2">
          <div className="h-3 w-20 bg-muted animate-pulse rounded" />
          <div className="h-5 w-24 bg-muted animate-pulse rounded" />
        </div>
      </div>
    </div>
  )
}
