import React, { useState, useEffect } from 'react';
import { Building2, UserCheck, Search, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';
import { suggestPartyByInn, validatePartyRequisites } from '../api/client';

export default function PartyCard({
  title,
  roleBadge,
  party,
  onChange,
}) {
  const [loadingSuggest, setLoadingSuggest] = useState(false);
  const [validationReport, setValidationReport] = useState(null);

  useEffect(() => {
    let active = true;
    const timer = setTimeout(async () => {
      try {
        const report = await validatePartyRequisites(party);
        if (active) setValidationReport(report);
      } catch (err) {
        // local fallback
      }
    }, 400);

    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [party]);

  const handleFieldChange = (field, value) => {
    onChange({
      ...party,
      [field]: value,
    });
  };

  const handleBankChange = (field, value) => {
    onChange({
      ...party,
      bank_requisites: {
        ...(party.bank_requisites || {}),
        [field]: value,
      },
    });
  };

  const handleSuggest = async () => {
    if (!party.inn || party.inn.length < 10) return;
    setLoadingSuggest(true);
    try {
      const result = await suggestPartyByInn(party.inn);
      if (result.found) {
        onChange({
          ...party,
          full_name: result.full_name || party.full_name,
          short_name: result.short_name || party.short_name,
          kpp: result.kpp || party.kpp,
          ogrn: result.ogrn || party.ogrn,
          legal_address: result.legal_address || party.legal_address,
          signatory_position: result.signatory_position || party.signatory_position,
          signatory_name: result.signatory_name || party.signatory_name,
        });
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingSuggest(false);
    }
  };

  const bank = party.bank_requisites || {};
  const isAllValid = validationReport?.valid;

  return (
    <div className="glass-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Card Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-glass)', paddingBottom: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: 'rgba(99, 102, 241, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary)' }}>
            <Building2 size={18} />
          </div>
          <div>
            <h3 style={{ fontSize: '15px', fontWeight: 700 }}>{title}</h3>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{roleBadge}</span>
          </div>
        </div>

        <div>
          {isAllValid ? (
            <span className="badge badge-valid">
              <CheckCircle2 size={12} /> Реквизиты проверены
            </span>
          ) : (
            <span className="badge badge-invalid">
              <AlertCircle size={12} /> Требуется проверка
            </span>
          )}
        </div>
      </div>

      {/* Form Fields */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
        {/* Party Type */}
        <div className="form-group" style={{ gridColumn: 'span 2' }}>
          <label className="form-label">Организационно-правовая форма</label>
          <select
            className="form-select"
            value={party.party_type || 'OOO'}
            onChange={(e) => handleFieldChange('party_type', e.target.value)}
          >
            <option value="OOO">ООО (Общество с ограниченной ответственностью)</option>
            <option value="AO">АО / ПАО (Акционерное общество)</option>
            <option value="IP">ИП (Индивидуальный предприниматель)</option>
            <option value="SELF_EMPLOYED">Самозанятый (Плательщик НПД)</option>
            <option value="INDIVIDUAL">Физическое лицо</option>
          </select>
        </div>

        {/* Full Name */}
        <div className="form-group" style={{ gridColumn: 'span 2' }}>
          <label className="form-label">Полное наименование организации или ФИО</label>
          <input
            type="text"
            className="form-input"
            value={party.full_name || ''}
            onChange={(e) => handleFieldChange('full_name', e.target.value)}
            placeholder="ООО «Пример» или ИП Иванов И.И."
          />
        </div>

        {/* INN with Lookup */}
        <div className="form-group">
          <label className="form-label">
            <span>ИНН (10 или 12 цифр)</span>
            {validationReport?.details?.inn?.valid && (
              <span style={{ color: 'var(--accent-emerald)', fontSize: '11px' }}>✓ Корректен</span>
            )}
          </label>
          <div style={{ display: 'flex', gap: '6px' }}>
            <input
              type="text"
              className={`form-input ${validationReport && !validationReport?.details?.inn?.valid ? 'is-invalid' : ''}`}
              value={party.inn || ''}
              onChange={(e) => handleFieldChange('inn', e.target.value)}
              placeholder="7707083893"
            />
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleSuggest}
              disabled={loadingSuggest || !party.inn}
              title="Заполнить по ИНН через DaData"
              style={{ padding: '8px 12px' }}
            >
              {loadingSuggest ? <RefreshCw size={14} className="spin" /> : <Search size={14} />}
            </button>
          </div>
          {validationReport?.errors?.inn && (
            <span style={{ color: 'var(--accent-rose)', fontSize: '11px' }}>{validationReport.errors.inn}</span>
          )}
        </div>

        {/* KPP */}
        <div className="form-group">
          <label className="form-label">КПП (для ЮЛ)</label>
          <input
            type="text"
            className="form-input"
            value={party.kpp || ''}
            onChange={(e) => handleFieldChange('kpp', e.target.value)}
            placeholder="770701001"
          />
        </div>

        {/* OGRN */}
        <div className="form-group">
          <label className="form-label">ОГРН / ОГРНИП</label>
          <input
            type="text"
            className="form-input"
            value={party.ogrn || ''}
            onChange={(e) => handleFieldChange('ogrn', e.target.value)}
            placeholder="1027700132195"
          />
        </div>

        {/* Phone */}
        <div className="form-group">
          <label className="form-label">Телефон</label>
          <input
            type="text"
            className="form-input"
            value={party.phone || ''}
            onChange={(e) => handleFieldChange('phone', e.target.value)}
            placeholder="+7 (495) 000-00-00"
          />
        </div>

        {/* Legal Address */}
        <div className="form-group" style={{ gridColumn: 'span 2' }}>
          <label className="form-label">Юридический адрес</label>
          <input
            type="text"
            className="form-input"
            value={party.legal_address || ''}
            onChange={(e) => handleFieldChange('legal_address', e.target.value)}
            placeholder="Индекс, город, улица, дом, офис"
          />
        </div>

        {/* Signatory Position */}
        <div className="form-group">
          <label className="form-label">Должность подписанта</label>
          <input
            type="text"
            className="form-input"
            value={party.signatory_position || ''}
            onChange={(e) => handleFieldChange('signatory_position', e.target.value)}
            placeholder="Генеральный директор"
          />
        </div>

        {/* Signatory Name */}
        <div className="form-group">
          <label className="form-label">ФИО подписанта</label>
          <input
            type="text"
            className="form-input"
            value={party.signatory_name || ''}
            onChange={(e) => handleFieldChange('signatory_name', e.target.value)}
            placeholder="Иванов Иван Иванович"
          />
        </div>

        {/* Signatory Basis */}
        <div className="form-group" style={{ gridColumn: 'span 2' }}>
          <label className="form-label">Основание полномочий</label>
          <input
            type="text"
            className="form-input"
            value={party.signatory_basis || ''}
            onChange={(e) => handleFieldChange('signatory_basis', e.target.value)}
            placeholder="Устава / Доверенности № 12 от 10.01.2025"
          />
        </div>
      </div>

      {/* Bank Requisites Block */}
      <div style={{ background: 'rgba(0, 0, 0, 0.2)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-glass)', marginTop: '4px' }}>
        <h4 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--accent-cyan)', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
          🏦 Банковские реквизиты
        </h4>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <div className="form-group" style={{ gridColumn: 'span 2' }}>
            <label className="form-label">Наименование банка</label>
            <input
              type="text"
              className="form-input"
              value={bank.bank_name || ''}
              onChange={(e) => handleBankChange('bank_name', e.target.value)}
              placeholder="ПАО СБЕРБАНК г. Москва"
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              <span>БИК (9 цифр)</span>
              {validationReport?.details?.bik?.valid && (
                <span style={{ color: 'var(--accent-emerald)', fontSize: '11px' }}>✓</span>
              )}
            </label>
            <input
              type="text"
              className={`form-input ${validationReport && !validationReport?.details?.bik?.valid ? 'is-invalid' : ''}`}
              value={bank.bik || ''}
              onChange={(e) => handleBankChange('bik', e.target.value)}
              placeholder="044525225"
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              <span>Расчетный счет (20 цифр)</span>
              {validationReport?.details?.account?.valid && (
                <span style={{ color: 'var(--accent-emerald)', fontSize: '11px' }}>✓ Привязан к БИК</span>
              )}
            </label>
            <input
              type="text"
              className={`form-input ${validationReport && !validationReport?.details?.account?.valid ? 'is-invalid' : ''}`}
              value={bank.account || ''}
              onChange={(e) => handleBankChange('account', e.target.value)}
              placeholder="40702810438000012345"
            />
            {validationReport?.errors?.account && (
              <span style={{ color: 'var(--accent-rose)', fontSize: '11px' }}>{validationReport.errors.account}</span>
            )}
          </div>

          <div className="form-group" style={{ gridColumn: 'span 2' }}>
            <label className="form-label">Корреспондентский счет (20 цифр)</label>
            <input
              type="text"
              className="form-input"
              value={bank.corr_account || ''}
              onChange={(e) => handleBankChange('corr_account', e.target.value)}
              placeholder="30101810400000000225"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
