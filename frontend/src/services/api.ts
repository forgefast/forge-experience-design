import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

export interface Fix {
  id: string
  type: 'css' | 'javascript'
  target_element: string
  target_selector?: string
  changes: Array<{
    property: string
    value: string
    reason: string
  }>
  priority: number
  status: 'pending' | 'applied' | 'validated' | 'rolled_back'
}

export interface Rule {
  id: string
  name: string
  description: string
  issue_type: string
  priority: number
  enabled: boolean
}

export const api = {
  async getFixes(applicationId?: string, limit: number = 100): Promise<Fix[]> {
    const response = await apiClient.get('/fixes/generate', {
      params: { application_id: applicationId, limit }
    })
    return response.data
  },

  async getRules(): Promise<Rule[]> {
    const response = await apiClient.get('/fixes/rules')
    return response.data
  },

  async enableRule(ruleId: string): Promise<void> {
    await apiClient.post(`/fixes/rules/${ruleId}/enable`)
  },

  async disableRule(ruleId: string): Promise<void> {
    await apiClient.post(`/fixes/rules/${ruleId}/disable`)
  },

  async getFixPreview(fixId: string) {
    const response = await apiClient.get(`/fixes/${fixId}/preview`)
    return response.data
  },

  async applyFixToSource(fixId: string, createBackup: boolean = true) {
    const response = await apiClient.post(`/fixes/${fixId}/apply-source`, null, {
      params: { create_backup: createBackup }
    })
    return response.data
  },

  async rollbackFixSource(fixId: string, backupPath: string) {
    const response = await apiClient.post(`/fixes/${fixId}/rollback-source`, {
      backup_path: backupPath
    })
    return response.data
  },

  async listBackups() {
    const response = await apiClient.get('/fixes/backups')
    return response.data
  }
}

