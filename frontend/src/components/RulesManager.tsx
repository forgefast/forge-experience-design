import { useState, useEffect } from 'react'
import { api, Rule } from '../services/api'

export default function RulesManager() {
  const [rules, setRules] = useState<Rule[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadRules()
  }, [])

  const loadRules = async () => {
    try {
      setLoading(true)
      const data = await api.getRules()
      setRules(data)
    } catch (error) {
      console.error('Erro ao carregar regras:', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleRule = async (ruleId: string, enabled: boolean) => {
    try {
      if (enabled) {
        await api.enableRule(ruleId)
      } else {
        await api.disableRule(ruleId)
      }
      await loadRules()
    } catch (error) {
      console.error('Erro ao alterar regra:', error)
      alert('Erro ao alterar regra')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Regras de Correção</h1>
          <p className="text-white/70 text-sm mt-1">Gerencie as regras que geram correções automáticas</p>
        </div>
        <button
          onClick={loadRules}
          className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-all"
        >
          🔄 Atualizar
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12 text-white/70">Carregando regras...</div>
      ) : (
        <div className="space-y-4">
          {rules.map((rule) => (
            <div
              key={rule.id}
              className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 hover:bg-white/15 transition-all"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <h3 className="text-xl font-semibold text-white">{rule.name}</h3>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      rule.enabled
                        ? 'bg-green-500/20 text-green-300 border border-green-500/30'
                        : 'bg-gray-500/20 text-gray-300 border border-gray-500/30'
                    }`}>
                      {rule.enabled ? '✅ Ativa' : '❌ Desativada'}
                    </span>
                    <span className="px-3 py-1 rounded-full text-xs bg-purple-500/20 text-purple-300 border border-purple-500/30">
                      Prioridade {rule.priority}
                    </span>
                  </div>
                  
                  <p className="text-white/70 mb-3">{rule.description}</p>
                  
                  <div className="flex items-center gap-4 text-sm">
                    <span className="text-white/60">
                      Tipo de problema: <code className="bg-white/10 px-2 py-1 rounded">{rule.issue_type}</code>
                    </span>
                  </div>
                </div>

                <div className="ml-6">
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={rule.enabled}
                      onChange={(e) => toggleRule(rule.id, e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-14 h-7 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-500/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-purple-500"></div>
                  </label>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {rules.length === 0 && !loading && (
        <div className="bg-white/10 backdrop-blur-md rounded-xl p-12 border border-white/20 text-center">
          <p className="text-white/70 text-lg">Nenhuma regra encontrada</p>
        </div>
      )}
    </div>
  )
}

