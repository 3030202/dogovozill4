import React, { useState, useEffect } from 'react';
import { FileText, FolderOpen, RotateCcw, Zap, Sun, Moon } from 'lucide-react';

export default function Header({ onResetSample, onOpenDrafts, draftsCount = 0 }) {
  const [theme, setTheme] = useState(
    () => document.documentElement.getAttribute('data-theme') || 'light'
  );

  // Sync state with external theme changes
  useEffect(() => {
    const handler = (e) => setTheme(e.detail);
    window.addEventListener('docgen-theme-change', handler);
    return () => window.removeEventListener('docgen-theme-change', handler);
  }, []);

  const handleToggleTheme = () => {
    window.toggleDocgenTheme?.();
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const isDark = theme === 'dark';

  return (
    <header
      className="glass-panel animate-in"
      style={{
        padding: '14px 22px',
        marginBottom: '20px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        gap: '16px',
        flexWrap: 'wrap',
      }}
    >
      {/* ── Logo + H1 ────────────────────────────────────────────────── */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* Logo mark */}
        <div style={{
          width: '36px',
          height: '36px',
          borderRadius: '10px',
          background: 'linear-gradient(135deg, #6366f1 0%, #06b6d4 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
          boxShadow: isDark
            ? '0 0 16px rgba(99,102,241,0.3)'
            : '0 2px 8px rgba(99,102,241,0.25)',
          transition: 'transform 300ms var(--ease-spring)',
          cursor: 'default',
        }}
          onMouseEnter={e => e.currentTarget.style.transform = 'rotate(-10deg) scale(1.08)'}
          onMouseLeave={e => e.currentTarget.style.transform = ''}
        >
          <FileText size={20} color="#fff" />
        </div>

        {/* Brand name + tagline */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            {/* SEO H1 */}
            <h1 style={{
              fontSize: '18px',
              fontWeight: 800,
              fontFamily: 'var(--font-display)',
              letterSpacing: '-0.03em',
              lineHeight: 1,
            }}>
              <span className="gradient-text">DocGen</span>
            </h1>

            <span style={{
              height: '14px',
              width: '1px',
              background: 'var(--border)',
            }} />

            <span style={{
              fontSize: '13px',
              color: 'var(--text-secondary)',
              fontWeight: 500,
            }}>
              Генератор договоров РФ
            </span>

            <span className="badge badge-gost" style={{ fontFamily: 'var(--font-mono)' }}>
              ГОСТ Р 7.0.97
            </span>
            <span className="badge badge-valid">
              <Zap size={9} /> Zero-LLM
            </span>
          </div>

          <p style={{
            fontSize: '11.5px',
            color: 'var(--text-muted)',
            marginTop: '4px',
            letterSpacing: '0.01em',
          }}>
            7 типов · DOCX + PDF · ИНН / БИК / ОГРН · DaData
          </p>
        </div>
      </div>

      {/* ── Actions ──────────────────────────────────────────────────── */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <button
          className="btn btn-outline"
          onClick={onOpenDrafts}
          id="btn-open-drafts"
          aria-label="Открыть черновики"
        >
          <FolderOpen size={14} />
          <span>Черновики</span>
          {draftsCount > 0 && (
            <span style={{
              background: 'var(--accent)',
              color: '#fff',
              fontSize: '10px',
              fontWeight: 700,
              padding: '0 5px',
              borderRadius: 'var(--radius-pill)',
              lineHeight: '16px',
              height: '16px',
              minWidth: '16px',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              animation: 'countUp 0.3s var(--ease-spring)',
            }}>
              {draftsCount}
            </span>
          )}
        </button>

        <button
          className="btn btn-ghost"
          onClick={onResetSample}
          id="btn-reset-sample"
          aria-label="Загрузить пример данных"
          data-tooltip="Заполнить эталонными данными"
        >
          <RotateCcw size={14} />
          <span>Пример</span>
        </button>

        {/* ── Theme toggle ──────────────────────────────────────────── */}
        <button
          className="theme-toggle"
          onClick={handleToggleTheme}
          id="btn-theme-toggle"
          aria-label={isDark ? 'Переключить на светлую тему' : 'Переключить на тёмную тему'}
          data-tooltip={isDark ? 'Светлая тема' : 'Тёмная тема'}
          title={isDark ? 'Светлая тема' : 'Тёмная тема'}
        >
          <span className="icon-sun" aria-hidden="true">
            <Sun size={16} color="var(--accent)" />
          </span>
          <span className="icon-moon" aria-hidden="true">
            <Moon size={16} color="var(--accent)" />
          </span>
        </button>
      </div>
    </header>
  );
}
