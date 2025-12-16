import { NextResponse } from "next/server"
import { getDb } from "@/lib/db"

export const dynamic = "force-dynamic"

export async function GET() {
  try {
    const db = getDb()

    const segments = db
      .prepare(`
        SELECT
          constituent_type,
          COUNT(*) as count,
          COALESCE(SUM(total_lifetime_giving), 0) as total_giving,
          COALESCE(AVG(total_lifetime_giving), 0) as avg_giving
        FROM constituents
        GROUP BY constituent_type
        ORDER BY total_giving DESC
      `)
      .all() as Array<{
        constituent_type: string
        count: number
        total_giving: number
        avg_giving: number
      }>

    // Map segments to a more UI-friendly format
    const formattedSegments = segments.map((segment) => ({
      id: segment.constituent_type.toLowerCase().replace(/\s+/g, "-"),
      name: segment.constituent_type,
      count: segment.count,
      totalGiving: segment.total_giving,
      avgGiving: segment.avg_giving,
      description: getSegmentDescription(segment.constituent_type),
      color: getSegmentColor(segment.constituent_type),
    }))

    return NextResponse.json({ segments: formattedSegments })
  } catch (error) {
    console.error("Error fetching segments:", error)
    return NextResponse.json(
      { error: "Failed to fetch segments" },
      { status: 500 }
    )
  }
}

function getSegmentDescription(type: string): string {
  const descriptions: Record<string, string> = {
    Donor: "Financial contributors to the organization",
    "Major Donor": "High-value contributors and key supporters",
    Volunteer: "Active volunteers and service contributors",
    "Board Member": "Governance and leadership team members",
    Staff: "Current and former staff members",
    Other: "Other constituent relationships",
  }
  return descriptions[type] || "Constituent segment"
}

function getSegmentColor(type: string): string {
  const colors: Record<string, string> = {
    Donor: "blue",
    "Major Donor": "purple",
    Volunteer: "green",
    "Board Member": "amber",
    Staff: "slate",
    Other: "gray",
  }
  return colors[type] || "gray"
}
