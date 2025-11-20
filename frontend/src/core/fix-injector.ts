/**
 * Fix Injector
 * 
 * Injeta correções CSS/JavaScript em outras aplicações (ex: ForgeTest Studio)
 * Pode ser usado como script externo ou extensão de navegador
 */

import { FixApplier, Fix } from './fix-applier';

export interface FixInjectorConfig {
  apiUrl: string;
  applicationId: string;
  autoApply: boolean;
  pollInterval: number; // em milissegundos
}

export class FixInjector {
  private config: FixInjectorConfig;
  private fixApplier: FixApplier;
  private pollIntervalId: number | null = null;
  private appliedFixIds: Set<string> = new Set();

  constructor(config: FixInjectorConfig) {
    this.config = config;
    this.fixApplier = new FixApplier();
  }

  /**
   * Inicia injeção automática de correções
   */
  start(): void {
    if (this.pollIntervalId !== null) {
      console.warn('FixInjector já está rodando');
      return;
    }

    console.log('FixInjector iniciado', this.config);

    // Aplicar correções imediatamente
    this.fetchAndApplyFixes();

    // Polling periódico
    this.pollIntervalId = window.setInterval(() => {
      this.fetchAndApplyFixes();
    }, this.config.pollInterval);
  }

  /**
   * Para injeção automática
   */
  stop(): void {
    if (this.pollIntervalId !== null) {
      clearInterval(this.pollIntervalId);
      this.pollIntervalId = null;
      console.log('FixInjector parado');
    }
  }

  /**
   * Busca e aplica correções da API
   */
  private async fetchAndApplyFixes(): Promise<void> {
    try {
      const response = await fetch(
        `${this.config.apiUrl}/api/fixes/generate?application_id=${this.config.applicationId}&limit=50`
      );

      if (!response.ok) {
        console.error('Erro ao buscar correções:', response.statusText);
        return;
      }

      const fixes: Fix[] = await response.json();

      // Aplicar apenas correções pendentes que ainda não foram aplicadas
      const pendingFixes = fixes.filter(
        fix => fix.status === 'pending' && !this.appliedFixIds.has(fix.id)
      );

      if (pendingFixes.length === 0) {
        return;
      }

      console.log(`Aplicando ${pendingFixes.length} correções`);

      for (const fix of pendingFixes) {
        if (this.config.autoApply) {
          const applied = this.fixApplier.applyFix(fix);
          if (applied) {
            this.appliedFixIds.add(fix.id);
            console.log(`Correção aplicada: ${fix.id}`, fix);

            // Notificar API que correção foi aplicada
            await this.notifyFixApplied(fix.id);
          }
        }
      }
    } catch (error) {
      console.error('Erro ao buscar/aplicar correções:', error);
    }
  }

  /**
   * Notifica API que correção foi aplicada
   */
  private async notifyFixApplied(fixId: string): Promise<void> {
    try {
      // Em produção, haveria um endpoint para atualizar status
      // Por enquanto, apenas log
      console.log(`Correção ${fixId} aplicada com sucesso`);
    } catch (error) {
      console.error('Erro ao notificar aplicação de correção:', error);
    }
  }

  /**
   * Aplica uma correção específica manualmente
   */
  applyFix(fix: Fix): boolean {
    const applied = this.fixApplier.applyFix(fix);
    if (applied) {
      this.appliedFixIds.add(fix.id);
    }
    return applied;
  }

  /**
   * Reverte uma correção
   */
  rollbackFix(fixId: string): boolean {
    const rolledBack = this.fixApplier.rollbackFix(fixId);
    if (rolledBack) {
      this.appliedFixIds.delete(fixId);
    }
    return rolledBack;
  }

  /**
   * Obtém correções aplicadas
   */
  getAppliedFixes(): Fix[] {
    return this.fixApplier.getAppliedFixes();
  }

  /**
   * Limpa todas as correções aplicadas
   */
  clearAll(): void {
    this.fixApplier.clearAll();
    this.appliedFixIds.clear();
    console.log('Todas as correções foram removidas');
  }
}

/**
 * Cria instância global do FixInjector
 * Útil para uso como script externo
 */
export function createFixInjector(config: FixInjectorConfig): FixInjector {
  const injector = new FixInjector(config);
  
  // Expor globalmente para uso em outras aplicações
  if (typeof window !== 'undefined') {
    (window as any).forgeExperienceDesign = {
      injector,
      start: () => injector.start(),
      stop: () => injector.stop(),
      applyFix: (fix: Fix) => injector.applyFix(fix),
      rollbackFix: (fixId: string) => injector.rollbackFix(fixId),
      clearAll: () => injector.clearAll()
    };
  }
  
  return injector;
}

/**
 * Script de inicialização automática
 * Pode ser injetado em outras aplicações
 */
export function autoStart(config: Partial<FixInjectorConfig>): void {
  const defaultConfig: FixInjectorConfig = {
    apiUrl: 'http://localhost:8003',
    applicationId: 'forgetest-studio',
    autoApply: true,
    pollInterval: 30000 // 30 segundos
  };

  const finalConfig = { ...defaultConfig, ...config };
  const injector = createFixInjector(finalConfig);
  injector.start();
}

