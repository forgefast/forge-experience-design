import { useState, useEffect } from 'react'
import { api } from '../services/api'

interface Backup {
  backup_path: string
  relative_path: string
  timestamp: string
  size: number
  created_at: string
}

export default function FixHistory() {
  const [backups, setBackups] = useState<Backup[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadBackups()
  }, [])

  const loadBackups = async () => {
    try {
      setLoading(true)
      const data = await api.listBackups()
      setBackups(data.backups || [])
    } catch (error) {
      console.error('Erro ao carregar backups:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString('pt-BR')
  }

  if (loading) {
    return (
      <div className="p-6">
        <div className="text-white">Carregando histórico...</div>
      </div>
    )
  }

  if (backups.length === 0) {
    return (
      <div className="p-6">
        <h2 className="text-2xl font-bold text-white mb-4">Histórico de Backups</h2>
        <div className="bg-gray-800 rounded-lg p-6 text-center">
          <p className="text-gray-400">Nenhum backup encontrado</p>
        </div>
      </div>
    )
  }

  // Agrupar por timestamp
  const groupedBackups = backups.reduce((acc, backup) => {
    if (!acc[backup.timestamp]) {
      acc[backup.timestamp] = []
    }
    acc[backup.timestamp].push(backup)
    return acc
  }, {} as Record<string, Backup[]>)

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">Histórico de Backups</h2>
        <button
          onClick={loadBackups}
          className="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600"
        >
          Atualizar
        </button>
      </div>

      <div className="space-y-4">
        {Object.entries(groupedBackups)
          .sort(([a], [b]) => b.localeCompare(a))
          .map(([timestamp, files]) => (
            <div key={timestamp} className="bg-gray-800 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold text-white">
                  Backup: {timestamp}
                </h3>
                <span className="text-sm text-gray-400">
                  {formatDate(files[0].created_at)}
                </span>
              </div>
              
              <div className="space-y-2">
                {files.map((backup, idx) => (
                  <div
                    key={idx}
                    className="bg-gray-900 rounded p-3 flex items-center justify-between"
                  >
                    <div className="flex-1">
                      <p className="text-white font-mono text-sm">
                        {backup.relative_path}
                      </p>
                      <p className="text-gray-400 text-xs mt-1">
                        {formatSize(backup.size)}
                      </p>
                    </div>
                    <div className="text-xs text-gray-500 font-mono">
                      {backup.backup_path}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
      </div>
    </div>
  )
}

