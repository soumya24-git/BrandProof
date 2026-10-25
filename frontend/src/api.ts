import type { Profile, Review } from './types'

const configuredBase = import.meta.env.VITE_API_URL?.trim()
const base = (configuredBase || (import.meta.env.DEV ? 'http://127.0.0.1:8000/api' : '')).replace(/\/+$/, '')
const invalidProductionBase = (() => {
  if (!import.meta.env.PROD || !base) return import.meta.env.PROD && !base
  try {
    const url = new URL(base)
    return !['http:', 'https:'].includes(url.protocol) || ['localhost', '127.0.0.1', '::1'].includes(url.hostname)
  } catch {
    return true
  }
})()

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  if (invalidProductionBase) {
    throw new Error('VITE_API_URL must be set to the deployed Django API URL ending in /api. A local address cannot be used in production.')
  }
  const response = await fetch(`${base}${url}`, init)
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    const errors = Object.values(body).flat().join(' ')
    throw new Error(errors || `Request failed (${response.status})`)
  }
  return response.json()
}
export const api = {
  profile: () => request<Profile>('/brand/'),
  saveProfile: (profile: Partial<Profile>) => request<Profile>('/brand/1/', { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(profile) }),
  reviews: () => request<Review[]>('/reviews/'),
  review: (id: number) => request<Review>(`/reviews/${id}/`),
  createReview: (title: string, content: string, files: File[]) => { const body = new FormData(); body.set('title', title); body.set('content', content); files.forEach(file => body.append('files', file)); return request<Review>('/reviews/', { method: 'POST', body }) },
  revise: (id: number, content: string) => request<Review>(`/reviews/${id}/`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ content }) }),
  decide: (id: number, decision: string, note: string) => request<Review>(`/reviews/${id}/decide/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ decision, note }) }),
}
