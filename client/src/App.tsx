import { useState, useEffect } from 'react'
import { LayoutDashboard, FileCheck, Save, Download, FileJson, AlertCircle, Maximize2 } from 'lucide-react'

function App() {
  const [activePlan, setActivePlan] = useState<string | null>(null)
  const [plans, setPlans] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [metadata, setMetadata] = useState<{image_width?: number, image_height?: number, scale?: number} | null>(null)
  const [imageError, setImageError] = useState(false)

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
      .finally(() => setLoading(false))
  }, [])

  // Fetch metadata when activePlan changes
  useEffect(() => {
    if (!activePlan) return
    setImageError(false)
    setMetadata(null)
    
    fetch(`/api/metadata/${activePlan}`)
      .then(res => res.ok ? res.json() : null)
      .then(data => {
        if (data) setMetadata(data)
      })
      .catch(err => console.error("Failed to load metadata:", err))
  }, [activePlan])

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-muted border-r border-border flex flex-col transition-all duration-300">
        <div className="h-16 flex items-center px-6 border-b border-border">
          <h1 className="text-xl font-bold tracking-tight text-primary">PlanFuge</h1>
        </div>
        
        <div className="p-4 flex-1 overflow-y-auto">
          <h2 className="text-xs uppercase font-semibold text-muted-foreground tracking-wider mb-4">Plan Selection</h2>
          
          {loading ? (
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
              
              {/* Left Column: Plan Image Viewer (Flex growing) */}
              <div className="flex-1 flex flex-col min-h-0 bg-muted/20 relative animate-in fade-in duration-500">
                {imageError ? (
                  <div className="absolute inset-0 flex items-center justify-center p-8">
                    <div className="max-w-sm w-full rounded-xl border border-red-500/20 bg-red-500/5 p-6 text-center text-red-600 dark:text-red-400">
                      <AlertCircle className="w-10 h-10 mx-auto mb-3 opacity-80" />
                      <h3 className="font-semibold mb-1">Image Missing</h3>
                      <p className="text-sm opacity-80">
                        Could not load data/pages/{activePlan}.png
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="absolute inset-0 overflow-auto p-6 flex items-start justify-center">
                    <div className="relative rounded-lg overflow-hidden border border-border shadow-md bg-white max-w-full">
                      <img 
                        src={`/api/images/pages/${activePlan}`} 
                        alt={`Plan ${activePlan}`}
                        className="max-w-full h-auto object-contain block"
                        onError={() => setImageError(true)}
                      />
                    </div>
                  </div>
                )}
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
                        <div className="w-2 h-2 rounded-full bg-green-500" />
                        Candidates JSON
                      </span>
                      <span className="text-muted-foreground text-xs">Available</span>
                    </li>
                    <li className="flex items-center justify-between text-sm">
                      <span className="flex items-center gap-2 text-foreground">
                        <div className="w-2 h-2 rounded-full bg-yellow-500" />
                        Review Draft
                      </span>
                      <span className="text-muted-foreground text-xs">Missing</span>
                    </li>
                  </ul>
                </div>

                {/* Quick Actions */}
                <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
                  <h4 className="text-base font-semibold mb-4">Quick Actions</h4>
                  <div className="grid grid-cols-2 gap-3">
                    <button className="col-span-2 flex items-center justify-center gap-2 p-3 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors shadow-sm font-medium">
                      <Save className="w-4 h-4" />
                      <span>Review Detections</span>
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
