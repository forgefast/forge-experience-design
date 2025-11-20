import { useState } from 'react'
import { api } from '../services/api'

interface ApplyFixDialogProps {
  fixId: string
  filePath: string
  changes: Array<{
    property: string
    action: string
    value: string
  }>
  onClose: () => void
  onSuccess: () => void
}

export default function ApplyFixDialog({
  fixId,
  filePath,
  changes,
  onClose,
  onSuccess
}: ApplyFixDialogProps) {
  const [createBackup, setCreateBackup] = useState(true)
  const [applying, setApplying] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleApply = async () => {
    try {
      setApplying(true)
      setError(null)
      
      const result = await api.applyFixToSource(fixId, createBackup)
      
      if (result.success) {
        onSuccess()
        onClose()
      } else {
        setError(result.errors?.join(', ') || 'Erro ao aplicar correção')
      }
    } catch (err: any) {
      setError(err.message || 'Erro ao aplicar correção')
    } finally {
      setApplying(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
        <h2 className="text-xl font-bold text-white mb-4">Aplicar Correção</h2>
        
        <div className="space-y-4">
          <div>
            <p className="text-sm text-gray-400 mb-1">Arquivo:</p>
            <p className="text-white font-mono text-sm">{filePath}</p>
          </div>

          <div>
            <p className="text-sm text-gray-400 mb-2">Mudanças:</p>
            <div className="bg-gray-900 rounded p-3 space-y-1">
              {changes.map((change, idx) => (
                <div key={idx} className="text-sm text-gray-300">
                  <span className="font-semibold">{change.property}</span>
                  {' '}: {change.value} ({change.action})
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="create-backup"
              checked={createBackup}
              onChange={(e) => setCreateBackup(e.target.checked)}
              className="w-4 h-4"
            />
            <label htmlFor="create-backup" className="text-sm text-gray-300">
              Criar backup antes de aplicar
            </label>
          </div>

          {error && (
            <div className="bg-red-900/30 border border-red-700 rounded p-3">
              <p className="text-red-300 text-sm">{error}</p>
            </div>
          )}
        </div>

        <div className="flex justify-end gap-2 mt-6">
          <button
            onClick={onClose}
            disabled={applying}
            className="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600 disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            onClick={handleApply}
            disabled={applying}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
          >
            {applying ? 'Aplicando...' : 'Aplicar'}
          </button>
        </div>
      </div>
    </div>
  )
}

