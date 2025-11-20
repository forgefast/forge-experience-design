import { useState, useEffect } from 'react'
import Dashboard from './components/Dashboard'
import FixesList from './components/FixesList'
import RulesManager from './components/RulesManager'
import { api } from './services/api'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'fixes' | 'rules'>('dashboard')
  const [stats, setStats] = useState({
    totalIssues: 0,
    fixesGenerated: 0,
    fixesApplied: 0,
    improvementRate: 0
  })

  useEffect(() => {
    loadStats()
    const interval = setInterval(loadStats, 5000) // Atualizar a cada 5s
    return () => clearInterval(interval)
  }, [])

  const loadStats = async () => {
    try {
      const fixes = await api.getFixes()
      const rules = await api.getRules()
      
      setStats({
        totalIssues: fixes.length,
        fixesGenerated: fixes.length,
        fixesApplied: fixes.filter(f => f.status === 'applied').length,
        improvementRate: fixes.length > 0 
          ? (fixes.filter(f => f.status === 'applied').length / fixes.length) * 100 
          : 0
      })
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="bg-white/10 backdrop-blur-md border-b border-white/20">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <span className="text-white text-xl font-bold">FED</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">ForgeExperienceDesign</h1>
                <p className="text-sm text-white/70">Correção Automática de UI/UX</p>
              </div>
            </div>
            <nav className="flex gap-2">
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`px-4 py-2 rounded-lg transition-all ${
                  activeTab === 'dashboard'
                    ? 'bg-purple-500 text-white'
                    : 'bg-white/10 text-white/70 hover:bg-white/20'
                }`}
              >
                📊 Dashboard
              </button>
              <button
                onClick={() => setActiveTab('fixes')}
                className={`px-4 py-2 rounded-lg transition-all ${
                  activeTab === 'fixes'
                    ? 'bg-purple-500 text-white'
                    : 'bg-white/10 text-white/70 hover:bg-white/20'
                }`}
              >
                🔧 Correções
              </button>
              <button
                onClick={() => setActiveTab('rules')}
                className={`px-4 py-2 rounded-lg transition-all ${
                  activeTab === 'rules'
                    ? 'bg-purple-500 text-white'
                    : 'bg-white/10 text-white/70 hover:bg-white/20'
                }`}
              >
                ⚙️ Regras
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {activeTab === 'dashboard' && <Dashboard stats={stats} onRefresh={loadStats} />}
        {activeTab === 'fixes' && <FixesList />}
        {activeTab === 'rules' && <RulesManager />}
      </main>
    </div>
  )
}

export default App

