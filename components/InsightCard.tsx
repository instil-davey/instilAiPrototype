"use client"

import { TrendingUp, TrendingDown, Minus, LucideIcon } from "lucide-react"
import * as Icons from "lucide-react"
import { cn } from "@/lib/utils"

export interface InsightCardProps {
  id: string
  title: string
  value: string
  change: string
  trend: "up" | "down" | "neutral"
  description: string
  icon: string
  delay?: number
}

export function InsightCard({
  title,
  value,
  change,
  trend,
  description,
  icon,
  delay = 0,
}: InsightCardProps) {
  // Get the icon component dynamically
  const IconComponent = getIconComponent(icon)

  const trendColors = {
    up: "text-emerald-600 bg-emerald-50",
    down: "text-rose-600 bg-rose-50",
    neutral: "text-slate-600 bg-slate-50",
  }

  const TrendIcon = {
    up: TrendingUp,
    down: TrendingDown,
    neutral: Minus,
  }[trend]

  return (
    <div
      className={cn(
        "group relative overflow-hidden rounded-xl border bg-card p-6",
        "transition-all duration-300 ease-out hover:shadow-lg hover:scale-[1.02]",
        "animate-slide-in opacity-0"
      )}
      style={{
        animationDelay: `${delay}ms`,
        animationFillMode: "forwards",
      }}
    >
      {/* Background gradient on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />

      <div className="relative">
        {/* Header with icon */}
        <div className="flex items-start justify-between mb-4">
          <div
            className={cn(
              "rounded-lg p-2.5 transition-colors duration-300",
              "bg-primary/10 group-hover:bg-primary/20"
            )}
          >
            <IconComponent className="h-5 w-5 text-primary" />
          </div>
          <div
            className={cn(
              "flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium",
              "transition-all duration-300",
              trendColors[trend]
            )}
          >
            <TrendIcon className="h-3 w-3" />
            <span>{change}</span>
          </div>
        </div>

        {/* Value */}
        <div className="mb-1">
          <div className="text-3xl font-bold tracking-tight text-foreground transition-colors duration-300 group-hover:text-primary">
            {value}
          </div>
        </div>

        {/* Title and description */}
        <div className="space-y-1">
          <h3 className="text-sm font-medium text-muted-foreground">{title}</h3>
          <p className="text-xs text-muted-foreground/80">{description}</p>
        </div>
      </div>

      {/* Bottom accent line */}
      <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-primary/0 via-primary to-primary/0 scale-x-0 transition-transform duration-300 group-hover:scale-x-100" />
    </div>
  )
}

function getIconComponent(iconName: string): LucideIcon {
  // Convert icon name to PascalCase
  const pascalCase = iconName
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join("")

  // Get the icon from lucide-react
  const Icon = (Icons as any)[pascalCase] as LucideIcon

  // Fallback to a default icon if not found
  return Icon || Icons.Activity
}
