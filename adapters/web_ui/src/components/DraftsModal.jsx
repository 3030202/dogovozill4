import React, { useEffect, useState } from 'react';
import { X, FolderOpen, Trash2, ArrowRight, Clock, FileText } from 'lucide-react';
import { listDrafts, deleteDraft } from '../api/client';

export default function DraftsModal({ isOpen, onClose, onSelectDraft }) {
  const [drafts, setDrafts] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadDraftsList = async () => {
    setLoading(true);
    try {
      const list = await listDrafts();
      setDrafts(list || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadDraftsList();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (window.confirm('Удалить этот черновик?')) {
      try {
        await deleteDraft(id);
        setDrafts(drafts.filter((d) => d.id !== id));
      } catch (err) {
        alert('Ошибка при удалении черновика');
      }
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        backdropFilter: 'blur(8px)',
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px',
      }}
      onClick={onClose}
    >
      <div
        className="glass-panel"
        style={{
          width: '100%',
          maxWidth: '650px',
          maxHeight: '80vh',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div
          style={{
            padding: '20px 24px',
            borderBottom: '1px solid var(--border-glass)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <FolderOpen size={22} color="var(--primary)" />
            <h2 style={{ fontSize: '18px', fontWeight: 700 }}>Сохраненные черновики</h2>
          </div>
          <button type="button" className="btn btn-outline" onClick={onClose} style={{ padding: '6px 10px' }}>
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <div style={{ padding: '20px 24px', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {loading && <p style={{ textAlign: 'center', color: 'var(--text-muted)' }}>Загрузка черновиков...</p>}

          {!loading && drafts.length === 0 && (
            <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)' }}>
              <FileText size={48} style={{ opacity: 0.3, marginBottom: '12px' }} />
              <p>Нет сохраненных черновиков</p>
              <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>
                Нажмите «Сохранить черновик» в правой панели редактора
              </span>
            </div>
          )}

          {!loading &&
            drafts.map((d) => (
              <div
                key={d.id}
                className="glass-card"
                style={{
                  padding: '16px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  cursor: 'pointer',
                }}
                onClick={() => onSelectDraft(d.id)}
              >
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span className="badge badge-law">{d.contract_type}</span>
                    <strong style={{ fontSize: '14px', color: '#fff' }}>{d.title}</strong>
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    {d.client_name ? `${d.client_name} ➔ ` : ''} {d.vendor_name || ''}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: 'var(--text-dim)', marginTop: '2px' }}>
                    <Clock size={12} />
                    <span>{d.updated_at_formatted}</span>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <button
                    type="button"
                    className="btn btn-outline"
                    onClick={(e) => handleDelete(d.id, e)}
                    style={{ padding: '6px 8px', color: 'var(--accent-rose)' }}
                    title="Удалить черновик"
                  >
                    <Trash2 size={16} />
                  </button>
                  <button type="button" className="btn btn-primary" style={{ padding: '6px 12px', fontSize: '13px' }}>
                    <span>Открыть</span>
                    <ArrowRight size={14} />
                  </button>
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}
