import { useState, useEffect } from 'react'
import { api } from '../services/api'

interface DiffLine {
  line: number
  type: 'context' | 'added' | 'removed' | 'header'
  content: string
}

interface PreviewData {
  fix_id: string
  file_path: string
  diff: string
  formatted_diff: DiffLine[]
  changes_summary: Array<{
    property: string
    action: string
    value: string
  }>
  statistics: {
    added_lines: number
    removed_lines: number
    line_count: number
  }
}

interface FixPreviewProps {
  fixId: string
  onClose: () => void
  onApply?: () => void
}

export default function FixPreview({ fixId, onClose, onApply }: FixPreviewProps) {
  const [preview, setPreview] = useState<PreviewData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadPreview()
  }, [fixId])

  const loadPreview = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await api.getFixPreview(fixId)
      setPreview(data)
    } catch (err: any) {
      setError(err.message || 'Erro ao carregar preview')
    } finally {
      setLoading(false)
    }
  }

  const renderDiffLine = (line: DiffLine, index: number) => {
    const bgColor = 
      line.type === 'added' ? 'bg-green-900/30' :
      line.type === 'removed' ? 'bg-red-900/30' :
      line.type === 'header' ? 'bg-gray-700' :
      'bg-transparent'
    
    const textColor =
      line.type === 'added' ? 'text-green-300' :
      line.type === 'removed' ? 'text-red-300' :
      line.type === 'header' ? 'text-yellow-400' :
      'text-gray-300'

    const prefix =
      line.type === 'added' ? '+' :
      line.type === 'removed' ? '-' :
      ' '

    return (
      <div
        key={index}
        className={`flex ${bgColor} font-mono text-sm`}
      >
        <span className="w-12 text-right pr-2 text-gray-500 select-none">
          {line.type !== 'header' ? line.line : ''}
        </span>
        <span className={`w-4 text-center ${textColor} select-none`}>
          {prefix}
        </span>
        <span className={`flex-1 ${textColor} whitespace-pre-wrap break-words`}>
          {line.content}
        </span>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-gray-800 p-6 rounded-lg">
          <div className="text-white">Carregando preview...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-gray-800 p-6 rounded-lg max-w-md">
          <div className="text-red-400 mb-4">Erro: {error}</div>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600"
          >
            Fechar
          </button>
        </div>
      </div>
    )
  }

  if (!preview) {
    return null
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-700 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white">Preview da Correção</h2>
            <p className="text-sm text-gray-400 mt-1">{preview.file_path}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl"
          >
            ×
          </button>
        </div>

        {/* Statistics */}
        <div className="p-4 bg-gray-900 border-b border-gray-700 flex gap-4 text-sm">
          <div className="text-green-400">
            +{preview.statistics.added_lines} linhas
          </div>
          <div className="text-red-400">
            -{preview.statistics.removed_lines} linhas
          </div>
          <div className="text-gray-400">
            {preview.statistics.line_count} linhas totais
          </div>
        </div>

        {/* Changes Summary */}
        {preview.changes_summary.length > 0 && (
          <div className="p-4 bg-gray-900 border-b border-gray-700">
            <h3 className="text-sm font-semibold text-white mb-2">Mudanças:</h3>
            <div className="flex flex-wrap gap-2">
              {preview.changes_summary.map((change, idx) => (
                <span
                  key={idx}
                  className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs"
                >
                  {change.property}: {change.value} ({change.action})
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Diff Content */}
        <div className="flex-1 overflow-auto">
          <div className="p-4">
            <div className="bg-gray-900 rounded border border-gray-700 overflow-hidden">
              {preview.formatted_diff.map((line, index) => renderDiffLine(line, index))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-700 flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600"
          >
            Cancelar
          </button>
          {onApply && (
            <button
              onClick={onApply}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Aplicar Correção
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

