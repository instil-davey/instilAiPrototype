"use client"

import { Users, TrendingUp } from "lucide-react"
import { cn } from "@/lib/utils"
import Link from "next/link"

export interface SegmentCardProps {
  id: string
  name: string
  count: number
  totalGiving: number
  avgGiving: number
  description: string
  color: string
  delay?: number
}

export function SegmentCard({
  id,
  name,
  count,
  totalGiving,
  avgGiving,
  description,
  color,
  delay = 0,
}: SegmentCardProps) {
  const colorVariants: Record<string, string> = {
    blue: "from-blue-500/10 to-blue-500/5 border-blue-200 hover:border-blue-300 hover:shadow-blue-100",
    purple:
      "from-purple-500/10 to-purple-500/5 border-purple-200 hover:border-purple-300 hover:shadow-purple-100",
    green:
      "from-green-500/10 to-green-500/5 border-green-200 hover:border-green-300 hover:shadow-green-100",
    amber:
      "from-amber-500/10 to-amber-500/5 border-amber-200 hover:border-amber-300 hover:shadow-amber-100",
    slate:
      "from-slate-500/10 to-slate-500/5 border-slate-200 hover:border-slate-300 hover:shadow-slate-100",
    gray: "from-gray-500/10 to-gray-500/5 border-gray-200 hover:border-gray-300 hover:shadow-gray-100",
  }

  const iconColorVariants: Record<string, string> = {
    blue: "bg-blue-100 text-blue-600",
    purple: "bg-purple-100 text-purple-600",
    green: "bg-green-100 text-green-600",
    amber: "bg-amber-100 text-amber-600",
    slate: "bg-slate-100 text-slate-600",
    gray: "bg-gray-100 text-gray-600",
  }

  return (
    <Link href={`/dashboard/segments/${id}`} className="block">
      <div
        className={cn(
          "group relative overflow-hidden rounded-xl border bg-gradient-to-br p-6",
          "transition-all duration-300 ease-out hover:shadow-lg hover:scale-[1.02]",
          "cursor-pointer animate-slide-in opacity-0",
          colorVariants[color] || colorVariants.gray
        )}
        style={{
          animationDelay: `${delay}ms`,
          animationFillMode: "forwards",
        }}
      >
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div
            className={cn(
              "rounded-lg p-2.5 transition-all duration-300",
              iconColorVariants[color] || iconColorVariants.gray,
              "group-hover:scale-110"
            )}
          >
            <Users className="h-5 w-5" />
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-foreground">{count}</div>
            <div className="text-xs text-muted-foreground">constituents</div>
          </div>
        </div>

        {/* Title and description */}
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-foreground mb-1 group-hover:text-primary transition-colors duration-300">
            {name}
          </h3>
          <p className="text-sm text-muted-foreground line-clamp-2">
            {description}
          </p>
        </div>

        {/* Stats grid */}
        <div className="grid grid-cols-2 gap-3 pt-4 border-t border-border/50">
          <div>
            <div className="flex items-center gap-1 text-xs text-muted-foreground mb-1">
              <TrendingUp className="h-3 w-3" />
              <span>Total Giving</span>
            </div>
            <div className="text-base font-semibold text-foreground">
              $
              {totalGiving.toLocaleString(undefined, {
                minimumFractionDigits: 0,
                maximumFractionDigits: 0,
              })}
            </div>
          </div>
          <div>
            <div className="flex items-center gap-1 text-xs text-muted-foreground mb-1">
              <TrendingUp className="h-3 w-3" />
              <span>Avg per Person</span>
            </div>
            <div className="text-base font-semibold text-foreground">
              $
              {avgGiving.toLocaleString(undefined, {
                minimumFractionDigits: 0,
                maximumFractionDigits: 0,
              })}
            </div>
          </div>
        </div>

        {/* Hover arrow indicator */}
        <div className="absolute bottom-4 right-4 opacity-0 transform translate-x-2 transition-all duration-300 group-hover:opacity-100 group-hover:translate-x-0">
          <div className="rounded-full bg-primary/10 p-1.5">
            <svg
              className="h-4 w-4 text-primary"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5l7 7-7 7"
              />
            </svg>
          </div>
        </div>
      </div>
    </Link>
  )
}
