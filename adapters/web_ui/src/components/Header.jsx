import React from 'react';
import { FileText, Shield, Sparkles, FolderOpen, RotateCcw } from 'lucide-react';

export default function Header({ onResetSample, onOpenDrafts, draftsCount = 0 }) {
  return (
    <header className="glass-panel" style={{ padding: '16px 24px', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{
          width: '44px',
          height: '44px',
          borderRadius: '12px',
          background: 'linear-gradient(135deg, #6366f1 0%, #06b6d4 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 20px rgba(99, 102, 241, 0.4)'
        }}>
          <FileText size={24} color="#ffffff" />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h1 style={{ fontSize: '20px', fontWeight: 800 }}>DocGen Omnichannel</h1>
            <span className="badge badge-gost">ГОСТ Р 7.0.97-2016</span>
            <span className="badge badge-valid">Zero-LLM Runtime</span>
          </div>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '2px' }}>
            Детерминированная омниканальная платформа сборки договоров РФ
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <button 
          className="btn btn-outline" 
          onClick={onOpenDrafts}
          title="Открыть сохраненные черновики"
        >
          <FolderOpen size={16} />
          <span>Черновики</span>
          {draftsCount > 0 && (
            <span style={{ background: 'var(--primary)', color: '#fff', fontSize: '11px', padding: '1px 6px', borderRadius: '10px' }}>
              {draftsCount}
            </span>
          )}
        </button>

        <button 
          className="btn btn-secondary" 
          onClick={onResetSample}
          title="Заполнить эталонными юридическими данными"
        >
          <RotateCcw size={16} />
          <span>Заполнить пример</span>
        </button>
      </div>
    </header>
  );
}
