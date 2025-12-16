import Database from "better-sqlite3"
import path from "path"

let db: Database.Database | null = null

export function getDb() {
  if (!db) {
    const dbPath = path.join(process.cwd(), "nonprofit_crm.db")
    db = new Database(dbPath, { readonly: true })
  }
  return db
}

export interface Constituent {
  constituent_id: number
  first_name: string
  last_name: string
  email: string | null
  phone: string | null
  address: string | null
  city: string | null
  state: string | null
  zip_code: string | null
  constituent_type: string
  created_date: string
  total_lifetime_giving: number
  created_at: string
  updated_at: string
}

export interface Contribution {
  contribution_id: number
  constituent_id: number
  contribution_date: string
  amount: number
  contribution_type: string
  campaign_id: string | null
  payment_method: string | null
  acknowledgment_sent: string
  notes: string | null
}

export interface Interaction {
  interaction_id: number
  constituent_id: number
  interaction_date: string
  interaction_type: string
  subject: string | null
  notes: string | null
  staff_member: string | null
  follow_up_required: string
}

export interface Opportunity {
  opportunity_id: number
  constituent_id: number
  opportunity_name: string
  stage: string
  expected_amount: number | null
  expected_close_date: string | null
  probability: number | null
  created_date: string
  assigned_to: string | null
  notes: string | null
}
