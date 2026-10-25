import type { Profile, Review } from './types'
const base = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'
async function request<T>(url: string, init?: RequestInit): Promise<T> {
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
