/**
 * Fix Applier
 * 
 * Aplica correções CSS/JavaScript na interface
 */

export interface Fix {
  id: string;
  type: 'css' | 'javascript';
  target_element: string;
  target_selector?: string;
  changes: Array<{
    property: string;
    value: string;
    reason: string;
  }>;
  status: 'pending' | 'applied' | 'validated' | 'rolled_back';
}

export class FixApplier {
  private appliedFixes: Map<string, Fix> = new Map();
  private styleElement: HTMLStyleElement | null = null;

  /**
   * Aplica correção
   */
  applyFix(fix: Fix): boolean {
    try {
      if (fix.type === 'css') {
        return this.applyCSSFix(fix);
      } else if (fix.type === 'javascript') {
        return this.applyJavaScriptFix(fix);
      }
      return false;
    } catch (error) {
      console.error('Error applying fix:', error);
      return false;
    }
  }

  /**
   * Aplica correção CSS
   */
  private applyCSSFix(fix: Fix): boolean {
    // Criar elemento style se não existir
    if (!this.styleElement) {
      this.styleElement = document.createElement('style');
      this.styleElement.id = 'forge-experience-design-fixes';
      document.head.appendChild(this.styleElement);
    }

    // Gerar CSS
    const selector = fix.target_selector || fix.target_element;
    const cssRules = fix.changes
      .map(change => `${change.property}: ${change.value} !important;`)
      .join('\n    ');

    const css = `
      /* Fix: ${fix.id} */
      ${selector} {
        ${cssRules}
      }
    `;

    // Adicionar CSS ao elemento style
    this.styleElement.textContent += css;

    // Marcar como aplicado
    fix.status = 'applied';
    this.appliedFixes.set(fix.id, fix);

    return true;
  }

  /**
   * Aplica correção JavaScript
   */
  private applyJavaScriptFix(fix: Fix): boolean {
    // Implementar se necessário
    console.warn('JavaScript fixes not yet implemented');
    return false;
  }

  /**
   * Remove correção (rollback)
   */
  rollbackFix(fixId: string): boolean {
    const fix = this.appliedFixes.get(fixId);
    if (!fix) {
      return false;
    }

    // Remover CSS (simplificado - em produção, manter referência específica)
    if (this.styleElement && fix.type === 'css') {
      // Remover regra específica do CSS
      const currentCSS = this.styleElement.textContent || '';
      const fixCSS = currentCSS.split(`/* Fix: ${fix.id} */`)[0] + 
                    (currentCSS.split(`/* Fix: ${fix.id} */`)[1]?.split('}')[1] || '');
      this.styleElement.textContent = fixCSS;
    }

    fix.status = 'rolled_back';
    this.appliedFixes.delete(fixId);

    return true;
  }

  /**
   * Obtém correções aplicadas
   */
  getAppliedFixes(): Fix[] {
    return Array.from(this.appliedFixes.values());
  }

  /**
   * Limpa todas as correções
   */
  clearAll(): void {
    if (this.styleElement) {
      this.styleElement.remove();
      this.styleElement = null;
    }
    this.appliedFixes.clear();
  }
}

export default FixApplier;

