import { useState, useEffect } from 'react'
import { api, Fix } from '../services/api'
import { FixApplier } from '../core/fix-applier'

interface DashboardProps {
  stats: {
    totalIssues: number
    fixesGenerated: number
    fixesApplied: number
    improvementRate: number
  }
  onRefresh: () => void
}

export default function Dashboard({ stats, onRefresh }: DashboardProps) {
  const [fixes, setFixes] = useState<Fix[]>([])
  const [loading, setLoading] = useState(true)
  const [applying, setApplying] = useState(false)
  const fixApplier = new FixApplier()

  useEffect(() => {
    loadFixes()
  }, [])

  const loadFixes = async () => {
    try {
      setLoading(true)
      const data = await api.getFixes()
      setFixes(data)
    } catch (error) {
      console.error('Erro ao carregar correções:', error)
    } finally {
      setLoading(false)
    }
  }

  const applyAllFixes = async () => {
    try {
      setApplying(true)
      const pendingFixes = fixes.filter(f => f.status === 'pending')
      
      for (const fix of pendingFixes) {
        fixApplier.applyFix(fix)
      }
      
      await loadFixes()
      onRefresh()
      alert(`✅ ${pendingFixes.length} correções aplicadas!`)
    } catch (error) {
      console.error('Erro ao aplicar correções:', error)
      alert('❌ Erro ao aplicar correções')
    } finally {
      setApplying(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white/70 text-sm">Problemas Detectados</p>
              <p className="text-3xl font-bold text-white mt-2">{stats.totalIssues}</p>
            </div>
            <div className="w-12 h-12 bg-red-500/20 rounded-lg flex items-center justify-center">
              <span className="text-2xl">⚠️</span>
            </div>
          </div>
        </div>

        <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white/70 text-sm">Correções Geradas</p>
              <p className="text-3xl font-bold text-white mt-2">{stats.fixesGenerated}</p>
            </div>
            <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
              <span className="text-2xl">🔧</span>
            </div>
          </div>
        </div>

        <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white/70 text-sm">Correções Aplicadas</p>
              <p className="text-3xl font-bold text-white mt-2">{stats.fixesApplied}</p>
            </div>
            <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
              <span className="text-2xl">✅</span>
            </div>
          </div>
        </div>

        <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white/70 text-sm">Taxa de Melhoria</p>
              <p className="text-3xl font-bold text-white mt-2">{stats.improvementRate.toFixed(1)}%</p>
            </div>
            <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
              <span className="text-2xl">📈</span>
            </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white">Ações Rápidas</h2>
            <p className="text-white/70 text-sm mt-1">Gerar e aplicar correções automaticamente</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={loadFixes}
              disabled={loading}
              className="px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-all disabled:opacity-50"
            >
              {loading ? '🔄 Carregando...' : '🔄 Atualizar'}
            </button>
            <button
              onClick={applyAllFixes}
              disabled={applying || fixes.filter(f => f.status === 'pending').length === 0}
              className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white rounded-lg transition-all disabled:opacity-50"
            >
              {applying ? '⏳ Aplicando...' : `✨ Aplicar Todas (${fixes.filter(f => f.status === 'pending').length})`}
            </button>
          </div>
        </div>
      </div>

      {/* Recent Fixes */}
      <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
        <h2 className="text-xl font-bold text-white mb-4">Correções Recentes</h2>
        {loading ? (
          <div className="text-center py-8 text-white/70">Carregando...</div>
        ) : fixes.length === 0 ? (
          <div className="text-center py-8 text-white/70">
            <p className="text-lg mb-2">Nenhuma correção encontrada</p>
            <p className="text-sm">As correções aparecerão aqui quando problemas forem detectados</p>
          </div>
        ) : (
          <div className="space-y-3">
            {fixes.slice(0, 5).map((fix) => (
              <div
                key={fix.id}
                className="bg-white/5 rounded-lg p-4 border border-white/10 hover:bg-white/10 transition-all"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        fix.status === 'applied' ? 'bg-green-500/20 text-green-300' :
                        fix.status === 'pending' ? 'bg-yellow-500/20 text-yellow-300' :
                        'bg-gray-500/20 text-gray-300'
                      }`}>
                        {fix.status === 'applied' ? '✅ Aplicada' :
                         fix.status === 'pending' ? '⏳ Pendente' : fix.status}
                      </span>
                      <span className="px-2 py-1 rounded text-xs bg-purple-500/20 text-purple-300">
                        Prioridade: {fix.priority}
                      </span>
                    </div>
                    <p className="text-white font-medium">{fix.target_element}</p>
                    <p className="text-white/60 text-sm mt-1">
                      {fix.changes.length} alteração(ões): {fix.changes.map(c => c.property).join(', ')}
                    </p>
                  </div>
                  {fix.status === 'pending' && (
                    <button
                      onClick={() => {
                        fixApplier.applyFix(fix)
                        loadFixes()
                      }}
                      className="px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-lg transition-all text-sm"
                    >
                      Aplicar
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

