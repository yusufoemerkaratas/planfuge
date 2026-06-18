import { useState, useEffect } from 'react'
import { LayoutDashboard, FileCheck, Save, Download, FileJson, AlertCircle } from 'lucide-react'

function App() {
  const [activePlan, setActivePlan] = useState<string | null>(null)
  const [plans, setPlans] = useState<string[]>([])
  const [loading, setLoading] = useState(true)

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
      <main className="flex-1 overflow-y-auto flex flex-col">
        {/* Header */}
        <header className="h-16 flex items-center px-8 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-10 shadow-sm">
          <h2 className="text-lg font-medium text-foreground">
            {activePlan ? `Dashboard — ${activePlan}` : "Dashboard"}
          </h2>
        </header>

        {/* Content Area */}
        <div className="flex-1 p-8 max-w-5xl mx-auto w-full">
          <div className="mb-10">
            <h3 className="text-3xl font-semibold tracking-tight mb-2">Welcome to PlanFuge</h3>
            <p className="text-muted-foreground text-lg">
              Centralized hub for reviewing AI-detected construction plan openings.
            </p>
          </div>

          {!activePlan ? (
             <div className="rounded-xl border border-dashed border-border bg-muted/50 p-12 text-center text-muted-foreground">
               <FileCheck className="w-12 h-12 mx-auto mb-4 opacity-50" />
               <p>Please select or add a plan to view details.</p>
             </div>
          ) : (
            <div className="grid gap-6 md:grid-cols-2 animate-in fade-in slide-in-from-bottom-4 duration-500">
              {/* Status Panel Skeleton */}
              <div className="rounded-xl border border-border bg-card p-6 shadow-sm hover:shadow-md transition-shadow duration-300">
                <h4 className="text-lg font-medium mb-4 flex items-center gap-2">
                  <FileCheck className="w-5 h-5 text-green-500" />
                  Pipeline Status
                </h4>
                <p className="text-sm text-muted-foreground mb-4">
                  Current data availability for <strong className="text-foreground">{activePlan}</strong>:
                </p>
                
                <ul className="space-y-3">
                  <li className="flex items-center justify-between text-sm">
                    <span className="flex items-center gap-2 text-foreground">
                      <div className="w-2 h-2 rounded-full bg-green-500" />
                      Source Image
                    </span>
                    <span className="text-muted-foreground">Available</span>
                  </li>
                  <li className="flex items-center justify-between text-sm">
                    <span className="flex items-center gap-2 text-foreground">
                      <div className="w-2 h-2 rounded-full bg-green-500" />
                      Candidates JSON
                    </span>
                    <span className="text-muted-foreground">Available</span>
                  </li>
                  <li className="flex items-center justify-between text-sm">
                    <span className="flex items-center gap-2 text-foreground">
                      <div className="w-2 h-2 rounded-full bg-yellow-500" />
                      Review Draft
                    </span>
                    <span className="text-muted-foreground">Missing</span>
                  </li>
                  <li className="flex items-center justify-between text-sm">
                    <span className="flex items-center gap-2 text-foreground">
                      <div className="w-2 h-2 rounded-full bg-yellow-500" />
                      Verified Export
                    </span>
                    <span className="text-muted-foreground">Missing</span>
                  </li>
                </ul>
              </div>

              {/* Quick Actions Placeholder */}
              <div className="rounded-xl border border-border bg-card p-6 shadow-sm hover:shadow-md transition-shadow duration-300">
                <h4 className="text-lg font-medium mb-4">Quick Actions</h4>
                <div className="grid grid-cols-2 gap-4">
                  <button className="flex flex-col items-center justify-center p-4 rounded-lg border border-border bg-muted/30 hover:bg-primary/5 hover:border-primary/20 transition-all group">
                    <Save className="w-6 h-6 mb-2 text-muted-foreground group-hover:text-primary transition-colors" />
                    <span className="text-sm font-medium text-foreground">Review Detections</span>
                  </button>
                  <button className="flex flex-col items-center justify-center p-4 rounded-lg border border-border bg-muted/30 hover:bg-primary/5 hover:border-primary/20 transition-all group">
                    <Download className="w-6 h-6 mb-2 text-muted-foreground group-hover:text-primary transition-colors" />
                    <span className="text-sm font-medium text-foreground">Export CSV</span>
                  </button>
                  <button className="flex flex-col items-center justify-center p-4 rounded-lg border border-border bg-muted/30 hover:bg-primary/5 hover:border-primary/20 transition-all group">
                    <FileJson className="w-6 h-6 mb-2 text-muted-foreground group-hover:text-primary transition-colors" />
                    <span className="text-sm font-medium text-foreground">Export JSON</span>
                  </button>
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
