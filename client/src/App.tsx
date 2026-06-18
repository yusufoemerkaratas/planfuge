import { useState, useEffect } from 'react'
import { LayoutDashboard, FileCheck, Save, Download, FileJson, AlertCircle, Maximize2, Loader2, CheckCircle2 } from 'lucide-react'

export interface Candidate {
  candidate_id: string;
  status: string;
  raw_text: string | null;
  label_type: string | null;
  width_mm: number | null;
  height_mm: number | null;
  diameter_mm: number | null;
  ra_value: string | null;
  ok_value: string | null;
  reference: string | null;
  review_comment: string | null;
  [key: string]: any;
}

function App() {
  const [activePlan, setActivePlan] = useState<string | null>(null)
  const [plans, setPlans] = useState<string[]>([])
  const [loadingPlans, setLoadingPlans] = useState(true)
  const [metadata, setMetadata] = useState<{image_width?: number, image_height?: number, scale?: number} | null>(null)
  const [imageError, setImageError] = useState(false)

  // Candidates state
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [loadingCandidates, setLoadingCandidates] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)

  // Fetch available plans on mount
  useEffect(() => {
    fetch('/api/plans')
      .then(res => res.json())
      .then(data => {
        if (data.plans && Array.isArray(data.plans)) {
          setPlans(data.plans)
          if (data.plans.length > 0) {
            setActivePlan(data.plans[0])
          }
        }
      })
      .catch(err => console.error("Failed to load plans:", err))
      .finally(() => setLoadingPlans(false))
  }, [])

  // Fetch metadata and candidates when activePlan changes
  useEffect(() => {
    if (!activePlan) return
    setImageError(false)
    setMetadata(null)
    setCandidates([])
    setLoadingCandidates(true)
    setSaveSuccess(false)
    
    // 1. Fetch metadata
    fetch(`/api/metadata/${activePlan}`)
      .then(res => res.ok ? res.json() : null)
      .then(data => {
        if (data) setMetadata(data)
      })
      .catch(err => console.error("Failed to load metadata:", err))

    // 2. Fetch candidates (Try reviews first, fallback to raw candidates)
    fetch(`/api/reviews/${activePlan}`)
      .then(res => {
        if (res.ok) return res.json()
        throw new Error('No draft found')
      })
      .then(data => {
        if (data && data.candidates) {
          setCandidates(data.candidates)
          setLoadingCandidates(false)
        } else {
          throw new Error('Empty draft')
        }
      })
      .catch(() => {
        // Fallback to raw candidates
        fetch(`/api/candidates/${activePlan}`)
          .then(res => res.ok ? res.json() : { candidates: [] })
          .then(data => {
            setCandidates(data.candidates || [])
          })
          .catch(err => console.error("Failed to load candidates:", err))
          .finally(() => setLoadingCandidates(false))
      })

  }, [activePlan])

  const handleSave = async () => {
    if (!activePlan || candidates.length === 0) return
    setIsSaving(true)
    setSaveSuccess(false)
    try {
      const response = await fetch(`/api/reviews/${activePlan}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(candidates),
      })
      if (response.ok) {
        setSaveSuccess(true)
        setTimeout(() => setSaveSuccess(false), 3000)
      } else {
        console.error("Save failed:", await response.text())
      }
    } catch (error) {
      console.error("Save error:", error)
    } finally {
      setIsSaving(false)
    }
  }

  const handleCellChange = (id: string, field: keyof Candidate, value: any) => {
    setCandidates(prev => 
      prev.map(c => c.candidate_id === id ? { ...c, [field]: value } : c)
    )
  }

  // Helper for text inputs
  const TextInput = ({ candidate, field, type = "text" }: { candidate: Candidate, field: keyof Candidate, type?: string }) => (
    <input
      type={type}
      value={candidate[field] === null ? "" : candidate[field]}
      onChange={(e) => handleCellChange(candidate.candidate_id, field, type === "number" ? (e.target.value ? Number(e.target.value) : null) : e.target.value)}
      className="w-full bg-transparent border-b border-transparent hover:border-border focus:border-primary focus:outline-none focus:ring-0 px-1 py-1 text-sm transition-colors"
      placeholder="-"
    />
  )

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-muted border-r border-border flex flex-col transition-all duration-300">
        <div className="h-16 flex items-center px-6 border-b border-border">
          <h1 className="text-xl font-bold tracking-tight text-primary">PlanFuge</h1>
        </div>
        
        <div className="p-4 flex-1 overflow-y-auto">
          <h2 className="text-xs uppercase font-semibold text-muted-foreground tracking-wider mb-4">Plan Selection</h2>
          
          {loadingPlans ? (
            <div className="animate-pulse space-y-2">
              <div className="h-10 bg-border rounded-md w-full"></div>
              <div className="h-10 bg-border rounded-md w-full"></div>
            </div>
          ) : plans.length === 0 ? (
            <div className="p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-md flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-yellow-600 shrink-0 mt-0.5" />
              <p className="text-sm text-yellow-700 dark:text-yellow-500">
                No plan files found. Please add PNG files to <strong>data/pages/</strong>.
              </p>
            </div>
          ) : (
            <nav className="space-y-1">
              {plans.map((plan_id) => (
                <button
                  key={plan_id}
                  onClick={() => setActivePlan(plan_id)}
                  className={`w-full flex items-center space-x-3 px-3 py-2 rounded-md font-medium transition-all duration-200 ${
                    activePlan === plan_id 
                      ? "bg-primary text-primary-foreground shadow-sm translate-x-1" 
                      : "text-muted-foreground hover:bg-primary/5 hover:text-foreground"
                  }`}
                >
                  <LayoutDashboard className={`w-4 h-4 ${activePlan === plan_id ? "text-primary-foreground/80" : ""}`} />
                  <span className="truncate">{plan_id}</span>
                </button>
              ))}
            </nav>
          )}
        </div>
        
        <div className="p-4 border-t border-border">
          <p className="text-xs text-muted-foreground">Demo Mode</p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Header */}
        <header className="h-16 flex items-center px-8 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-10 shrink-0">
          <h2 className="text-lg font-medium text-foreground flex items-center gap-3">
            {activePlan ? `Dashboard — ${activePlan}` : "Dashboard"}
            {metadata && metadata.image_width && metadata.image_height && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-muted text-muted-foreground border border-border">
                <Maximize2 className="w-3 h-3" />
                {metadata.image_width} x {metadata.image_height}
              </span>
            )}
          </h2>
        </header>

        {/* Content Area - Split View */}
        <div className="flex-1 overflow-hidden">
          {!activePlan ? (
             <div className="h-full flex items-center justify-center p-8">
               <div className="max-w-md w-full rounded-xl border border-dashed border-border bg-muted/50 p-12 text-center text-muted-foreground">
                 <FileCheck className="w-12 h-12 mx-auto mb-4 opacity-50" />
                 <p>Please select or add a plan to view details.</p>
               </div>
             </div>
          ) : (
            <div className="h-full flex flex-col lg:flex-row divide-y lg:divide-y-0 lg:divide-x divide-border">
              
              {/* Left Column: Plan Image Viewer & Candidate Table */}
              <div className="flex-1 flex flex-col min-h-0 bg-muted/20 relative animate-in fade-in duration-500">
                
                {/* Top Half: Plan Image Viewer */}
                <div className="flex-[3] relative border-b border-border overflow-auto flex items-start justify-center p-6 bg-muted/10">
                  {imageError ? (
                    <div className="m-auto max-w-sm w-full rounded-xl border border-red-500/20 bg-red-500/5 p-6 text-center text-red-600 dark:text-red-400">
                      <AlertCircle className="w-10 h-10 mx-auto mb-3 opacity-80" />
                      <h3 className="font-semibold mb-1">Image Missing</h3>
                      <p className="text-sm opacity-80">
                        Could not load data/pages/{activePlan}.png
                      </p>
                    </div>
                  ) : (
                    <div className="relative rounded-lg overflow-hidden border border-border shadow-md bg-white max-w-full">
                      <img 
                        src={`/api/images/pages/${activePlan}`} 
                        alt={`Plan ${activePlan}`}
                        className="max-w-full h-auto object-contain block"
                        onError={() => setImageError(true)}
                      />
                    </div>
                  )}
                </div>

                {/* Bottom Half: Editable Candidate Table */}
                <div className="flex-[2] bg-background flex flex-col min-h-0">
                  <div className="px-4 py-3 border-b border-border flex items-center justify-between bg-card">
                    <h3 className="font-semibold text-sm">Detected Candidates ({candidates.length})</h3>
                  </div>
                  
                  <div className="flex-1 overflow-auto p-0">
                    {loadingCandidates ? (
                      <div className="flex items-center justify-center h-full text-muted-foreground">
                        <Loader2 className="w-6 h-6 animate-spin mr-2" />
                        Loading candidates...
                      </div>
                    ) : candidates.length === 0 ? (
                      <div className="flex items-center justify-center h-full text-muted-foreground p-4 text-sm text-center">
                        No candidates found for this plan.
                      </div>
                    ) : (
                      <div className="inline-block min-w-full align-middle">
                        <table className="min-w-full divide-y divide-border border-b border-border">
                          <thead className="bg-muted/50 sticky top-0 z-10 backdrop-blur-sm">
                            <tr>
                              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider whitespace-nowrap">ID</th>
                              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider whitespace-nowrap">Status</th>
                              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider whitespace-nowrap">Raw Text</th>
                              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider whitespace-nowrap">Label Type</th>
                              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider whitespace-nowrap">W (mm)</th>
                              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider whitespace-nowrap">H (mm)</th>
                              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider whitespace-nowrap">Ø (mm)</th>
                              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider whitespace-nowrap">RA</th>
                              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider whitespace-nowrap">OK</th>
                              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider whitespace-nowrap">Reference</th>
                              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider whitespace-nowrap">Comment</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-border bg-card">
                            {candidates.map((c) => (
                              <tr key={c.candidate_id} className="hover:bg-muted/30 transition-colors">
                                <td className="px-4 py-2 whitespace-nowrap text-xs font-medium text-muted-foreground border-r border-border/50 bg-muted/10">
                                  {c.candidate_id}
                                </td>
                                <td className="px-2 py-2 whitespace-nowrap">
                                  <select 
                                    value={c.status || 'needs_review'} 
                                    onChange={(e) => handleCellChange(c.candidate_id, 'status', e.target.value)}
                                    className={`text-xs px-2 py-1 rounded border-none font-medium focus:ring-1 focus:ring-primary ${
                                      c.status === 'verified' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' :
                                      c.status === 'rejected' ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' :
                                      c.status === 'duplicate_candidate' ? 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400' :
                                      'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
                                    }`}
                                  >
                                    <option value="needs_review">Needs Review</option>
                                    <option value="verified">Verified</option>
                                    <option value="rejected">Rejected</option>
                                    <option value="duplicate_candidate">Duplicate</option>
                                  </select>
                                </td>
                                <td className="px-2 py-2 min-w-[120px]"><TextInput candidate={c} field="raw_text" /></td>
                                <td className="px-2 py-2 min-w-[100px]"><TextInput candidate={c} field="label_type" /></td>
                                <td className="px-2 py-2 min-w-[80px]"><TextInput candidate={c} field="width_mm" type="number" /></td>
                                <td className="px-2 py-2 min-w-[80px]"><TextInput candidate={c} field="height_mm" type="number" /></td>
                                <td className="px-2 py-2 min-w-[80px]"><TextInput candidate={c} field="diameter_mm" type="number" /></td>
                                <td className="px-2 py-2 min-w-[80px]"><TextInput candidate={c} field="ra_value" /></td>
                                <td className="px-2 py-2 min-w-[80px]"><TextInput candidate={c} field="ok_value" /></td>
                                <td className="px-2 py-2 min-w-[120px]"><TextInput candidate={c} field="reference" /></td>
                                <td className="px-2 py-2 min-w-[150px]"><TextInput candidate={c} field="review_comment" /></td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                </div>

              </div>

              {/* Right Column: Status & Actions (Fixed width on desktop) */}
              <div className="w-full lg:w-96 shrink-0 overflow-y-auto p-6 bg-background space-y-6">
                
                {/* Status Panel */}
                <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
                  <h4 className="text-base font-semibold mb-4 flex items-center gap-2">
                    <FileCheck className="w-4 h-4 text-green-500" />
                    Pipeline Status
                  </h4>
                  <ul className="space-y-3">
                    <li className="flex items-center justify-between text-sm">
                      <span className="flex items-center gap-2 text-foreground">
                        <div className={`w-2 h-2 rounded-full ${!imageError ? 'bg-green-500' : 'bg-red-500'}`} />
                        Source Image
                      </span>
                      <span className="text-muted-foreground text-xs">{!imageError ? 'Available' : 'Missing'}</span>
                    </li>
                    <li className="flex items-center justify-between text-sm">
                      <span className="flex items-center gap-2 text-foreground">
                        <div className={`w-2 h-2 rounded-full ${candidates.length > 0 ? 'bg-green-500' : 'bg-yellow-500'}`} />
                        Candidates JSON
                      </span>
                      <span className="text-muted-foreground text-xs">{candidates.length > 0 ? 'Loaded' : 'Missing'}</span>
                    </li>
                    <li className="flex items-center justify-between text-sm">
                      <span className="flex items-center gap-2 text-foreground">
                        <div className="w-2 h-2 rounded-full bg-yellow-500" />
                        Verified Export
                      </span>
                      <span className="text-muted-foreground text-xs">Missing</span>
                    </li>
                  </ul>
                </div>

                {/* Quick Actions */}
                <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
                  <h4 className="text-base font-semibold mb-4">Quick Actions</h4>
                  <div className="grid grid-cols-2 gap-3">
                    <button 
                      onClick={handleSave}
                      disabled={isSaving || candidates.length === 0}
                      className="col-span-2 flex items-center justify-center gap-2 p-3 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm font-medium"
                    >
                      {isSaving ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : saveSuccess ? (
                        <CheckCircle2 className="w-4 h-4 text-green-400" />
                      ) : (
                        <Save className="w-4 h-4" />
                      )}
                      <span>{isSaving ? 'Saving...' : saveSuccess ? 'Saved!' : 'Review Detections'}</span>
                    </button>
                    <button className="flex flex-col items-center justify-center p-3 rounded-lg border border-border bg-muted/30 hover:bg-primary/5 hover:border-primary/20 transition-all group">
                      <Download className="w-5 h-5 mb-1 text-muted-foreground group-hover:text-primary transition-colors" />
                      <span className="text-xs font-medium text-foreground">Export CSV</span>
                    </button>
                    <button className="flex flex-col items-center justify-center p-3 rounded-lg border border-border bg-muted/30 hover:bg-primary/5 hover:border-primary/20 transition-all group">
                      <FileJson className="w-5 h-5 mb-1 text-muted-foreground group-hover:text-primary transition-colors" />
                      <span className="text-xs font-medium text-foreground">Export JSON</span>
                    </button>
                  </div>
                </div>

              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
