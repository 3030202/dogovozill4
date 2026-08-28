import React, { useState, useEffect } from 'react';
import {
  FileText, Truck, Briefcase, Hammer, ShieldCheck,
  Download, Save, CheckCircle2, FileCode, Layers,
  Building, CreditCard, Scale, KeyRound, Monitor, UserCheck,
  Sun, Moon, FolderOpen, RotateCcw, ChevronRight, Zap, Check,
} from 'lucide-react';

import PartyCard from './components/PartyCard';
import SpecificationEditor from './components/SpecificationEditor';
import DraftsModal from './components/DraftsModal';

import {
  fetchContractTypes, fetchSampleContract, calculateFinancials,
  downloadDocx, downloadPdf, saveDraft, getDraft, listDrafts,
} from './api/client';

// ── Contract type metadata ─────────────────────────────────────────────
const TYPE_ICONS = {
  supply: <Truck size={13} />,
  services: <Briefcase size={13} />,
  work: <Hammer size={13} />,
  nda: <ShieldCheck size={13} />,
  lease: <KeyRound size={13} />,
  license_sw: <Monitor size={13} />,
  freelance: <UserCheck size={13} />,
};

// ── Pipeline steps ────────────────────────────────────────────────────
const STEPS = [
  { id: 'parties',  label: 'Стороны',       icon: <Building size={12} /> },
  { id: 'spec',     label: 'Предмет',        icon: <Layers size={12} /> },
  { id: 'terms',    label: 'Оплата',         icon: <CreditCard size={12} /> },
];

// ── Stance options ─────────────────────────────────────────────────────
const STANCES = [
  { key: 'pro_buyer',  label: 'Pro-Заказчик' },
  { key: 'balanced',   label: 'Нейтрально'   },
  { key: 'pro_vendor', label: 'Pro-Исполн.'  },
];

// ── Theme Toggle ──────────────────────────────────────────────────────
function ThemeToggle() {
  const [theme, setTheme] = useState(
    () => document.documentElement.getAttribute('data-theme') || 'dark'
  );
  useEffect(() => {
    const h = (e) => setTheme(e.detail);
    window.addEventListener('docgen-theme-change', h);
    return () => window.removeEventListener('docgen-theme-change', h);
  }, []);
  const toggle = () => { window.toggleDocgenTheme?.(); setTheme(t => t === 'dark' ? 'light' : 'dark'); };
  return (
    <button className="theme-toggle" onClick={toggle}
      aria-label={theme === 'dark' ? 'Светлая тема' : 'Тёмная тема'}>
      <span className="icon-sun"><Sun size={13} /></span>
      <span className="icon-moon"><Moon size={13} /></span>
    </button>
  );
}

// ── Main App ──────────────────────────────────────────────────────────
export default function App() {
  const [contractTypes, setContractTypes] = useState([]);
  const [selectedType, setSelectedType]   = useState('supply');
  const [contractData, setContractData]   = useState(null);
  const [activeStep, setActiveStep]       = useState('parties');
  const [legalStance, setLegalStance]     = useState('balanced');

  const [calcResult, setCalcResult]             = useState(null);
  const [isDownloadingDocx, setIsDownloadingDocx] = useState(false);
  const [isDownloadingPdf, setIsDownloadingPdf]   = useState(false);
  const [isSavingDraft, setIsSavingDraft]         = useState(false);
  const [draftsCount, setDraftsCount]             = useState(0);
  const [isDraftsModalOpen, setIsDraftsModalOpen] = useState(false);
  const [notification, setNotification]           = useState(null);

  // ── Init ──────────────────────────────────────────────────────────
  useEffect(() => {
    fetchContractTypes().then(setContractTypes).catch(console.error);
    loadSample('supply');
    listDrafts().then(l => setDraftsCount(l?.length || 0)).catch(() => {});
  }, []);

  // ── Auto-calc ─────────────────────────────────────────────────────
  useEffect(() => {
    if (!contractData) return;
    let total = 0;
    if (selectedType === 'supply' && contractData.items)
      total = contractData.items.reduce((s, i) => s + (parseFloat(i.quantity) || 0) * (parseFloat(i.price_per_unit) || 0), 0);
    else if (selectedType === 'services' && contractData.services)
      total = contractData.services.reduce((s, i) => s + (parseFloat(i.price) || 0), 0);
    else if (selectedType === 'work' && contractData.stages)
      total = contractData.stages.reduce((s, i) => s + (parseFloat(i.cost) || 0), 0);
    else if (selectedType === 'lease' && contractData.lease_terms)
      total = (parseFloat(contractData.lease_terms.monthly_rent_rubles) || 0) * (parseInt(contractData.lease_terms.rent_period_months) || 1);
    else if (selectedType === 'license_sw')
      total = parseFloat(contractData.license_fee) || 0;
    else if (selectedType === 'freelance' && contractData.tasks)
      total = contractData.tasks.reduce((s, t) => s + (parseFloat(t.cost) || 0), 0);

    const pay = contractData.payment_terms || {};
    const adv = pay.type === '50_50' ? pay.advance_percent || 50 : 0;
    calculateFinancials({
      total_amount: total, vat_rate: contractData.vat_rate ?? 20,
      vat_included: contractData.vat_included ?? true,
      is_exempt_vat: contractData.is_exempt_vat ?? false,
      advance_percent: adv,
    }).then(setCalcResult).catch(console.error);
  }, [contractData, selectedType]);

  // ── Helpers ───────────────────────────────────────────────────────
  const showNotif = (msg, type = 'success') => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 3200);
  };

  const loadSample = async (type) => {
    try {
      const s = await fetchSampleContract(type);
      setContractData(s);
      setSelectedType(type);
    } catch (e) { console.error(e); }
  };

  const handleTypeChange = (type) => { loadSample(type); setActiveStep('parties'); };

  const handleMetadataChange = (field, val) =>
    setContractData(p => ({ ...p, metadata: { ...(p?.metadata || {}), [field]: val } }));

  const handlePartyChange = (key, val) => setContractData(p => ({ ...p, [key]: val }));

  const handlePaymentChange = (field, val) =>
    setContractData(p => ({ ...p, payment_terms: { ...(p?.payment_terms || {}), [field]: val } }));

  const handleStanceChange = (stance) => {
    setLegalStance(stance);
    setContractData(p => ({ ...p, legal_stance: stance }));
  };

  const handleDownloadDocx = async () => {
    setIsDownloadingDocx(true);
    try { await downloadDocx(selectedType, contractData); showNotif('DOCX сформирован по ГОСТ Р 7.0.97'); }
    catch (e) { showNotif(e.message, 'error'); }
    finally { setIsDownloadingDocx(false); }
  };

  const handleDownloadPdf = async () => {
    setIsDownloadingPdf(true);
    try { await downloadPdf(selectedType, contractData); showNotif('PDF сформирован'); }
    catch (e) { showNotif(e.message, 'error'); }
    finally { setIsDownloadingPdf(false); }
  };

  const handleSaveDraft = async () => {
    setIsSavingDraft(true);
    try {
      const title = `${selectedType.toUpperCase()} № ${contractData?.metadata?.contract_number || 'б/н'}`;
      await saveDraft(selectedType, contractData, title);
      showNotif('Черновик сохранён');
      listDrafts().then(l => setDraftsCount(l?.length || 0)).catch(() => {});
    } catch (e) { showNotif(e.message, 'error'); }
    finally { setIsSavingDraft(false); }
  };

  const handleSelectDraft = async (id) => {
    try {
      const d = await getDraft(id);
      if (d?.data) { setSelectedType(d.contract_type || 'supply'); setContractData(d.data); setIsDraftsModalOpen(false); showNotif(`Черновик «${d.title}» загружен`); }
    } catch { showNotif('Не удалось загрузить черновик', 'error'); }
  };

  // ── Loading state ─────────────────────────────────────────────────
  if (!contractData) {
    return (
      <div className="app-shell" style={{ alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
          <FileText size={28} color="var(--c-tx-3)" />
          <div className="loading-bar" style={{ width: '120px' }} />
          <span style={{ fontSize: '12px', color: 'var(--c-tx-3)' }}>Инициализация…</span>
        </div>
      </div>
    );
  }

  const meta    = contractData.metadata || {};
  const payment = contractData.payment_terms || {};
  const currentType = contractTypes.find(t => t.key === selectedType);

  // Sidebar step completion flags
  const stepsDone = {
    parties: !!(contractData.client?.name && contractData.vendor?.name),
    spec: true,
    terms: true,
  };

  return (
    <div className="app-shell">
      {/* ══════════════════════════════════════════════════════════════
          SIDEBAR
      ══════════════════════════════════════════════════════════════ */}
      <aside className="sidebar">
        {/* Sidebar header - Logo */}
        <div className="sidebar-header">
          <div style={{
            width: 28, height: 28, borderRadius: 6,
            background: 'linear-gradient(135deg, #6366f1, #06b6d4)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
          }}>
            <FileText size={15} color="#fff" />
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 13, fontWeight: 800, fontFamily: 'var(--font-head)', letterSpacing: '-0.02em', color: 'var(--c-tx)', lineHeight: 1 }}>
              DocGen
            </div>
            <div style={{ fontSize: 10, color: 'var(--c-tx-3)', marginTop: 2, fontFamily: 'var(--font-mono)' }}>
              Zero-LLM · ГОСТ Р 7.0.97
            </div>
          </div>
          <ThemeToggle />
        </div>

        {/* Sidebar body - scrollable */}
        <div className="sidebar-body">
          {/* ── Contract Type Picker ── */}
          <div className="sidebar-section-label">Тип договора</div>
          <div className="type-chip-grid">
            {contractTypes.map(t => (
              <button
                key={t.key}
                className={`type-chip${selectedType === t.key ? ' selected' : ''} animate-in stagger-item`}
                onClick={() => handleTypeChange(t.key)}
                title={t.title}
              >
                <span className="type-chip-icon">{TYPE_ICONS[t.key] || <FileText size={13} />}</span>
                <span className="type-chip-text">
                  <div className="type-chip-name">{t.title}</div>
                  <div className="type-chip-law">{t.law_reference}</div>
                </span>
                {selectedType === t.key && <Check size={11} color="var(--c-tx-2)" />}
              </button>
            ))}
          </div>

          <div className="divider" style={{ margin: '12px 16px' }} />

          {/* ── Pipeline Steps ── */}
          <div className="sidebar-section-label">Заполнение</div>
          <div className="pipeline-nav">
            {STEPS.map((step, idx) => (
              <React.Fragment key={step.id}>
                <div
                  className={`pipeline-step${activeStep === step.id ? ' active' : ''}${stepsDone[step.id] && activeStep !== step.id ? ' done' : ''}`}
                  onClick={() => setActiveStep(step.id)}
                >
                  <span className="pipeline-step-num">
                    {stepsDone[step.id] && activeStep !== step.id
                      ? <Check size={10} />
                      : idx + 1}
                  </span>
                  <span className="pipeline-step-label">{step.label}</span>
                </div>
                {idx < STEPS.length - 1 && <div className="pipeline-connector" />}
              </React.Fragment>
            ))}
          </div>

          <div className="divider" style={{ margin: '12px 16px' }} />

          {/* ── Legal Stance ── */}
          <div className="sidebar-section-label">Юр. позиция</div>
          <div style={{ padding: '0 8px', display: 'flex', flexDirection: 'column', gap: 1 }}>
            {STANCES.map(s => (
              <button
                key={s.key}
                onClick={() => handleStanceChange(s.key)}
                style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  padding: '6px 8px', borderRadius: 'var(--r-md)', border: 'none',
                  background: legalStance === s.key ? 'var(--c-ac-sub)' : 'transparent',
                  cursor: 'pointer', fontFamily: 'var(--font-ui)', width: '100%',
                  transition: 'background var(--t-fast)',
                  outline: legalStance === s.key ? '1px solid var(--c-ac-border)' : 'none',
                  outlineOffset: -1,
                }}
              >
                <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--c-tx)' }}>{s.label}</span>
                {legalStance === s.key && <Check size={11} color="var(--c-tx-2)" />}
              </button>
            ))}
          </div>

          <div className="divider" style={{ margin: '12px 16px' }} />

          {/* ── Summary Stats ── */}
          <div className="sidebar-section-label">Сумма</div>
          <div className="stat-row" style={{ marginBottom: 0 }}>
            <div className="stat-cell">
              <div className="stat-label">Итого</div>
              <div className="stat-value" style={{ fontSize: 14 }}>
                {calcResult?.total_formatted || '—'}
              </div>
              <div className="stat-sub">руб.</div>
            </div>
            <div className="stat-cell">
              <div className="stat-label">{contractData.is_exempt_vat ? 'НДС' : `НДС ${contractData.vat_rate || 20}%`}</div>
              <div className="stat-value" style={{ fontSize: 14 }}>
                {contractData.is_exempt_vat ? 'н/о' : (calcResult?.vat_formatted || '—')}
              </div>
              <div className="stat-sub">{contractData.is_exempt_vat ? 'УСН' : 'руб.'}</div>
            </div>
          </div>
        </div>

        {/* Sidebar footer - actions */}
        <div className="sidebar-footer">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <button className="btn btn-primary btn-full" onClick={handleDownloadDocx} disabled={isDownloadingDocx}>
              <Download size={13} />
              {isDownloadingDocx ? 'Генерация…' : 'Скачать DOCX'}
            </button>
            <button className="btn btn-outline btn-full" onClick={handleDownloadPdf} disabled={isDownloadingPdf}>
              <FileCode size={13} />
              {isDownloadingPdf ? 'Компиляция…' : 'Скачать PDF'}
            </button>
            <div style={{ display: 'flex', gap: 6 }}>
              <button className="btn btn-ghost" style={{ flex: 1, height: 30 }} onClick={handleSaveDraft} disabled={isSavingDraft}>
                <Save size={12} />{isSavingDraft ? '…' : 'Сохранить'}
              </button>
              <button className="btn btn-ghost" style={{ flex: 1, height: 30 }} onClick={() => setIsDraftsModalOpen(true)}>
                <FolderOpen size={12} />
                <span>Черновики</span>
                {draftsCount > 0 && (
                  <span style={{ background: 'var(--c-ac)', color: 'var(--c-tx-inv)', fontSize: 9, padding: '0 4px', borderRadius: 99, lineHeight: '14px', fontWeight: 700 }}>
                    {draftsCount}
                  </span>
                )}
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* ══════════════════════════════════════════════════════════════
          MAIN AREA
      ══════════════════════════════════════════════════════════════ */}
      <div className="main-area">
        {/* ── Topbar ── */}
        <div className="topbar">
          {/* Breadcrumb + pipeline stepper */}
          <span style={{ fontSize: 11, color: 'var(--c-tx-3)', fontFamily: 'var(--font-mono)', whiteSpace: 'nowrap', flexShrink: 0 }}>
            {currentType?.title || selectedType}
          </span>
          <ChevronRight size={12} color="var(--c-tx-3)" />

          {/* Step tabs */}
          <div className="topbar-stepper">
            {STEPS.map((step, idx) => (
              <React.Fragment key={step.id}>
                <button
                  className={`topbar-step${activeStep === step.id ? ' active' : ''}${stepsDone[step.id] && activeStep !== step.id ? ' done' : ''}`}
                  onClick={() => setActiveStep(step.id)}
                >
                  <span className="topbar-step-n">
                    {stepsDone[step.id] && activeStep !== step.id ? '✓' : idx + 1}
                  </span>
                  <span className="topbar-step-label">{step.label}</span>
                </button>
                {idx < STEPS.length - 1 && <span className="topbar-sep" />}
              </React.Fragment>
            ))}
          </div>

          <div style={{ flex: 1 }} />

          {/* Legal wording chip */}
          {calcResult?.legal_wording && (
            <div style={{
              fontSize: 10, color: 'var(--c-tx-3)', fontFamily: 'var(--font-mono)',
              maxWidth: 260, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
              background: 'var(--c-bg-2)', padding: '2px 8px', borderRadius: 'var(--r-pill)',
              border: '1px solid var(--c-line)',
            }} title={calcResult.legal_wording}>
              {calcResult.legal_wording}
            </div>
          )}

          <button className="btn btn-ghost" onClick={() => loadSample(selectedType)} style={{ flexShrink: 0, fontSize: 11, height: 26, gap: 4 }}>
            <RotateCcw size={11} />Сброс
          </button>
        </div>

        {/* ── Meta bar ── */}
        <div style={{ borderBottom: '1px solid var(--c-line)', padding: '0 20px' }}>
          <div className="meta-bar" style={{ margin: '12px 0' }}>
            {[
              { label: '№ договора',   field: 'contract_number', ph: '2025/П-01' },
              { label: 'Дата',         field: 'contract_date',   ph: '15.02.2025' },
              { label: 'Город',        field: 'city',            ph: 'г. Москва'  },
              { label: 'Действует до', field: 'valid_until',     ph: '31.12.2025' },
            ].map(f => (
              <div key={f.field} className="meta-cell">
                <div className="meta-cell-label">{f.label}</div>
                <input
                  type="text"
                  value={meta[f.field] || ''}
                  onChange={e => handleMetadataChange(f.field, e.target.value)}
                  placeholder={f.ph}
                  style={{
                    background: 'transparent', border: 'none', outline: 'none',
                    color: 'var(--c-tx)', fontSize: 13, fontWeight: 600, width: '100%',
                    fontFamily: 'var(--font-ui)', padding: 0,
                  }}
                />
              </div>
            ))}
          </div>
        </div>

        {/* ── Content area ── */}
        <div className="content-area">
          {/* Toast */}
          {notification && (
            <div className="animate-slide-in" role="alert" aria-live="polite" style={{
              position: 'fixed', bottom: 24, right: 24,
              background: notification.type === 'success' ? 'var(--c-ok)' : 'var(--c-err)',
              color: '#fff', padding: '8px 16px', borderRadius: 'var(--r-md)',
              fontSize: 13, fontWeight: 600, zIndex: 2000,
              display: 'flex', alignItems: 'center', gap: 8,
              boxShadow: 'var(--c-shadow-lg)',
            }}>
              <CheckCircle2 size={15} />{notification.msg}
            </div>
          )}

          {/* ── STEP: Parties ── */}
          {activeStep === 'parties' && (
            <div className="animate-in" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <PartyCard
                title="Заказчик / Покупатель"
                roleBadge="Заказчик"
                party={contractData.client || {}}
                onChange={p => handlePartyChange('client', p)}
              />
              <PartyCard
                title="Исполнитель / Поставщик"
                roleBadge="Исполнитель"
                party={contractData.vendor || {}}
                onChange={p => handlePartyChange('vendor', p)}
              />
            </div>
          )}

          {/* ── STEP: Specification ── */}
          {activeStep === 'spec' && (
            <div className="animate-in">
              <SpecificationEditor
                contractType={selectedType}
                data={contractData}
                onChange={setContractData}
              />
            </div>
          )}

          {/* ── STEP: Payment & Terms ── */}
          {activeStep === 'terms' && (
            <div className="animate-in" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, alignItems: 'start' }}>
              {/* Payment */}
              <div className="panel">
                <div className="panel-header">
                  <span className="panel-title">Условия оплаты</span>
                  <CreditCard size={14} color="var(--c-tx-3)" />
                </div>
                <div className="panel-body">
                  <div className="grid-2">
                    <div className="form-group">
                      <label className="form-label">График расчётов</label>
                      <select className="form-select" value={payment.type || '100_POSTPAYMENT'} onChange={e => handlePaymentChange('type', e.target.value)}>
                        <option value="100_POSTPAYMENT">100% Постоплата</option>
                        <option value="50_50">50% / 50% (аванс)</option>
                        <option value="100_PREPAYMENT">100% Предоплата</option>
                      </select>
                    </div>
                    <div className="form-group">
                      <label className="form-label">Срок оплаты (дн.)</label>
                      <input type="number" className="form-input" value={payment.postpayment_days || 5} onChange={e => handlePaymentChange('postpayment_days', parseInt(e.target.value) || 1)} />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Тип дней</label>
                      <select className="form-select" value={payment.days_type || 'banking'} onChange={e => handlePaymentChange('days_type', e.target.value)}>
                        <option value="banking">Банковские</option>
                        <option value="calendar">Календарные</option>
                      </select>
                    </div>
                    <div className="form-group">
                      <label className="form-label">НДС</label>
                      <select className="form-select"
                        value={contractData.is_exempt_vat ? 'exempt' : contractData.vat_rate === 10 ? '10' : '20'}
                        onChange={e => {
                          if (e.target.value === 'exempt') setContractData(p => ({ ...p, is_exempt_vat: true, vat_rate: 0 }));
                          else setContractData(p => ({ ...p, is_exempt_vat: false, vat_rate: parseInt(e.target.value), vat_included: true }));
                        }}
                      >
                        <option value="20">НДС 20%</option>
                        <option value="10">НДС 10%</option>
                        <option value="exempt">Без НДС (УСН)</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>

              {/* Disputes */}
              <div className="panel">
                <div className="panel-header">
                  <span className="panel-title">Ответственность и споры</span>
                  <Scale size={14} color="var(--c-tx-3)" />
                </div>
                <div className="panel-body">
                  <div className="grid-2">
                    <div className="form-group">
                      <label className="form-label">Срок ответа на претензию</label>
                      <input type="number" className="form-input"
                        value={contractData.dispute_resolution?.pre_trial_claim_days || 30}
                        onChange={e => setContractData(p => ({ ...p, dispute_resolution: { ...(p.dispute_resolution || {}), pre_trial_claim_days: parseInt(e.target.value) || 0 } }))}
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Подсудность</label>
                      <select className="form-select"
                        value={contractData.dispute_resolution?.court_jurisdiction || 'arbitration_plaintiff'}
                        onChange={e => setContractData(p => ({ ...p, dispute_resolution: { ...(p.dispute_resolution || {}), court_jurisdiction: e.target.value } }))}
                      >
                        <option value="arbitration_plaintiff">АС по месту Истца</option>
                        <option value="arbitration_defendant">АС по месту Ответчика</option>
                        <option value="moscow">АС города Москвы</option>
                      </select>
                    </div>
                  </div>

                  {/* Compliance */}
                  <div style={{ marginTop: 8, padding: '10px 12px', background: 'var(--c-bg-2)', borderRadius: 'var(--r-md)', border: '1px solid var(--c-line)' }}>
                    <div className="kv-table">
                      {[
                        ['ГОСТ Р 7.0.97-2016', 'поля 25/15/20/20'],
                        ['cantSplit таблицы',  'включено'],
                        ['ФНС / ЦБ РФ чексум', 'ИНН + БИК'],
                        ['LLM', 'Zero-LLM'],
                      ].map(([k, v]) => (
                        <div key={k} className="kv-row">
                          <span className="kv-key">{k}</span>
                          <span className="kv-val" style={{ color: 'var(--c-ok)' }}>✓ {v}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Financial detail */}
              {calcResult && (
                <div className="panel span-2">
                  <div className="panel-header">
                    <span className="panel-title">Финансовый расчёт</span>
                    <Zap size={13} color="var(--c-tx-3)" />
                  </div>
                  <div className="panel-body">
                    <div className="grid-4">
                      {[
                        { label: 'Сумма договора',  val: `${calcResult.total_formatted} ₽` },
                        { label: `НДС ${contractData.is_exempt_vat ? '(без НДС)' : contractData.vat_rate + '%'}`, val: contractData.is_exempt_vat ? 'Не облагается' : `${calcResult.vat_formatted} ₽` },
                        { label: 'Без НДС',          val: calcResult.subtotal_formatted ? `${calcResult.subtotal_formatted} ₽` : '—' },
                        { label: 'Аванс',             val: calcResult.advance_amount > 0 ? `${calcResult.advance_amount.toLocaleString('ru-RU', { minimumFractionDigits: 2 })} ₽` : 'Нет' },
                      ].map(({ label, val }) => (
                        <div key={label} style={{ padding: '10px 12px', background: 'var(--c-bg-2)', borderRadius: 'var(--r-md)', border: '1px solid var(--c-line)' }}>
                          <div className="stat-label">{label}</div>
                          <div className="stat-value" style={{ fontSize: 13, marginTop: 4 }}>{val}</div>
                        </div>
                      ))}
                    </div>
                    {calcResult.legal_wording && (
                      <div style={{ marginTop: 10, fontSize: 11, color: 'var(--c-tx-3)', fontFamily: 'var(--font-mono)', padding: '8px 10px', background: 'var(--c-bg-2)', borderRadius: 'var(--r-md)', border: '1px solid var(--c-line)' }}>
                        <span style={{ color: 'var(--c-warn)', fontWeight: 700 }}>Прописью: </span>{calcResult.legal_wording}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Drafts modal */}
      <DraftsModal isOpen={isDraftsModalOpen} onClose={() => setIsDraftsModalOpen(false)} onSelectDraft={handleSelectDraft} />
    </div>
  );
}
