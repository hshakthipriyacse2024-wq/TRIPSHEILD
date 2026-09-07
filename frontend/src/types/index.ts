export interface User {
  id: string;
  email: string;
  full_name: string;
  phone?: string;
  role: 'traveler' | 'ops_admin' | 'sys_admin';
  is_active: boolean;
  created_at: string;
}

export interface TravelerPreference {
  id: string;
  user_id: string;
  budget_priority: number;
  speed_priority: number;
  comfort_priority: number;
  minimal_changes_priority: number;
  preferred_airlines: string[];
  preferred_transport: string[];
  max_connections: number;
  preferred_hotel_category: string;
  accessibility_requirements: Record<string, any>;
  important_activities: string[];
  non_negotiable_bookings: string[];
}

export interface Journey {
  id: string;
  user_id: string;
  title: string;
  description: string;
  origin: string;
  destination: string;
  start_date: string;
  end_date: string;
  status: 'draft' | 'active' | 'disrupted' | 'recovering' | 'recovered' | 'completed' | 'cancelled';
  resilience_score: number | null;
  is_demo: boolean;
  nodes: JourneyNode[];
  dependencies: JourneyDependency[];
  created_at: string;
  updated_at: string;
}

export interface JourneyNode {
  id: string;
  journey_id: string;
  type: 'flight' | 'train' | 'bus' | 'hotel' | 'airport_transfer' | 'taxi' | 'activity' | 'restaurant' | 'event' | 'car_rental' | 'other';
  provider: string;
  location: string;
  latitude?: number;
  longitude?: number;
  destination_location?: string;
  dest_latitude?: number;
  dest_longitude?: number;
  start_time: string;
  end_time: string;
  status: 'confirmed' | 'at_risk' | 'affected' | 'recovered' | 'cancelled' | 'pending';
  cost: number;
  currency: string;
  booking_reference: string;
  cancellation_policy?: Record<string, any>;
  flexibility: 'none' | 'low' | 'medium' | 'high';
  importance: 'critical' | 'high' | 'medium' | 'low';
  traveler_preference_weight: number;
  details: Record<string, any>;
  sequence_order: number;
  created_at: string;
  updated_at: string;
}

export interface JourneyDependency {
  id: string;
  journey_id: string;
  source_node_id: string;
  target_node_id: string;
  relationship_type: 'depends_on' | 'connects_to' | 'precedes' | 'located_near' | 'requires' | 'optional_after' | 'alternative_to';
  buffer_minutes: number;
  is_critical: boolean;
}

export interface Disruption {
  id: string;
  journey_id: string;
  affected_node_id: string;
  type: string;
  severity: 'low' | 'moderate' | 'high' | 'severe' | 'critical';
  description: string;
  delay_minutes: number;
  is_simulated: boolean;
  status: string;
  detected_at: string;
  resolved_at?: string;
  impact_analysis?: ImpactAnalysis;
}

export interface ImpactAnalysis {
  id: string;
  disruption_id: string;
  journey_id: string;
  impact_score: number;
  severity_class: string;
  nodes_affected: number;
  financial_exposure: number;
  currency: string;
  time_impact_minutes: number;
  scoring_breakdown: Record<string, number>;
  affected_nodes_detail: any[];
  analyzed_at: string;
}

export interface RecoveryStrategy {
  id: string;
  disruption_id: string;
  journey_id: string;
  title: string;
  description: string;
  changed_components: string[];
  preserved_components: string[];
  additional_cost: number;
  currency: string;
  time_saved_minutes: number;
  num_changes: number;
  feasibility_score: number;
  comfort_score: number;
  urgency_score: number;
  financial_impact_score: number;
  recovery_confidence: number;
  overall_score: number;
  explanation: string;
  is_recommended: boolean;
  rank: number;
  status: string;
}

export interface Notification {
  id: string;
  user_id: string;
  journey_id?: string;
  type: string;
  title: string;
  message: string;
  priority: string;
  is_read: boolean;
  created_at: string;
}

export interface AuditLog {
  id: string;
  user_id?: string;
  journey_id?: string;
  event_type: string;
  description: string;
  details: Record<string, any>;
  created_at: string;
}

export interface Simulation {
  id: string;
  journey_id: string;
  disruption_type: string;
  parameters: Record<string, any>;
  impact_result: ImpactAnalysis;
  recovery_options: RecoveryStrategy[];
  resilience_score_before: number;
  resilience_score_after: number;
  status: string;
}

export interface GuardianMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  context?: Record<string, any>;
}

export interface DashboardStats {
  total_journeys: number;
  active_journeys: number;
  total_disruptions: number;
  active_disruptions: number;
  recoveries_completed: number;
  money_saved: number;
  time_saved_minutes: number;
  avg_resilience_score: number;
  recent_alerts: Notification[];
}
