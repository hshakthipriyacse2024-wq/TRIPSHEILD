import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number, currency: string = 'INR'): string {
  if (currency === 'INR') return `₹${amount.toLocaleString()}`;
  if (currency === 'EUR') return `€${amount.toLocaleString()}`;
  if (currency === 'USD') return `$${amount.toLocaleString()}`;
  return `${amount.toLocaleString()} ${currency}`;
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

export function formatTime(dateStr: string): string {
  return new Date(dateStr).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
}

export function formatDateTime(dateStr: string): string {
  return `${formatDate(dateStr)} ${formatTime(dateStr)}`;
}

export const statusColors: Record<string, string> = {
  confirmed: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  at_risk: 'bg-amber-100 text-amber-800 border-amber-200',
  affected: 'bg-red-100 text-red-800 border-red-200',
  recovered: 'bg-blue-100 text-blue-800 border-blue-200',
  cancelled: 'bg-gray-100 text-gray-500 border-gray-200',
  pending: 'bg-gray-100 text-gray-600 border-gray-200',
};

export const severityColors: Record<string, string> = {
  low: 'bg-emerald-100 text-emerald-800',
  moderate: 'bg-yellow-100 text-yellow-800',
  high: 'bg-orange-100 text-orange-800',
  severe: 'bg-red-100 text-red-800',
  critical: 'bg-red-200 text-red-900',
};

export const nodeTypeIcons: Record<string, string> = {
  flight: '✈️',
  train: '🚂',
  bus: '🚌',
  hotel: '🏨',
  airport_transfer: '🚐',
  taxi: '🚕',
  activity: '🎯',
  restaurant: '🍽️',
  event: '🎭',
  car_rental: '🚗',
  other: '📦',
};
