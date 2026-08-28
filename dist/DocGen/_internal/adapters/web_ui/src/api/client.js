/**
 * API Client for DocGen Platform
 */

const API_BASE = '/api';

export async function fetchContractTypes() {
  const res = await fetch(`${API_BASE}/contracts/types`);
  if (!res.ok) throw new Error('Не удалось загрузить типы договоров');
  return res.json();
}

export async function fetchSampleContract(contractType) {
  const res = await fetch(`${API_BASE}/contracts/sample/${contractType}`);
  if (!res.ok) throw new Error('Не удалось загрузить образец договора');
  return res.json();
}

export async function validatePartyRequisites(partyData) {
  const res = await fetch(`${API_BASE}/contracts/validate-party`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(partyData),
  });
  if (!res.ok) throw new Error('Ошибка валидации реквизитов');
  return res.json();
}

export async function suggestPartyByInn(inn) {
  const res = await fetch(`${API_BASE}/contracts/suggest/${encodeURIComponent(inn)}`);
  if (!res.ok) return { found: false, valid_inn: false };
  return res.json();
}

export async function validateFullContract(contractType, data) {
  const res = await fetch(`${API_BASE}/contracts/validate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ contract_type: contractType, data }),
  });
  if (!res.ok) throw new Error('Ошибка валидации договора');
  return res.json();
}

export async function calculateFinancials(params) {
  const res = await fetch(`${API_BASE}/contracts/calculate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error('Ошибка расчета сумм');
  return res.json();
}

export async function downloadDocx(contractType, data) {
  const res = await fetch(`${API_BASE}/contracts/generate/docx`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ contract_type: contractType, data }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Ошибка генерации DOCX' }));
    throw new Error(err.detail || 'Ошибка генерации DOCX');
  }
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  const contractNum = (data?.metadata?.contract_number || 'draft').replace(/[/\\?%*:|"<>]/g, '_');
  a.href = url;
  a.download = `Contract_${contractType}_${contractNum}.docx`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}

export async function downloadPdf(contractType, data) {
  const res = await fetch(`${API_BASE}/contracts/generate/pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ contract_type: contractType, data }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Ошибка генерации PDF' }));
    throw new Error(err.detail || 'Ошибка генерации PDF');
  }
  const blob = await res.blob();
  const isPdf = res.headers.get('Content-Type')?.includes('pdf');
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  const contractNum = (data?.metadata?.contract_number || 'draft').replace(/[/\\?%*:|"<>]/g, '_');
  a.href = url;
  a.download = `Contract_${contractType}_${contractNum}.${isPdf ? 'pdf' : 'typ'}`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}

export async function saveDraft(contractType, data, title, id = null) {
  const res = await fetch(`${API_BASE}/drafts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id, title, contract_type: contractType, data }),
  });
  if (!res.ok) throw new Error('Ошибка сохранения черновика');
  return res.json();
}

export async function listDrafts() {
  const res = await fetch(`${API_BASE}/drafts`);
  if (!res.ok) throw new Error('Ошибка получения списка черновиков');
  return res.json();
}

export async function getDraft(id) {
  const res = await fetch(`${API_BASE}/drafts/${id}`);
  if (!res.ok) throw new Error('Ошибка загрузки черновика');
  return res.json();
}

export async function deleteDraft(id) {
  const res = await fetch(`${API_BASE}/drafts/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Ошибка удаления черновика');
  return res.json();
}
