/**
 * Fix Injector Script
 * 
 * Script standalone para injetar em outras aplicações
 * Uso: <script src="http://localhost:3001/fix-injector.js"></script>
 */

(function() {
  'use strict';

  const CONFIG = {
    apiUrl: 'http://localhost:8003',
    applicationId: 'forgetest-studio',
    autoApply: true,
    pollInterval: 30000
  };

  // Aplicar configuração do window se disponível
  if (window.FORGE_EXPERIENCE_DESIGN_CONFIG) {
    Object.assign(CONFIG, window.FORGE_EXPERIENCE_DESIGN_CONFIG);
  }

  class FixApplier {
    constructor() {
      this.appliedFixes = new Map();
      this.styleElement = null;
    }

    applyFix(fix) {
      try {
        if (fix.type === 'css') {
          return this.applyCSSFix(fix);
        }
        return false;
      } catch (error) {
        console.error('Error applying fix:', error);
        return false;
      }
    }

    applyCSSFix(fix) {
      if (!this.styleElement) {
        this.styleElement = document.createElement('style');
        this.styleElement.id = 'forge-experience-design-fixes';
        document.head.appendChild(this.styleElement);
      }

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

      this.styleElement.textContent += css;
      fix.status = 'applied';
      this.appliedFixes.set(fix.id, fix);

      return true;
    }

    rollbackFix(fixId) {
      const fix = this.appliedFixes.get(fixId);
      if (!fix) {
        return false;
      }

      if (this.styleElement && fix.type === 'css') {
        const currentCSS = this.styleElement.textContent || '';
        const fixCSS = currentCSS.split(`/* Fix: ${fix.id} */`)[0] + 
                      (currentCSS.split(`/* Fix: ${fix.id} */`)[1]?.split('}')[1] || '');
        this.styleElement.textContent = fixCSS;
      }

      fix.status = 'rolled_back';
      this.appliedFixes.delete(fixId);
      return true;
    }

    clearAll() {
      if (this.styleElement) {
        this.styleElement.remove();
        this.styleElement = null;
      }
      this.appliedFixes.clear();
    }
  }

  class FixInjector {
    constructor(config) {
      this.config = config;
      this.fixApplier = new FixApplier();
      this.pollIntervalId = null;
      this.appliedFixIds = new Set();
    }

    start() {
      if (this.pollIntervalId !== null) {
        console.warn('FixInjector já está rodando');
        return;
      }

      console.log('ForgeExperienceDesign: FixInjector iniciado', this.config);
      this.fetchAndApplyFixes();
      this.pollIntervalId = setInterval(() => {
        this.fetchAndApplyFixes();
      }, this.config.pollInterval);
    }

    stop() {
      if (this.pollIntervalId !== null) {
        clearInterval(this.pollIntervalId);
        this.pollIntervalId = null;
        console.log('ForgeExperienceDesign: FixInjector parado');
      }
    }

    async fetchAndApplyFixes() {
      try {
        const response = await fetch(
          `${this.config.apiUrl}/api/fixes/generate?application_id=${this.config.applicationId}&limit=50`
        );

        if (!response.ok) {
          return;
        }

        const fixes = await response.json();
        const pendingFixes = fixes.filter(
          fix => fix.status === 'pending' && !this.appliedFixIds.has(fix.id)
        );

        if (pendingFixes.length === 0) {
          return;
        }

        console.log(`ForgeExperienceDesign: Aplicando ${pendingFixes.length} correções`);

        for (const fix of pendingFixes) {
          if (this.config.autoApply) {
            const applied = this.fixApplier.applyFix(fix);
            if (applied) {
              this.appliedFixIds.add(fix.id);
              console.log(`ForgeExperienceDesign: Correção aplicada: ${fix.id}`);
            }
          }
        }
      } catch (error) {
        console.error('ForgeExperienceDesign: Erro ao buscar/aplicar correções:', error);
      }
    }

    applyFix(fix) {
      const applied = this.fixApplier.applyFix(fix);
      if (applied) {
        this.appliedFixIds.add(fix.id);
      }
      return applied;
    }

    rollbackFix(fixId) {
      const rolledBack = this.fixApplier.rollbackFix(fixId);
      if (rolledBack) {
        this.appliedFixIds.delete(fixId);
      }
      return rolledBack;
    }

    clearAll() {
      this.fixApplier.clearAll();
      this.appliedFixIds.clear();
    }
  }

  // Criar e iniciar injector
  const injector = new FixInjector(CONFIG);
  
  // Expor globalmente
  window.forgeExperienceDesign = {
    injector: injector,
    start: () => injector.start(),
    stop: () => injector.stop(),
    applyFix: (fix) => injector.applyFix(fix),
    rollbackFix: (fixId) => injector.rollbackFix(fixId),
    clearAll: () => injector.clearAll()
  };

  // Iniciar automaticamente
  if (CONFIG.autoApply) {
    injector.start();
  }

  console.log('ForgeExperienceDesign: Script carregado e pronto');
})();

