/**
 * Stylelint Validator
 * 
 * Valida CSS usando stylelint (executado no build, não em runtime)
 * Para runtime, fazemos validação básica de CSS
 */

export interface CSSIssue {
  rule: string;
  severity: 'error' | 'warning';
  message: string;
  line?: number;
  column?: number;
}

export class StylelintValidator {
  /**
   * Valida CSS básico (sem stylelint em runtime)
   * Faz validações simples de propriedades CSS
   */
  validateCSS(css: string): CSSIssue[] {
    const issues: CSSIssue[] = [];
    
    // Verificar propriedades inválidas comuns
    const invalidProperties = [
      /color:\s*#[0-9a-fA-F]{3,6}\s*;?/g,  // Cores hex válidas
    ];
    
    // Verificar unidades inválidas
    const lines = css.split('\n');
    lines.forEach((line, index) => {
      // Verificar unidades sem número
      if (line.match(/:\s*(px|em|rem|%|vh|vw)\s*;/) && !line.match(/:\s*\d+(\.\d+)?(px|em|rem|%|vh|vw)\s*;/)) {
        issues.push({
          rule: 'invalid-unit',
          severity: 'error',
          message: 'Unidade CSS sem valor numérico',
          line: index + 1
        });
      }
      
      // Verificar propriedades com valores inválidos
      if (line.match(/min-width:\s*0(px|em|rem)?\s*;/) || line.match(/min-height:\s*0(px|em|rem)?\s*;/)) {
        issues.push({
          rule: 'zero-dimension',
          severity: 'warning',
          message: 'Dimensão mínima zero pode causar problemas de layout',
          line: index + 1
        });
      }
    });
    
    return issues;
  }

  /**
   * Valida estilos inline de um elemento
   */
  validateInlineStyles(element: HTMLElement): CSSIssue[] {
    const style = element.getAttribute('style');
    if (!style) {
      return [];
    }
    
    return this.validateCSS(style);
  }

  /**
   * Sugere correções para problemas encontrados
   */
  suggestFixes(issue: CSSIssue): string | null {
    switch (issue.rule) {
      case 'zero-dimension':
        return 'Considere usar min-width: 1px ou min-height: 1px';
      case 'invalid-unit':
        return 'Adicione um valor numérico antes da unidade';
      default:
        return null;
    }
  }
}

export const stylelintValidator = new StylelintValidator();

