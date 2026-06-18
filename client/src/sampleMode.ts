export type CandidateSource = 'raw' | 'review' | 'sample'

export function canSaveCandidates(source: CandidateSource): boolean {
  return source !== 'sample'
}

export function candidateSourceFromApi(source: string): CandidateSource {
  if (source === 'review') return 'review'
  if (source === 'sample') return 'sample'
  return 'raw'
}

export function candidateSourceLabel(source: CandidateSource): string {
  if (source === 'review') return 'Saved review draft'
  if (source === 'sample') return 'Demo sample data'
  return 'Raw CV candidates'
}
