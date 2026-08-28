import React, { useState, useEffect } from 'react';
import {
  FileText,
  Truck,
  Briefcase,
  Hammer,
  ShieldCheck,
  Download,
  Save,
  CheckCircle2,
  AlertTriangle,
  FileCode,
  Layers,
  FileCheck2,
  Building,
  CreditCard,
  Scale,
  Sparkles,
} from 'lucide-react';

import Header from './components/Header';
import PartyCard from './components/PartyCard';
import SpecificationEditor from './components/SpecificationEditor';
import DraftsModal from './components/DraftsModal';

import {
  fetchContractTypes,
  fetchSampleContract,
  calculateFinancials,
  downloadDocx,
  downloadPdf,
  saveDraft,
  getDraft,
  listDrafts,
} from './api/client';

export default function App() {
  const [contractTypes, setContractTypes] = useState([]);
  const [selectedType, setSelectedType] = useState('supply');
  const [contractData, setContractData] = useState(null);
  const [activeTab, setActiveTab] = useState('parties');

  const [calcResult, setCalcResult] = useState(null);
  const [isDownloadingDocx, setIsDownloadingDocx] = useState(false);
  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);
  const [isSavingDraft, setIsSavingDraft] = useState(false);
  const [draftsCount, setDraftsCount] = useState(0);
  const [isDraftsModalOpen, setIsDraftsModalOpen] = useState(false);
  const [notification, setNotification] = useState(null);

  // Load contract types on mount
  useEffect(() => {
    fetchContractTypes()
      .then((types) => setContractTypes(types))
      .catch((err) => console.error(err));
    loadSample('supply');
    updateDraftsCount();
  }, []);

  const updateDraftsCount = async () => {
    try {
      const list = await listDrafts();
      setDraftsCount(list?.length || 0);
    } catch (e) {
      // ignore
    }
  };

  const showNotification = (msg, type = 'success') => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 3500);
  };

  const loadSample = async (type) => {
    try {
      const sample = await fetchSampleContract(type);
      setContractData(sample);
      setSelectedType(type);
    } catch (e) {
      console.error(e);
    }
  };

  const handleTypeChange = (type) => {
    setSelectedType(type);
    loadSample(type);
  };

  // Recalculate sums and legal wording whenever contractData changes
  useEffect(() => {
    if (!contractData) return;

    let total = 0;
    if (selectedType === 'supply' && contractData.items) {
      total = contractData.items.reduce(
        (sum, item) => sum + (parseFloat(item.quantity) || 0) * (parseFloat(item.price_per_unit) || 0),
        0
      );
    } else if (selectedType === 'services' && contractData.services) {
      total = contractData.services.reduce((sum, s) => sum + (parseFloat(s.price) || 0), 0);
    } else if (selectedType === 'work' && contractData.stages) {
      total = contractData.stages.reduce((sum, st) => sum + (parseFloat(st.cost) || 0), 0);
    }

    const pay = contractData.payment_terms || {};
    const advPercent = pay.type === '50_50' ? pay.advance_percent || 50 : 0;

    calculateFinancials({
      total_amount: total,
      vat_rate: contractData.vat_rate ?? 20,
      vat_included: contractData.vat_included ?? true,
      is_exempt_vat: contractData.is_exempt_vat ?? false,
      advance_percent: advPercent,
    })
      .then((res) => setCalcResult(res))
      .catch((e) => console.error(e));
  }, [contractData, selectedType]);

  const handleMetadataChange = (field, value) => {
    setContractData((prev) => ({
      ...prev,
      metadata: {
        ...(prev?.metadata || {}),
        [field]: value,
      },
    }));
  };

  const handlePartyChange = (partyKey, updatedParty) => {
    setContractData((prev) => ({
      ...prev,
      [partyKey]: updatedParty,
    }));
  };

  const handleTermsChange = (field, value) => {
    setContractData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handlePaymentTermsChange = (field, value) => {
    setContractData((prev) => ({
      ...prev,
      payment_terms: {
        ...(prev?.payment_terms || {}),
        [field]: value,
      },
    }));
  };

  const handleDownloadDocx = async () => {
    if (!contractData) return;
    setIsDownloadingDocx(true);
    try {
      await downloadDocx(selectedType, contractData);
      showNotification('Документ DOCX успешно сформирован по ГОСТ Р 7.0.97-2016!');
    } catch (err) {
      alert(`Ошибка: ${err.message}`);
    } finally {
      setIsDownloadingDocx(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!contractData) return;
    setIsDownloadingPdf(true);
    try {
      await downloadPdf(selectedType, contractData);
      showNotification('Векторный PDF документ сформирован!');
    } catch (err) {
      alert(`Ошибка: ${err.message}`);
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  const handleSaveDraft = async () => {
    if (!contractData) return;
    setIsSavingDraft(true);
    try {
      const title = `Договор ${selectedType.toUpperCase()} № ${contractData?.metadata?.contract_number || 'б/н'}`;
      await saveDraft(selectedType, contractData, title);
      showNotification('Черновик успешно сохранен в хранилище!');
      updateDraftsCount();
    } catch (err) {
      alert(`Ошибка: ${err.message}`);
    } finally {
      setIsSavingDraft(false);
    }
  };

  const handleSelectDraft = async (draftId) => {
    try {
      const full = await getDraft(draftId);
      if (full?.data) {
        setSelectedType(full.contract_type || 'supply');
        setContractData(full.data);
        setIsDraftsModalOpen(false);
        showNotification(`Черновик «${full.title}» загружен`);
      }
    } catch (err) {
      alert('Не удалось загрузить черновик');
    }
  };

  const getTypeIcon = (key) => {
    switch (key) {
      case 'supply':
        return <Truck size={18} />;
      case 'services':
        return <Briefcase size={18} />;
      case 'work':
        return <Hammer size={18} />;
      case 'nda':
        return <ShieldCheck size={18} />;
      default:
        return <FileText size={18} />;
    }
  };

  if (!contractData) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: 'var(--text-muted)' }}>Инициализация платформы DocGen...</p>
      </div>
    );
  }

  const meta = contractData.metadata || {};
  const payment = contractData.payment_terms || {};

  return (
    <div style={{ minHeight: '100vh', padding: '24px', maxWidth: '1440px', margin: '0 auto' }}>
      {/* Header */}
      <Header
        onResetSample={() => loadSample(selectedType)}
        onOpenDrafts={() => setIsDraftsModalOpen(true)}
        draftsCount={draftsCount}
      />

      {/* Notification Toast */}
      {notification && (
        <div
          style={{
            position: 'fixed',
            top: '24px',
            right: '24px',
            background: notification.type === 'success' ? '#065f46' : '#991b1b',
            color: '#ffffff',
            padding: '12px 20px',
            borderRadius: 'var(--radius-md)',
            boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
            zIndex: 2000,
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            fontWeight: 600,
            fontSize: '14px',
          }}
        >
          <CheckCircle2 size={18} />
          <span>{notification.msg}</span>
        </div>
      )}

      {/* Contract Type Selection Bar */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '12px', marginBottom: '20px' }}>
        {contractTypes.map((t) => {
          const isSelected = t.key === selectedType;
          return (
            <button
              key={t.key}
              type="button"
              className="glass-card"
              onClick={() => handleTypeChange(t.key)}
              style={{
                padding: '14px 18px',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                textAlign: 'left',
                cursor: 'pointer',
                borderColor: isSelected ? 'var(--primary)' : 'var(--border-glass)',
                background: isSelected ? 'rgba(99, 102, 241, 0.15)' : 'var(--bg-card)',
                boxShadow: isSelected ? '0 0 15px rgba(99, 102, 241, 0.3)' : 'none',
              }}
            >
              <div
                style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: '10px',
                  background: isSelected ? 'var(--primary)' : 'rgba(255, 255, 255, 0.05)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: isSelected ? '#fff' : 'var(--text-muted)',
                }}
              >
                {getTypeIcon(t.key)}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '13.5px', fontWeight: 700, color: isSelected ? '#ffffff' : 'var(--text-main)' }}>
                  {t.title}
                </div>
                <div style={{ fontSize: '11.5px', color: isSelected ? '#a5b4fc' : 'var(--text-dim)', marginTop: '2px' }}>
                  {t.law_reference}
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Contract Header Metadata Card */}
      <div className="glass-panel" style={{ padding: '16px 20px', marginBottom: '20px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label">Номер договора</label>
            <input
              type="text"
              className="form-input"
              value={meta.contract_number || ''}
              onChange={(e) => handleMetadataChange('contract_number', e.target.value)}
              placeholder="2025/П-01"
            />
          </div>

          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label">Дата заключения</label>
            <input
              type="text"
              className="form-input"
              value={meta.contract_date || ''}
              onChange={(e) => handleMetadataChange('contract_date', e.target.value)}
              placeholder="15.02.2025"
            />
          </div>

          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label">Место заключения (город)</label>
            <input
              type="text"
              className="form-input"
              value={meta.city || ''}
              onChange={(e) => handleMetadataChange('city', e.target.value)}
              placeholder="г. Москва"
            />
          </div>

          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label">Срок действия договора</label>
            <input
              type="text"
              className="form-input"
              value={meta.valid_until || ''}
              onChange={(e) => handleMetadataChange('valid_until', e.target.value)}
              placeholder="до 31 декабря 2025 года"
            />
          </div>
        </div>
      </div>

      {/* Main Split Layout: Editor Tabs (Left) vs Calculations & Actions (Right) */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: '24px', alignItems: 'start' }}>
        {/* Left Column: Tabbed Form */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Tabs Nav */}
          <div className="glass-panel" style={{ padding: '6px', display: 'flex', gap: '8px' }}>
            <button
              type="button"
              className={`btn ${activeTab === 'parties' ? 'btn-primary' : 'btn-outline'}`}
              onClick={() => setActiveTab('parties')}
              style={{ flex: 1 }}
            >
              <Building size={16} />
              <span>1. Стороны и Реквизиты</span>
            </button>

            <button
              type="button"
              className={`btn ${activeTab === 'spec' ? 'btn-primary' : 'btn-outline'}`}
              onClick={() => setActiveTab('spec')}
              style={{ flex: 1 }}
            >
              <Layers size={16} />
              <span>2. Спецификация и Этапы</span>
            </button>

            <button
              type="button"
              className={`btn ${activeTab === 'terms' ? 'btn-primary' : 'btn-outline'}`}
              onClick={() => setActiveTab('terms')}
              style={{ flex: 1 }}
            >
              <CreditCard size={16} />
              <span>3. Оплата и НДС</span>
            </button>
          </div>

          {/* Tab 1: Parties */}
          {activeTab === 'parties' && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <PartyCard
                title="Сторона 1: Заказчик / Покупатель"
                roleBadge="Заказчик"
                party={contractData.client || {}}
                onChange={(p) => handlePartyChange('client', p)}
              />
              <PartyCard
                title="Сторона 2: Исполнитель / Поставщик"
                roleBadge="Исполнитель"
                party={contractData.vendor || {}}
                onChange={(p) => handlePartyChange('vendor', p)}
              />
            </div>
          )}

          {/* Tab 2: Specification */}
          {activeTab === 'spec' && (
            <SpecificationEditor
              contractType={selectedType}
              data={contractData}
              onChange={(updated) => setContractData(updated)}
            />
          )}

          {/* Tab 3: Terms */}
          {activeTab === 'terms' && (
            <div className="glass-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', borderBottom: '1px solid var(--border-glass)', paddingBottom: '12px' }}>
                <CreditCard size={20} color="var(--primary)" />
                <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Условия оплаты и налоговый режим</h3>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                {/* Payment Schedule */}
                <div className="form-group">
                  <label className="form-label">График и порядок расчетов</label>
                  <select
                    className="form-select"
                    value={payment.type || '100_POSTPAYMENT'}
                    onChange={(e) => handlePaymentTermsChange('type', e.target.value)}
                  >
                    <option value="100_POSTPAYMENT">100% Постоплата (после приемки)</option>
                    <option value="50_50">50% Аванс / 50% Постоплата</option>
                    <option value="100_PREPAYMENT">100% Предварительная оплата</option>
                  </select>
                </div>

                {/* Days count */}
                <div className="form-group">
                  <label className="form-label">Срок оплаты (дней)</label>
                  <input
                    type="number"
                    className="form-input"
                    value={payment.postpayment_days || 5}
                    onChange={(e) => handlePaymentTermsChange('postpayment_days', parseInt(e.target.value, 10) || 1)}
                  />
                </div>

                {/* Days type */}
                <div className="form-group">
                  <label className="form-label">Тип дней</label>
                  <select
                    className="form-select"
                    value={payment.days_type || 'banking'}
                    onChange={(e) => handlePaymentTermsChange('days_type', e.target.value)}
                  >
                    <option value="banking">Банковские (рабочие) дни</option>
                    <option value="calendar">Календарные дни</option>
                  </select>
                </div>

                {/* VAT Mode */}
                <div className="form-group">
                  <label className="form-label">Ставка и режим НДС</label>
                  <select
                    className="form-select"
                    value={
                      contractData.is_exempt_vat
                        ? 'exempt'
                        : contractData.vat_rate === 10
                        ? '10'
                        : '20'
                    }
                    onChange={(e) => {
                      if (e.target.value === 'exempt') {
                        setContractData((prev) => ({ ...prev, is_exempt_vat: true, vat_rate: 0 }));
                      } else {
                        setContractData((prev) => ({
                          ...prev,
                          is_exempt_vat: false,
                          vat_rate: parseInt(e.target.value, 10),
                          vat_included: true,
                        }));
                      }
                    }}
                  >
                    <option value="20">20% (НДС включен в цену)</option>
                    <option value="10">10% (НДС включен в цену)</option>
                    <option value="exempt">Без НДС (УСН / ст. 346.11 НК РФ)</option>
                  </select>
                </div>
              </div>

              {/* Dispute & Penalties */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', borderBottom: '1px solid var(--border-glass)', paddingBottom: '12px', marginTop: '10px' }}>
                <Scale size={20} color="var(--accent-amber)" />
                <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Ответственность и порядок разрешения споров</h3>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div className="form-group">
                  <label className="form-label">Срок ответа на претензию (дней)</label>
                  <input
                    type="number"
                    className="form-input"
                    value={contractData.dispute_resolution?.pre_trial_claim_days || 30}
                    onChange={(e) =>
                      setContractData((prev) => ({
                        ...prev,
                        dispute_resolution: {
                          ...(prev.dispute_resolution || {}),
                          pre_trial_claim_days: parseInt(e.target.value, 10) || 0,
                        },
                      }))
                    }
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Подсудность споров</label>
                  <select
                    className="form-select"
                    value={contractData.dispute_resolution?.court_jurisdiction || 'arbitration_plaintiff'}
                    onChange={(e) =>
                      setContractData((prev) => ({
                        ...prev,
                        dispute_resolution: {
                          ...(prev.dispute_resolution || {}),
                          court_jurisdiction: e.target.value,
                        },
                      }))
                    }
                  >
                    <option value="arbitration_plaintiff">Арбитражный суд по месту нахождения Истца</option>
                    <option value="arbitration_defendant">Арбитражный суд по месту нахождения Ответчика</option>
                    <option value="moscow">Арбитражный суд города Москвы</option>
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Calculations & Actions (Sticky) */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', position: 'sticky', top: '24px' }}>
          {/* Summary Card */}
          <div className="glass-panel" style={{ padding: '24px' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={18} color="var(--primary)" />
              <span>Расчет цены и НДС</span>
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Сумма договора:</span>
                <strong style={{ fontSize: '20px', color: '#ffffff', fontFamily: 'var(--font-mono)' }}>
                  {calcResult?.total_formatted || '0,00'} ₽
                </strong>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', fontSize: '13px' }}>
                <span style={{ color: 'var(--text-muted)' }}>
                  {contractData.is_exempt_vat ? 'НДС:' : `В т.ч. НДС ${contractData.vat_rate}%:`}
                </span>
                <span style={{ color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>
                  {contractData.is_exempt_vat ? 'Не облагается (УСН)' : `${calcResult?.vat_formatted || '0,00'} ₽`}
                </span>
              </div>

              {calcResult?.advance_amount > 0 && (
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', fontSize: '13px', borderTop: '1px dashed var(--border-glass)', paddingTop: '8px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Авансовый платеж (50%):</span>
                  <span style={{ color: 'var(--accent-emerald)', fontFamily: 'var(--font-mono)' }}>
                    {calcResult?.advance_amount?.toLocaleString('ru-RU', { minimumFractionDigits: 2 })} ₽
                  </span>
                </div>
              )}
            </div>

            {/* Legal Wording Box */}
            {calcResult?.legal_wording && (
              <div style={{ background: 'rgba(0,0,0,0.3)', padding: '12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-glass)', marginTop: '14px', fontSize: '12px', color: 'var(--text-muted)', lineHeight: '1.45' }}>
                <strong style={{ color: 'var(--accent-amber)', display: 'block', marginBottom: '4px' }}>Сумма прописью (ГК РФ):</strong>
                {calcResult.legal_wording}
              </div>
            )}

            {/* Action Buttons */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '20px' }}>
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleDownloadDocx}
                disabled={isDownloadingDocx}
                style={{ width: '100%', padding: '12px' }}
              >
                <Download size={16} />
                <span>{isDownloadingDocx ? 'Генерация DOCX...' : 'Скачать DOCX (ГОСТ)'}</span>
              </button>

              <button
                type="button"
                className="btn btn-success"
                onClick={handleDownloadPdf}
                disabled={isDownloadingPdf}
                style={{ width: '100%', padding: '12px' }}
              >
                <FileCode size={16} />
                <span>{isDownloadingPdf ? 'Компиляция PDF...' : 'Скачать PDF (Typst)'}</span>
              </button>

              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleSaveDraft}
                disabled={isSavingDraft}
                style={{ width: '100%', padding: '10px' }}
              >
                <Save size={16} />
                <span>{isSavingDraft ? 'Сохранение...' : 'Сохранить черновик'}</span>
              </button>
            </div>
          </div>

          {/* Compliance Card */}
          <div className="glass-card" style={{ padding: '16px', fontSize: '12px' }}>
            <h4 style={{ fontWeight: 600, color: '#fff', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <CheckCircle2 size={15} color="var(--accent-emerald)" />
              <span>Стандарты сборки документа</span>
            </h4>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '6px', color: 'var(--text-muted)' }}>
              <li>✓ ГОСТ Р 7.0.97-2016 (поля 25/15/20/20)</li>
              <li>✓ Защита от разрывов строк таблиц (`cantSplit`)</li>
              <li>✓ Алгоритмы контрольных сумм ФНС/ЦБ РФ</li>
              <li>✓ Детерминированная сборка без LLM</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Drafts Modal */}
      <DraftsModal
        isOpen={isDraftsModalOpen}
        onClose={() => setIsDraftsModalOpen(false)}
        onSelectDraft={handleSelectDraft}
      />
    </div>
  );
}
