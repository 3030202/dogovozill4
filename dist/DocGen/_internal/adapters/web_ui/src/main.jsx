import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import './index.css';

// ── Theme init (before render = no FOUC) ──────────────────────────────
const THEME_KEY = 'docgen-theme';

function getInitialTheme() {
  const saved = localStorage.getItem(THEME_KEY);
  if (saved === 'light' || saved === 'dark') return saved;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  const mc = document.querySelector('meta[name="theme-color"]');
  if (mc) mc.setAttribute('content', theme === 'dark' ? '#0a0a0a' : '#ffffff');
}

applyTheme(getInitialTheme());

window.toggleDocgenTheme = () => {
  const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  applyTheme(next);
  localStorage.setItem(THEME_KEY, next);
  window.dispatchEvent(new CustomEvent('docgen-theme-change', { detail: next }));
};

// ── Mount ─────────────────────────────────────────────────────────────
createRoot(document.getElementById('root')).render(
  <React.StrictMode><App /></React.StrictMode>
);
