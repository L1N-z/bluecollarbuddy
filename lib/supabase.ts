import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://placeholder.supabase.co'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'placeholder-key'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Database types
export interface BobAccount {
  id?: string
  name: string
  role: string
  role_description: string
  profile: string
  services_type: 'pricing' | 'list' | 'none'
  services: Service[]
  services_not_provided: string
  location: string
  created_at?: string
  updated_at?: string
}

export interface Service {
  name: string
  price?: number
}

export interface AgentSettings {
  id?: string
  enabled: boolean
  delay_time: number
  default_greeting: string
  created_at?: string
  updated_at?: string
} 