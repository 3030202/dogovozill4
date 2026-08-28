import React from 'react';
import { Plus, Trash2, Package, Truck, Wrench, Shield, Calendar, MapPin, DollarSign } from 'lucide-react';

export default function SpecificationEditor({ contractType, data, onChange }) {
  // 1. SUPPLY CONTRACT
  if (contractType === 'supply') {
    const items = data.items || [];
    const delivery = data.delivery_terms || {};

    const handleItemChange = (index, field, value) => {
      const updated = [...items];
      updated[index] = { ...updated[index], [field]: value };
      onChange({ ...data, items: updated });
    };

    const handleAddItem = () => {
      const newItem = {
        name: 'Новый товар / оборудование',
        unit: 'шт.',
        quantity: 1,
        price_per_unit: 10000,
      };
      onChange({ ...data, items: [...items, newItem] });
    };

    const handleRemoveItem = (index) => {
      onChange({ ...data, items: items.filter((_, i) => i !== index) });
    };

    const handleDeliveryChange = (field, value) => {
      onChange({
        ...data,
        delivery_terms: { ...delivery, [field]: value },
      });
    };

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Package size={20} color="var(--primary)" />
              <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Спецификация поставляемых товаров</h3>
            </div>
            <button type="button" className="btn btn-primary" onClick={handleAddItem} style={{ padding: '6px 12px', fontSize: '13px' }}>
              <Plus size={14} /> Добавить позицию
            </button>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-glass)', textAlign: 'left', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '8px 6px', width: '36px' }}>№</th>
                  <th style={{ padding: '8px' }}>Наименование товара / артикул</th>
                  <th style={{ padding: '8px', width: '80px' }}>Ед. изм.</th>
                  <th style={{ padding: '8px', width: '90px' }}>Кол-во</th>
                  <th style={{ padding: '8px', width: '130px' }}>Цена за ед. (руб.)</th>
                  <th style={{ padding: '8px', width: '120px' }}>Сумма (руб.)</th>
                  <th style={{ padding: '8px', width: '40px' }}></th>
                </tr>
              </thead>
              <tbody>
                {items.map((item, idx) => {
                  const lineTotal = (parseFloat(item.quantity) || 0) * (parseFloat(item.price_per_unit) || 0);
                  return (
                    <tr key={idx} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                      <td style={{ padding: '8px 6px', textAlign: 'center', color: 'var(--text-dim)' }}>{idx + 1}</td>
                      <td style={{ padding: '8px' }}>
                        <input
                          type="text"
                          className="form-input"
                          value={item.name || ''}
                          onChange={(e) => handleItemChange(idx, 'name', e.target.value)}
                        />
                      </td>
                      <td style={{ padding: '8px' }}>
                        <input
                          type="text"
                          className="form-input"
                          value={item.unit || 'шт.'}
                          onChange={(e) => handleItemChange(idx, 'unit', e.target.value)}
                        />
                      </td>
                      <td style={{ padding: '8px' }}>
                        <input
                          type="number"
                          step="any"
                          className="form-input"
                          value={item.quantity || 1}
                          onChange={(e) => handleItemChange(idx, 'quantity', parseFloat(e.target.value) || 0)}
                        />
                      </td>
                      <td style={{ padding: '8px' }}>
                        <input
                          type="number"
                          step="any"
                          className="form-input"
                          value={item.price_per_unit || 0}
                          onChange={(e) => handleItemChange(idx, 'price_per_unit', parseFloat(e.target.value) || 0)}
                        />
                      </td>
                      <td style={{ padding: '8px', fontWeight: 600, color: '#fff' }}>
                        {lineTotal.toLocaleString('ru-RU', { minimumFractionDigits: 2 })}
                      </td>
                      <td style={{ padding: '8px' }}>
                        {items.length > 1 && (
                          <button
                            type="button"
                            className="btn btn-outline"
                            onClick={() => handleRemoveItem(idx)}
                            style={{ padding: '6px 8px', color: 'var(--accent-rose)' }}
                            title="Удалить позицию"
                          >
                            <Trash2 size={14} />
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Delivery Terms */}
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <Truck size={20} color="var(--accent-cyan)" />
            <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Условия доставки и приемки</h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
            <div className="form-group" style={{ gridColumn: 'span 2' }}>
              <label className="form-label">Адрес доставки / склад грузополучателя</label>
              <input
                type="text"
                className="form-input"
                value={delivery.destination_address || ''}
                onChange={(e) => handleDeliveryChange('destination_address', e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Срок поставки (рабочих дней)</label>
              <input
                type="number"
                className="form-input"
                value={delivery.delivery_timeframe_days || 10}
                onChange={(e) => handleDeliveryChange('delivery_timeframe_days', parseInt(e.target.value, 10) || 1)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Срок приемки товара (дней)</label>
              <input
                type="number"
                className="form-input"
                value={delivery.acceptance_days || 3}
                onChange={(e) => handleDeliveryChange('acceptance_days', parseInt(e.target.value, 10) || 1)}
              />
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 2. SERVICES CONTRACT
  if (contractType === 'services') {
    const services = data.services || [];
    const terms = data.service_terms || {};

    const handleServiceChange = (index, field, value) => {
      const updated = [...services];
      updated[index] = { ...updated[index], [field]: value };
      onChange({ ...data, services: updated });
    };

    const handleAddService = () => {
      const newService = {
        name: 'Оказание консультационных / IT услуг',
        description: 'Комплексный анализ и предоставление отчета',
        price: 50000,
      };
      onChange({ ...data, services: [...services, newService] });
    };

    const handleRemoveService = (index) => {
      onChange({ ...data, services: services.filter((_, i) => i !== index) });
    };

    const handleTermsChange = (field, value) => {
      onChange({
        ...data,
        service_terms: { ...terms, [field]: value },
      });
    };

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Package size={20} color="var(--primary)" />
              <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Перечень оказываемых услуг</h3>
            </div>
            <button type="button" className="btn btn-primary" onClick={handleAddService} style={{ padding: '6px 12px', fontSize: '13px' }}>
              <Plus size={14} /> Добавить услугу
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {services.map((srv, idx) => (
              <div key={idx} style={{ background: 'rgba(0, 0, 0, 0.25)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-glass)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <span style={{ fontWeight: 600, fontSize: '14px' }}>Услуга № {idx + 1}</span>
                  {services.length > 1 && (
                    <button
                      type="button"
                      className="btn btn-outline"
                      onClick={() => handleRemoveService(idx)}
                      style={{ padding: '4px 8px', color: 'var(--accent-rose)' }}
                    >
                      <Trash2 size={14} />
                    </button>
                  )}
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 180px', gap: '12px' }}>
                  <div className="form-group">
                    <label className="form-label">Наименование услуги</label>
                    <input
                      type="text"
                      className="form-input"
                      value={srv.name || ''}
                      onChange={(e) => handleServiceChange(idx, 'name', e.target.value)}
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Стоимость (руб.)</label>
                    <input
                      type="number"
                      className="form-input"
                      value={srv.price || 0}
                      onChange={(e) => handleServiceChange(idx, 'price', parseFloat(e.target.value) || 0)}
                    />
                  </div>

                  <div className="form-group" style={{ gridColumn: 'span 2' }}>
                    <label className="form-label">Описание состава услуг и ожидаемого результата</label>
                    <textarea
                      rows={2}
                      className="form-textarea"
                      value={srv.description || ''}
                      onChange={(e) => handleServiceChange(idx, 'description', e.target.value)}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Service Terms */}
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <Calendar size={20} color="var(--accent-cyan)" />
            <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Сроки оказания и приемка</h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
            <div className="form-group">
              <label className="form-label">Дата начала оказания услуг</label>
              <input
                type="date"
                className="form-input"
                value={terms.service_start_date || ''}
                onChange={(e) => handleTermsChange('service_start_date', e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Дата окончания оказания услуг</label>
              <input
                type="date"
                className="form-input"
                value={terms.service_end_date || ''}
                onChange={(e) => handleTermsChange('service_end_date', e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Срок рассмотрения Акта (дней)</label>
              <input
                type="number"
                className="form-input"
                value={terms.act_review_days || 5}
                onChange={(e) => handleTermsChange('act_review_days', parseInt(e.target.value, 10) || 1)}
              />
            </div>

            <div className="form-group" style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', gap: '10px', marginTop: '28px' }}>
              <input
                type="checkbox"
                id="ip_rights"
                checked={terms.ip_rights_transfer ?? true}
                onChange={(e) => handleTermsChange('ip_rights_transfer', e.target.checked)}
                style={{ width: '18px', height: '18px' }}
              />
              <label htmlFor="ip_rights" style={{ fontSize: '13px', cursor: 'pointer' }}>
                Передача исключительных прав на результаты (РИД) Заказчику
              </label>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 3. WORK CONTRACT
  if (contractType === 'work') {
    const stages = data.stages || [];
    const terms = data.work_terms || {};

    const handleStageChange = (index, field, value) => {
      const updated = [...stages];
      updated[index] = { ...updated[index], [field]: value };
      onChange({ ...data, stages: updated });
    };

    const handleAddStage = () => {
      const nextNum = stages.length + 1;
      const newStage = {
        stage_number: nextNum,
        title: `Этап ${nextNum}: Выполнение монтажных/строительных работ`,
        start_date: '2025-03-01',
        end_date: '2025-03-31',
        cost: 100000,
        deliverable_result: 'Смонтированное оборудование и протокол испытаний',
      };
      onChange({ ...data, stages: [...stages, newStage] });
    };

    const handleRemoveStage = (index) => {
      onChange({ ...data, stages: stages.filter((_, i) => i !== index) });
    };

    const handleWorkTermsChange = (field, value) => {
      onChange({
        ...data,
        work_terms: { ...terms, [field]: value },
      });
    };

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <MapPin size={20} color="var(--primary)" />
            <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Объект и место проведения работ</h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
            <div className="form-group" style={{ gridColumn: 'span 2' }}>
              <label className="form-label">Наименование объекта работ</label>
              <input
                type="text"
                className="form-input"
                value={data.work_object_name || ''}
                onChange={(e) => onChange({ ...data, work_object_name: e.target.value })}
                placeholder="Серверное помещение / Офис этаж 4"
              />
            </div>

            <div className="form-group" style={{ gridColumn: 'span 2' }}>
              <label className="form-label">Место выполнения работ (адрес)</label>
              <input
                type="text"
                className="form-input"
                value={data.work_location || ''}
                onChange={(e) => onChange({ ...data, work_location: e.target.value })}
                placeholder="г. Москва, ул. Примерная, д. 10"
              />
            </div>
          </div>
        </div>

        {/* Stages */}
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Wrench size={20} color="var(--accent-amber)" />
              <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Календарный план и этапы работ</h3>
            </div>
            <button type="button" className="btn btn-primary" onClick={handleAddStage} style={{ padding: '6px 12px', fontSize: '13px' }}>
              <Plus size={14} /> Добавить этап
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {stages.map((stage, idx) => (
              <div key={idx} style={{ background: 'rgba(0, 0, 0, 0.25)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-glass)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <span style={{ fontWeight: 600, fontSize: '14px' }}>Этап № {stage.stage_number || idx + 1}</span>
                  {stages.length > 1 && (
                    <button
                      type="button"
                      className="btn btn-outline"
                      onClick={() => handleRemoveStage(idx)}
                      style={{ padding: '4px 8px', color: 'var(--accent-rose)' }}
                    >
                      <Trash2 size={14} />
                    </button>
                  )}
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr 1fr', gap: '10px' }}>
                  <div className="form-group" style={{ gridColumn: 'span 2' }}>
                    <label className="form-label">Наименование работ</label>
                    <input
                      type="text"
                      className="form-input"
                      value={stage.title || ''}
                      onChange={(e) => handleStageChange(idx, 'title', e.target.value)}
                    />
                  </div>

                  <div className="form-group" style={{ gridColumn: 'span 2' }}>
                    <label className="form-label">Овеществленный результат</label>
                    <input
                      type="text"
                      className="form-input"
                      value={stage.deliverable_result || ''}
                      onChange={(e) => handleStageChange(idx, 'deliverable_result', e.target.value)}
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Дата начала</label>
                    <input
                      type="date"
                      className="form-input"
                      value={stage.start_date || ''}
                      onChange={(e) => handleStageChange(idx, 'start_date', e.target.value)}
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Дата завершения</label>
                    <input
                      type="date"
                      className="form-input"
                      value={stage.end_date || ''}
                      onChange={(e) => handleStageChange(idx, 'end_date', e.target.value)}
                    />
                  </div>

                  <div className="form-group" style={{ gridColumn: 'span 2' }}>
                    <label className="form-label">Стоимость этапа (руб.)</label>
                    <input
                      type="number"
                      className="form-input"
                      value={stage.cost || 0}
                      onChange={(e) => handleStageChange(idx, 'cost', parseFloat(e.target.value) || 0)}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Work Terms */}
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <Shield size={20} color="var(--accent-emerald)" />
            <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Гарантии и условия подряда</h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
            <div className="form-group">
              <label className="form-label">Гарантийный срок (месяцев)</label>
              <input
                type="number"
                className="form-input"
                value={terms.warranty_months || 12}
                onChange={(e) => handleWorkTermsChange('warranty_months', parseInt(e.target.value, 10) || 0)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Срок приемки по КС-2 (дней)</label>
              <input
                type="number"
                className="form-input"
                value={terms.acceptance_days || 5}
                onChange={(e) => handleWorkTermsChange('acceptance_days', parseInt(e.target.value, 10) || 1)}
              />
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 4. NDA CONTRACT
  if (contractType === 'nda') {
    const scope = data.scope || {};
    const ndaTerms = data.nda_terms || {};

    const handleScopeChange = (field, value) => {
      onChange({
        ...data,
        scope: { ...scope, [field]: value },
      });
    };

    const handleNdaTermsChange = (field, value) => {
      onChange({
        ...data,
        nda_terms: { ...ndaTerms, [field]: value },
      });
    };

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <Shield size={20} color="var(--accent-rose)" />
            <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Предмет конфиденциальности (ФЗ № 98-ФЗ)</h3>
          </div>

          <div className="form-group">
            <label className="form-label">Цель раскрытия информации</label>
            <textarea
              rows={3}
              className="form-textarea"
              value={scope.purpose || ''}
              onChange={(e) => handleScopeChange('purpose', e.target.value)}
            />
          </div>
        </div>

        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <DollarSign size={20} color="var(--accent-amber)" />
            <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Сроки охраны и ответственность</h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
            <div className="form-group">
              <label className="form-label">Срок охраны тайны (лет)</label>
              <input
                type="number"
                className="form-input"
                value={ndaTerms.confidentiality_years || 3}
                onChange={(e) => handleNdaTermsChange('confidentiality_years', parseInt(e.target.value, 10) || 1)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Штраф за разглашение (руб.)</label>
              <input
                type="number"
                className="form-input"
                value={ndaTerms.disclosure_penalty_rubles || 500000}
                onChange={(e) => handleNdaTermsChange('disclosure_penalty_rubles', parseFloat(e.target.value) || 0)}
              />
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 5. LEASE CONTRACT
  if (contractType === 'lease') {
    const leaseObj = data.lease_object || {};
    const leaseTerms = data.lease_terms || {};

    const handleObjChange = (field, value) => {
      onChange({ ...data, lease_object: { ...leaseObj, [field]: value } });
    };
    const handleLTermsChange = (field, value) => {
      onChange({ ...data, lease_terms: { ...leaseTerms, [field]: value } });
    };

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <Package size={20} color="var(--accent-amber)" />
            <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Объект аренды (ГК РФ гл. 34)</h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label className="form-label">Наименование имущества / оборудования</label>
              <input type="text" className="form-input" value={leaseObj.name || ''} onChange={(e) => handleObjChange('name', e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Инвентарный / серийный номер</label>
              <input type="text" className="form-input" value={leaseObj.inventory_number || ''} onChange={(e) => handleObjChange('inventory_number', e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Рыночная стоимость (руб.)</label>
              <input type="number" className="form-input" value={leaseObj.market_value_rubles || 0} onChange={(e) => handleObjChange('market_value_rubles', parseFloat(e.target.value) || 0)} />
            </div>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label className="form-label">Местонахождение объекта</label>
              <input type="text" className="form-input" value={leaseObj.location || ''} onChange={(e) => handleObjChange('location', e.target.value)} />
            </div>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label className="form-label">Техническое состояние</label>
              <textarea rows={2} className="form-textarea" value={leaseObj.condition || ''} onChange={(e) => handleObjChange('condition', e.target.value)} />
            </div>
          </div>
        </div>

        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <Calendar size={20} color="var(--primary)" />
            <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Условия аренды</h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
            <div className="form-group">
              <label className="form-label">Срок аренды (месяцев)</label>
              <input type="number" className="form-input" value={leaseTerms.rent_period_months || 12} onChange={(e) => handleLTermsChange('rent_period_months', parseInt(e.target.value, 10) || 1)} />
            </div>
            <div className="form-group">
              <label className="form-label">Ежемесячная арендная плата (руб.)</label>
              <input type="number" className="form-input" value={leaseTerms.monthly_rent_rubles || 0} onChange={(e) => handleLTermsChange('monthly_rent_rubles', parseFloat(e.target.value) || 0)} />
            </div>
            <div className="form-group">
              <label className="form-label">Обеспечительный платёж (× мес.)</label>
              <input type="number" step="0.5" className="form-input" value={leaseTerms.security_deposit_months || 0} onChange={(e) => handleLTermsChange('security_deposit_months', parseFloat(e.target.value) || 0)} />
            </div>
            <div className="form-group">
              <label className="form-label" style={{ visibility: 'hidden' }}>.</label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', cursor: 'pointer' }}>
                  <input type="checkbox" checked={leaseTerms.utilities_by_tenant ?? true} onChange={(e) => handleLTermsChange('utilities_by_tenant', e.target.checked)} />
                  Коммунальные расходы на арендаторе
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', cursor: 'pointer' }}>
                  <input type="checkbox" checked={leaseTerms.sublease_allowed ?? false} onChange={(e) => handleLTermsChange('sublease_allowed', e.target.checked)} />
                  Субаренда разрешена
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 6. LICENSE / SaaS CONTRACT
  if (contractType === 'license_sw') {
    const software = data.software || [];
    const terms = data.license_terms || {};

    const handleSWChange = (index, field, value) => {
      const updated = [...software];
      updated[index] = { ...updated[index], [field]: value };
      onChange({ ...data, software: updated });
    };

    const handleAddSW = () => {
      onChange({ ...data, software: [...software, { name: 'Новое ПО', version: '1.0', delivery_method: 'облачный доступ (SaaS)' }] });
    };

    const handleRemoveSW = (index) => {
      onChange({ ...data, software: software.filter((_, i) => i !== index) });
    };

    const handleLicTermsChange = (field, value) => {
      onChange({ ...data, license_terms: { ...terms, [field]: value } });
    };

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Package size={20} color="var(--accent-cyan)" />
              <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Программное обеспечение (ГК РФ ч. IV)</h3>
            </div>
            <button type="button" className="btn btn-primary" onClick={handleAddSW} style={{ padding: '6px 12px', fontSize: '13px' }}>
              <Plus size={14} /> Добавить ПО
            </button>
          </div>

          {software.map((sw, idx) => (
            <div key={idx} style={{ display: 'grid', gridTemplateColumns: '1fr 100px 200px 36px', gap: '8px', marginBottom: '10px', alignItems: 'end' }}>
              <div className="form-group" style={{ margin: 0 }}>
                <label className="form-label">Наименование ПО</label>
                <input type="text" className="form-input" value={sw.name || ''} onChange={(e) => handleSWChange(idx, 'name', e.target.value)} />
              </div>
              <div className="form-group" style={{ margin: 0 }}>
                <label className="form-label">Версия</label>
                <input type="text" className="form-input" value={sw.version || ''} onChange={(e) => handleSWChange(idx, 'version', e.target.value)} />
              </div>
              <div className="form-group" style={{ margin: 0 }}>
                <label className="form-label">Способ доставки</label>
                <select className="form-select" value={sw.delivery_method || ''} onChange={(e) => handleSWChange(idx, 'delivery_method', e.target.value)}>
                  <option value="облачный доступ (SaaS)">SaaS (облако)</option>
                  <option value="on-premise (установка на серверы Заказчика)">On-premise</option>
                  <option value="дистрибутив на физическом носителе">Носитель</option>
                </select>
              </div>
              <button type="button" className="btn btn-danger" onClick={() => handleRemoveSW(idx)} style={{ padding: '6px', height: '36px' }}>
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>

        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <DollarSign size={20} color="var(--accent-emerald)" />
            <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Условия лицензии</h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
            <div className="form-group">
              <label className="form-label">Тип лицензии</label>
              <select className="form-select" value={terms.license_type || 'simple'} onChange={(e) => handleLicTermsChange('license_type', e.target.value)}>
                <option value="simple">Простая (неисключительная)</option>
                <option value="exclusive">Исключительная</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Территория</label>
              <input type="text" className="form-input" value={terms.territory || 'Российская Федерация'} onChange={(e) => handleLicTermsChange('territory', e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Лицензионное вознаграждение (руб.)</label>
              <input type="number" className="form-input" value={data.license_fee || 0} onChange={(e) => onChange({ ...data, license_fee: parseFloat(e.target.value) || 0 })} />
            </div>
            <div className="form-group">
              <label className="form-label">Срок лицензии (мес.)</label>
              <input type="number" className="form-input" value={terms.period_months || 12} onChange={(e) => handleLicTermsChange('period_months', parseInt(e.target.value, 10) || 1)} />
            </div>
            <div className="form-group">
              <label className="form-label">Лимит пользователей</label>
              <input type="number" className="form-input" value={terms.allowed_users || 0} onChange={(e) => handleLicTermsChange('allowed_users', parseInt(e.target.value, 10) || 0)} />
            </div>
            <div className="form-group">
              <label className="form-label">SLA Uptime (%)</label>
              <input type="number" step="0.1" className="form-input" value={terms.sla_uptime_percent || 99.5} onChange={(e) => handleLicTermsChange('sla_uptime_percent', parseFloat(e.target.value) || 99)} />
            </div>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <div style={{ display: 'flex', gap: '20px' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', cursor: 'pointer' }}>
                  <input type="checkbox" checked={terms.support_included ?? true} onChange={(e) => handleLicTermsChange('support_included', e.target.checked)} />
                  Техподдержка включена
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', cursor: 'pointer' }}>
                  <input type="checkbox" checked={terms.source_code_included ?? false} onChange={(e) => handleLicTermsChange('source_code_included', e.target.checked)} />
                  Исходный код
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', cursor: 'pointer' }}>
                  <input type="checkbox" checked={terms.modification_allowed ?? false} onChange={(e) => handleLicTermsChange('modification_allowed', e.target.checked)} />
                  Модификация разрешена
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 7. FREELANCE / ГПХ CONTRACT
  if (contractType === 'freelance') {
    const tasks = data.tasks || [];
    const fTerms = data.freelance_terms || {};

    const handleTaskChange = (index, field, value) => {
      const updated = [...tasks];
      updated[index] = { ...updated[index], [field]: value };
      onChange({ ...data, tasks: updated });
    };

    const handleAddTask = () => {
      onChange({ ...data, tasks: [...tasks, { name: 'Новое задание', description: '', cost: 10000, deadline_days: 5 }] });
    };

    const handleRemoveTask = (index) => {
      onChange({ ...data, tasks: tasks.filter((_, i) => i !== index) });
    };

    const handleFTermsChange = (field, value) => {
      onChange({ ...data, freelance_terms: { ...fTerms, [field]: value } });
    };

    const totalTasks = tasks.reduce((s, t) => s + (parseFloat(t.cost) || 0), 0);

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Wrench size={20} color="var(--accent-emerald)" />
              <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Задания и результаты (ГПХ / ФЗ-422)</h3>
            </div>
            <button type="button" className="btn btn-primary" onClick={handleAddTask} style={{ padding: '6px 12px', fontSize: '13px' }}>
              <Plus size={14} /> Добавить задание
            </button>
          </div>

          {tasks.map((task, idx) => (
            <div key={idx} style={{ padding: '12px', background: 'rgba(255,255,255,0.03)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-glass)', marginBottom: '10px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 100px 100px 36px', gap: '8px', alignItems: 'end' }}>
                <div className="form-group" style={{ margin: 0 }}>
                  <label className="form-label">Задание / результат</label>
                  <input type="text" className="form-input" value={task.name || ''} onChange={(e) => handleTaskChange(idx, 'name', e.target.value)} />
                </div>
                <div className="form-group" style={{ margin: 0 }}>
                  <label className="form-label">Срок (р.д.)</label>
                  <input type="number" className="form-input" value={task.deadline_days || 5} onChange={(e) => handleTaskChange(idx, 'deadline_days', parseInt(e.target.value, 10) || 1)} />
                </div>
                <div className="form-group" style={{ margin: 0 }}>
                  <label className="form-label">Стоимость (₽)</label>
                  <input type="number" className="form-input" value={task.cost || 0} onChange={(e) => handleTaskChange(idx, 'cost', parseFloat(e.target.value) || 0)} />
                </div>
                <button type="button" className="btn btn-danger" onClick={() => handleRemoveTask(idx)} style={{ padding: '6px', height: '36px' }}>
                  <Trash2 size={14} />
                </button>
              </div>
              <div className="form-group" style={{ marginTop: '8px', marginBottom: 0 }}>
                <label className="form-label">Описание</label>
                <textarea rows={2} className="form-textarea" value={task.description || ''} onChange={(e) => handleTaskChange(idx, 'description', e.target.value)} />
              </div>
            </div>
          ))}

          <div style={{ textAlign: 'right', fontSize: '14px', fontWeight: 700, color: 'var(--accent-emerald)', marginTop: '8px' }}>
            Итого: {totalTasks.toLocaleString('ru-RU', { minimumFractionDigits: 2 })} ₽
          </div>
        </div>

        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <Shield size={20} color="var(--accent-amber)" />
            <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Условия сотрудничества</h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
            <div className="form-group">
              <label className="form-label">Срок рассмотрения акта (р.д.)</label>
              <input type="number" className="form-input" value={fTerms.act_review_days || 3} onChange={(e) => handleFTermsChange('act_review_days', parseInt(e.target.value, 10) || 1)} />
            </div>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', cursor: 'pointer' }}>
                  <input type="checkbox" checked={fTerms.is_self_employed ?? true} onChange={(e) => handleFTermsChange('is_self_employed', e.target.checked)} />
                  Исполнитель — самозанятый (плательщик НПД, ФЗ-422)
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', cursor: 'pointer' }}>
                  <input type="checkbox" checked={fTerms.check_receipt_required ?? true} onChange={(e) => handleFTermsChange('check_receipt_required', e.target.checked)} />
                  Чек из «Мой налог» обязателен
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', cursor: 'pointer' }}>
                  <input type="checkbox" checked={fTerms.ip_rights_transfer ?? true} onChange={(e) => handleFTermsChange('ip_rights_transfer', e.target.checked)} />
                  Передача исключительных прав на результат
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', cursor: 'pointer' }}>
                  <input type="checkbox" checked={fTerms.no_employment_relations ?? true} onChange={(e) => handleFTermsChange('no_employment_relations', e.target.checked)} />
                  Антиподмена трудовых отношений (ТК РФ)
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
}
