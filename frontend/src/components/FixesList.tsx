import { useState, useEffect } from 'react'
import { api, Fix } from '../services/api'
import { FixApplier } from '../core/fix-applier'
import FixPreview from './FixPreview'
import ApplyFixDialog from './ApplyFixDialog'

export default function FixesList() {
  const [fixes, setFixes] = useState<Fix[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'pending' | 'applied' | 'rolled_back'>('all')
  const [previewFixId, setPreviewFixId] = useState<string | null>(null)
  const [applyFixId, setApplyFixId] = useState<string | null>(null)
  const fixApplier = new FixApplier()

  useEffect(() => {
    loadFixes()
    const interval = setInterval(loadFixes, 5000)
    return () => clearInterval(interval)
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

  const applyFix = (fix: Fix) => {
    fixApplier.applyFix(fix)
    loadFixes()
  }

  const rollbackFix = (fixId: string) => {
    fixApplier.rollbackFix(fixId)
    loadFixes()
  }

  const handlePreview = (fixId: string) => {
    setPreviewFixId(fixId)
  }

  const handleApplyFromPreview = async () => {
    if (previewFixId) {
      setPreviewFixId(null)
      setApplyFixId(previewFixId)
    }
  }

  const handleApplySuccess = () => {
    loadFixes()
  }

  const filteredFixes = fixes.filter(fix => {
    if (filter === 'all') return true
    return fix.status === filter
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">Correções</h1>
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg transition-all ${
              filter === 'all' ? 'bg-purple-500 text-white' : 'bg-white/10 text-white/70'
            }`}
          >
            Todas ({fixes.length})
          </button>
          <button
            onClick={() => setFilter('pending')}
            className={`px-4 py-2 rounded-lg transition-all ${
              filter === 'pending' ? 'bg-purple-500 text-white' : 'bg-white/10 text-white/70'
            }`}
          >
            Pendentes ({fixes.filter(f => f.status === 'pending').length})
          </button>
          <button
            onClick={() => setFilter('applied')}
            className={`px-4 py-2 rounded-lg transition-all ${
              filter === 'applied' ? 'bg-purple-500 text-white' : 'bg-white/10 text-white/70'
            }`}
          >
            Aplicadas ({fixes.filter(f => f.status === 'applied').length})
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-white/70">Carregando correções...</div>
      ) : filteredFixes.length === 0 ? (
        <div className="bg-white/10 backdrop-blur-md rounded-xl p-12 border border-white/20 text-center">
          <p className="text-white/70 text-lg">Nenhuma correção encontrada</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredFixes.map((fix) => (
            <div
              key={fix.id}
              className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 hover:bg-white/15 transition-all"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      fix.status === 'applied' ? 'bg-green-500/20 text-green-300 border border-green-500/30' :
                      fix.status === 'pending' ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30' :
                      'bg-gray-500/20 text-gray-300 border border-gray-500/30'
                    }`}>
                      {fix.status === 'applied' ? '✅ Aplicada' :
                       fix.status === 'pending' ? '⏳ Pendente' :
                       fix.status === 'rolled_back' ? '↩️ Revertida' : fix.status}
                    </span>
                    <span className="px-3 py-1 rounded-full text-sm bg-purple-500/20 text-purple-300 border border-purple-500/30">
                      Prioridade {fix.priority}
                    </span>
                    <span className="px-3 py-1 rounded-full text-sm bg-blue-500/20 text-blue-300 border border-blue-500/30">
                      {fix.type.toUpperCase()}
                    </span>
                  </div>
                  
                  <h3 className="text-lg font-semibold text-white mb-2">
                    {fix.target_element}
                  </h3>
                  
                  {fix.target_selector && (
                    <p className="text-white/60 text-sm mb-3">
                      Seletor: <code className="bg-white/10 px-2 py-1 rounded">{fix.target_selector}</code>
                    </p>
                  )}

                  <div className="mt-4">
                    <p className="text-white/70 text-sm mb-2">Alterações:</p>
                    <div className="space-y-2">
                      {fix.changes.map((change, idx) => (
                        <div
                          key={idx}
                          className="bg-white/5 rounded-lg p-3 border border-white/10"
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <span className="text-white font-mono text-sm">{change.property}</span>
                              <span className="text-white/60 mx-2">→</span>
                              <span className="text-purple-300 font-mono text-sm">{change.value}</span>
                            </div>
                            <span className="text-white/50 text-xs">{change.reason}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="ml-6 flex flex-col gap-2">
                  {fix.status === 'pending' && (
                    <>
                      <button
                        onClick={() => handlePreview(fix.id)}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all text-sm font-medium"
                      >
                        👁️ Preview
                      </button>
                      <button
                        onClick={() => setApplyFixId(fix.id)}
                        className="px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white rounded-lg transition-all text-sm font-medium"
                      >
                        ✨ Aplicar
                      </button>
                    </>
                  )}
                  {fix.status === 'applied' && (
                    <button
                      onClick={() => rollbackFix(fix.id)}
                      className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-300 border border-red-500/30 rounded-lg transition-all text-sm font-medium"
                    >
                      ↩️ Reverter
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Preview Modal */}
      {previewFixId && (
        <FixPreview
          fixId={previewFixId}
          onClose={() => setPreviewFixId(null)}
          onApply={handleApplyFromPreview}
        />
      )}

      {/* Apply Dialog */}
      {applyFixId && (() => {
        const fix = fixes.find(f => f.id === applyFixId)
        if (!fix) return null
        
        return (
          <ApplyFixDialog
            fixId={fix.id}
            filePath={fix.target_selector || fix.target_element}
            changes={fix.changes || []}
            onClose={() => setApplyFixId(null)}
            onSuccess={handleApplySuccess}
          />
        )
      })()}
    </div>
  )
}

