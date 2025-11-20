/**
 * Axe Validator
 * 
 * Usa axe-core para detectar problemas de acessibilidade
 */

import { run, AxeResults } from 'axe-core';

export interface AccessibilityIssue {
  id: string;
  description: string;
  help: string;
  helpUrl: string;
  impact: 'minor' | 'moderate' | 'serious' | 'critical';
  nodes: Array<{
    html: string;
    target: string[];
    failureSummary?: string;
  }>;
}

export class AxeValidator {
  /**
   * Executa análise de acessibilidade na página atual
   */
  async analyzePage(): Promise<AccessibilityIssue[]> {
    try {
      const results: AxeResults = await run(document);
      
      const issues: AccessibilityIssue[] = results.violations.map(violation => ({
        id: violation.id,
        description: violation.description,
        help: violation.help,
        helpUrl: violation.helpUrl,
        impact: violation.impact as AccessibilityIssue['impact'],
        nodes: violation.nodes.map(node => ({
          html: node.html,
          target: node.target,
          failureSummary: node.failureSummary
        }))
      }));
      
      return issues;
    } catch (error) {
      console.error('Erro ao executar análise axe-core:', error);
      return [];
    }
  }

  /**
   * Analisa um elemento específico
   */
  async analyzeElement(element: HTMLElement): Promise<AccessibilityIssue[]> {
    try {
      const results: AxeResults = await run(element);
      
      const issues: AccessibilityIssue[] = results.violations.map(violation => ({
        id: violation.id,
        description: violation.description,
        help: violation.help,
        helpUrl: violation.helpUrl,
        impact: violation.impact as AccessibilityIssue['impact'],
        nodes: violation.nodes.map(node => ({
          html: node.html,
          target: node.target,
          failureSummary: node.failureSummary
        }))
      }));
      
      return issues;
    } catch (error) {
      console.error('Erro ao analisar elemento com axe-core:', error);
      return [];
    }
  }

  /**
   * Converte issues do axe em formato compatível com ForgeLogs
   */
  convertToUIIssues(issues: AccessibilityIssue[]): Array<{
    type: string;
    severity: 'low' | 'medium' | 'high';
    message: string;
    element?: string;
    details: Record<string, any>;
  }> {
    const severityMap: Record<string, 'low' | 'medium' | 'high'> = {
      'minor': 'low',
      'moderate': 'medium',
      'serious': 'high',
      'critical': 'high'
    };

    return issues.flatMap(issue => 
      issue.nodes.map(node => ({
        type: `accessibility_${issue.id}`,
        severity: severityMap[issue.impact] || 'medium',
        message: issue.description,
        element: node.target.join(' '),
        details: {
          help: issue.help,
          helpUrl: issue.helpUrl,
          html: node.html,
          failureSummary: node.failureSummary
        }
      }))
    );
  }
}

export const axeValidator = new AxeValidator();

