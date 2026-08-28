"""Cross-platform Desktop Application for Deterministic Legal Document Generation.

Features clean UI, real-time Russian requisites validation, live sum/VAT calculation,
and single-click GOST DOCX / Typst PDF generation.
"""

from __future__ import annotations
import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from core.templates.registry import ContractRegistry
from core.validator import validate_inn, validate_bik, validate_bank_account
from core.rendering.docx_engine import DocxEngine
from core.rendering.typst_engine import TypstEngine
from core.num_to_words import format_rubles


class DocGenDesktopApp:
    """Desktop GUI application."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("DocGen Omnichannel — Юридическая платформа генерации договоров (Zero-LLM)")
        self.root.geometry("1100x780")
        self.root.minsize(900, 650)

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Color palette
        self.bg_color = "#1E1E2E"
        self.card_bg = "#2A2B3C"
        self.accent_color = "#6366F1"
        self.text_color = "#E0E0E0"
        self.success_color = "#10B981"
        self.error_color = "#EF4444"

        self.root.configure(bg=self.bg_color)
        self._configure_styles()

        self.current_contract_type = tk.StringVar(value="supply")
        self.sample_contract = ContractRegistry.get_sample_contract("supply")

        self._build_ui()
        self._load_sample_data("supply")

    def _configure_styles(self):
        self.style.configure(".", background=self.bg_color, foreground=self.text_color, font=("Helvetica", 10))
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("Card.TFrame", background=self.card_bg, relief="flat")
        self.style.configure("TLabel", background=self.bg_color, foreground=self.text_color, font=("Helvetica", 10))
        self.style.configure("Card.TLabel", background=self.card_bg, foreground=self.text_color, font=("Helvetica", 10))
        self.style.configure("Header.TLabel", background=self.bg_color, foreground="#FFFFFF", font=("Helvetica", 14, "bold"))
        self.style.configure("CardHeader.TLabel", background=self.card_bg, foreground="#A5B4FC", font=("Helvetica", 11, "bold"))
        self.style.configure("Primary.TButton", font=("Helvetica", 10, "bold"), background=self.accent_color, foreground="#FFFFFF")
        self.style.map("Primary.TButton", background=[("active", "#4F46E5")])
        self.style.configure("Success.TButton", font=("Helvetica", 10, "bold"), background=self.success_color, foreground="#FFFFFF")
        self.style.map("Success.TButton", background=[("active", "#059669")])

    def _build_ui(self):
        # Top Header Bar
        top_bar = ttk.Frame(self.root, padding=12)
        top_bar.pack(fill="x")

        lbl_title = ttk.Label(top_bar, text="🏛️ DocGen Platform (Zero-LLM / ГОСТ РФ)", style="Header.TLabel")
        lbl_title.pack(side="left")

        lbl_type = ttk.Label(top_bar, text="Вид договора:")
        lbl_type.pack(side="left", padx=(30, 8))

        type_options = [
            ("Поставка товаров (ГК РФ гл. 30 §3)", "supply"),
            ("Возмездное оказание услуг (ГК РФ гл. 39)", "services"),
            ("Подрядные работы (ГК РФ гл. 37)", "work"),
            ("Соглашение NDA (ФЗ № 98-ФЗ)", "nda"),
        ]
        self.type_combobox = ttk.Combobox(
            top_bar,
            values=[opt[0] for opt in type_options],
            state="readonly",
            width=38
        )
        self.type_combobox.current(0)
        self.type_combobox.pack(side="left")
        self.type_combobox.bind("<<ComboboxSelected>>", self._on_type_changed)

        btn_sample = ttk.Button(top_bar, text="🔄 Сбросить к эталону", command=self._reload_current_sample)
        btn_sample.pack(side="right", padx=6)

        # Main Split Content (Notebook / Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=6)

        # Tab 1: Party & Contract Details
        self.tab_parties = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_parties, text="1. Стороны и Реквизиты")

        # Tab 2: Specification & Items
        self.tab_spec = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_spec, text="2. Спецификация и Суммы")

        # Tab 3: Terms & Preview
        self.tab_terms = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_terms, text="3. Условия и Генерация")

        self._build_parties_tab()
        self._build_spec_tab()
        self._build_terms_tab()

    def _build_parties_tab(self):
        # Top Meta Box (Number, Date, City)
        meta_frame = ttk.Frame(self.tab_parties, style="Card.TFrame", padding=10)
        meta_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(meta_frame, text="Номер договора:", style="Card.TLabel").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.ent_meta_num = ttk.Entry(meta_frame, width=18)
        self.ent_meta_num.grid(row=0, column=1, padx=6, pady=2)

        ttk.Label(meta_frame, text="Дата заключения:", style="Card.TLabel").grid(row=0, column=2, sticky="w", padx=12, pady=2)
        self.ent_meta_date = ttk.Entry(meta_frame, width=16)
        self.ent_meta_date.grid(row=0, column=3, padx=6, pady=2)

        ttk.Label(meta_frame, text="Город:", style="Card.TLabel").grid(row=0, column=4, sticky="w", padx=12, pady=2)
        self.ent_meta_city = ttk.Entry(meta_frame, width=16)
        self.ent_meta_city.grid(row=0, column=5, padx=6, pady=2)

        # Parties Grid: Client (Left) and Vendor (Right)
        parties_grid = ttk.Frame(self.tab_parties)
        parties_grid.pack(fill="both", expand=True)

        self.client_entries = self._create_party_card(parties_grid, "СТОРОНА 1 (ЗАКАЗЧИК / ПОКУПАТЕЛЬ)", 0)
        self.vendor_entries = self._create_party_card(parties_grid, "СТОРОНА 2 (ИСПОЛНИТЕЛЬ / ПОСТАВЩИК)", 1)

    def _create_party_card(self, parent, title: str, col: int) -> dict:
        frame = ttk.Frame(parent, style="Card.TFrame", padding=12)
        frame.grid(row=0, column=col, sticky="nsew", padx=6, pady=4)
        parent.columnconfigure(col, weight=1)

        ttk.Label(frame, text=title, style="CardHeader.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        fields = [
            ("Наименование / ФИО:", "full_name", 34),
            ("ИНН:", "inn", 20),
            ("КПП:", "kpp", 20),
            ("ОГРН/ОГРНИП:", "ogrn", 20),
            ("Юр. адрес:", "legal_address", 34),
            ("Должность подписанта:", "signatory_position", 25),
            ("ФИО подписанта:", "signatory_name", 25),
            ("Основание полномочий:", "signatory_basis", 25),
            ("Банк:", "bank_name", 34),
            ("БИК банка:", "bik", 20),
            ("Расчетный счет:", "account", 30),
            ("Корр. счет:", "corr_account", 30),
        ]

        entries = {}
        for idx, (label_text, key, width) in enumerate(fields, start=1):
            ttk.Label(frame, text=label_text, style="Card.TLabel").grid(row=idx, column=0, sticky="w", pady=2)
            ent = ttk.Entry(frame, width=width)
            ent.grid(row=idx, column=1, sticky="w", padx=6, pady=2)
            entries[key] = ent

            if key in ("inn", "bik", "account"):
                ent.bind("<KeyRelease>", lambda e: self._validate_live_requisites())

        # Validation status label
        lbl_status = ttk.Label(frame, text="✅ Реквизиты проверены", foreground=self.success_color, style="Card.TLabel", font=("Helvetica", 9, "bold"))
        lbl_status.grid(row=len(fields) + 1, column=0, columnspan=2, sticky="w", pady=(8, 0))
        entries["_status_label"] = lbl_status

        return entries

    def _build_spec_tab(self):
        # Items / Stages List
        spec_frame = ttk.Frame(self.tab_spec, style="Card.TFrame", padding=10)
        spec_frame.pack(fill="both", expand=True)

        lbl_spec = ttk.Label(spec_frame, text="📦 Спецификация товаров / перечень услуг / этапы работ", style="CardHeader.TLabel")
        lbl_spec.pack(anchor="w", pady=(0, 6))

        columns = ("col_num", "col_name", "col_unit", "col_qty", "col_price", "col_total")
        self.tree_items = ttk.Treeview(spec_frame, columns=columns, show="headings", height=8)
        self.tree_items.heading("col_num", text="№")
        self.tree_items.heading("col_name", text="Наименование")
        self.tree_items.heading("col_unit", text="Ед.")
        self.tree_items.heading("col_qty", text="Кол-во")
        self.tree_items.heading("col_price", text="Цена (руб.)")
        self.tree_items.heading("col_total", text="Сумма (руб.)")

        self.tree_items.column("col_num", width=40, anchor="center")
        self.tree_items.column("col_name", width=380, anchor="w")
        self.tree_items.column("col_unit", width=60, anchor="center")
        self.tree_items.column("col_qty", width=70, anchor="e")
        self.tree_items.column("col_price", width=110, anchor="e")
        self.tree_items.column("col_total", width=120, anchor="e")

        self.tree_items.pack(fill="both", expand=True, pady=4)

        # Bottom Totals Frame
        tot_frame = ttk.Frame(self.tab_spec, padding=8)
        tot_frame.pack(fill="x")

        self.lbl_total_sum = ttk.Label(tot_frame, text="ИТОГО: 0,00 руб. (в т.ч. НДС 20%)", font=("Helvetica", 12, "bold"), foreground="#FFFFFF")
        self.lbl_total_sum.pack(side="left")

    def _build_terms_tab(self):
        terms_frame = ttk.Frame(self.tab_terms, style="Card.TFrame", padding=12)
        terms_frame.pack(fill="x", pady=6)

        ttk.Label(terms_frame, text="⚙️ Настройки оплаты и налогового режима", style="CardHeader.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        ttk.Label(terms_frame, text="Условия оплаты:", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=4)
        self.combo_payment = ttk.Combobox(
            terms_frame,
            values=["100% Постоплата (5 рабочих дней)", "50% Аванс / 50% Постоплата", "100% Предоплата"],
            state="readonly",
            width=36
        )
        self.combo_payment.current(0)
        self.combo_payment.grid(row=1, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(terms_frame, text="Ставка НДС:", style="Card.TLabel").grid(row=2, column=0, sticky="w", pady=4)
        self.combo_vat = ttk.Combobox(
            terms_frame,
            values=["20% (НДС включен в цену)", "10% (НДС включен в цену)", "Без НДС (УСН / ст. 346.11 НК РФ)"],
            state="readonly",
            width=36
        )
        self.combo_vat.current(0)
        self.combo_vat.grid(row=2, column=1, sticky="w", padx=6, pady=4)

        # Action Buttons Card
        btn_frame = ttk.Frame(self.tab_terms, style="Card.TFrame", padding=16)
        btn_frame.pack(fill="x", pady=12)

        ttk.Label(btn_frame, text="🚀 Экспорт юридического документа:", style="CardHeader.TLabel").pack(anchor="w", pady=(0, 10))

        btn_docx = ttk.Button(btn_frame, text="📥 Сгенерировать DOCX (ГОСТ Р 7.0.97-2016)", style="Primary.TButton", command=self._export_docx)
        btn_docx.pack(side="left", padx=(0, 12), ipady=6)

        btn_pdf = ttk.Button(btn_frame, text="📑 Сгенерировать PDF (Typst Vector)", style="Success.TButton", command=self._export_pdf)
        btn_pdf.pack(side="left", padx=6, ipady=6)

    def _on_type_changed(self, event=None):
        types_map = ["supply", "services", "work", "nda"]
        idx = self.type_combobox.current()
        selected_type = types_map[idx]
        self.current_contract_type.set(selected_type)
        self._load_sample_data(selected_type)

    def _reload_current_sample(self):
        self._load_sample_data(self.current_contract_type.get())
        messagebox.showinfo("Успешно", "Форма сброшена к эталонным данным.")

    def _load_sample_data(self, contract_type: str):
        sample = ContractRegistry.get_sample_contract(contract_type)
        self.sample_contract = sample

        # Metadata
        self.ent_meta_num.delete(0, tk.END)
        self.ent_meta_num.insert(0, sample.metadata.contract_number)
        self.ent_meta_date.delete(0, tk.END)
        self.ent_meta_date.insert(0, sample.metadata.contract_date)
        self.ent_meta_city.delete(0, tk.END)
        self.ent_meta_city.insert(0, sample.metadata.city)

        # Parties
        self._fill_party_entries(self.client_entries, sample.client)
        self._fill_party_entries(self.vendor_entries, sample.vendor)

        # Specification Table
        for row in self.tree_items.get_children():
            self.tree_items.delete(row)

        if hasattr(sample, "items"):
            for i, item in enumerate(sample.items, start=1):
                self.tree_items.insert("", "end", values=(
                    i, item.name, item.unit, f"{item.quantity:g}",
                    format_rubles(item.price_per_unit), format_rubles(item.total_price)
                ))
        elif hasattr(sample, "stages"):
            for stage in sample.stages:
                self.tree_items.insert("", "end", values=(
                    stage.stage_number, stage.title, "этап", "1",
                    format_rubles(stage.cost), format_rubles(stage.cost)
                ))
        elif hasattr(sample, "services"):
            for i, s in enumerate(sample.services, start=1):
                self.tree_items.insert("", "end", values=(
                    i, s.name, "услуга", "1",
                    format_rubles(s.price), format_rubles(s.price)
                ))

        total_amount = getattr(sample, "total_amount", 0.0)
        self.lbl_total_sum.config(text=f"ИТОГО: {format_rubles(total_amount)} руб. (в т.ч. НДС 20%)")
        self._validate_live_requisites()

    def _fill_party_entries(self, entries: dict, party):
        data = party.model_dump()
        bank = data.get("bank_requisites", {})
        for k, ent in entries.items():
            if k == "_status_label":
                continue
            ent.delete(0, tk.END)
            if k in data and data[k] is not None:
                ent.insert(0, str(data[k]))
            elif k in bank and bank[k] is not None:
                ent.insert(0, str(bank[k]))

    def _validate_live_requisites(self):
        for entries in (self.client_entries, self.vendor_entries):
            inn = entries["inn"].get().strip()
            bik = entries["bik"].get().strip()
            acc = entries["account"].get().strip()

            inn_ok, inn_msg = validate_inn(inn)
            bik_ok, bik_msg = validate_bik(bik)
            acc_ok, acc_msg = validate_bank_account(acc, bik) if bik_ok else (False, "БИК не верен")

            lbl = entries["_status_label"]
            if inn_ok and bik_ok and acc_ok:
                lbl.config(text="✅ Реквизиты проверены (ИНН/БИК/Счет корректны)", foreground=self.success_color)
            else:
                errs = []
                if not inn_ok:
                    errs.append("ИНН")
                if not bik_ok:
                    errs.append("БИК")
                if not acc_ok:
                    errs.append("Счет")
                lbl.config(text=f"⚠️ Ошибка контрольной суммы: {', '.join(errs)}", foreground=self.error_color)

    def _collect_current_contract(self):
        contract_type = self.current_contract_type.get()
        sample = ContractRegistry.get_sample_contract(contract_type)

        # Update metadata
        sample.metadata.contract_number = self.ent_meta_num.get().strip() or sample.metadata.contract_number
        sample.metadata.contract_date = self.ent_meta_date.get().strip() or sample.metadata.contract_date
        sample.metadata.city = self.ent_meta_city.get().strip() or sample.metadata.city

        # Update client
        sample.client.full_name = self.client_entries["full_name"].get().strip() or sample.client.full_name
        sample.client.inn = self.client_entries["inn"].get().strip() or sample.client.inn
        sample.client.kpp = self.client_entries["kpp"].get().strip() or sample.client.kpp
        sample.client.ogrn = self.client_entries["ogrn"].get().strip() or sample.client.ogrn
        sample.client.legal_address = self.client_entries["legal_address"].get().strip() or sample.client.legal_address
        sample.client.signatory_name = self.client_entries["signatory_name"].get().strip() or sample.client.signatory_name
        sample.client.bank_requisites.bik = self.client_entries["bik"].get().strip() or sample.client.bank_requisites.bik
        sample.client.bank_requisites.account = self.client_entries["account"].get().strip() or sample.client.bank_requisites.account

        # Update vendor
        sample.vendor.full_name = self.vendor_entries["full_name"].get().strip() or sample.vendor.full_name
        sample.vendor.inn = self.vendor_entries["inn"].get().strip() or sample.vendor.inn
        sample.vendor.kpp = self.vendor_entries["kpp"].get().strip() or sample.vendor.kpp
        sample.vendor.ogrn = self.vendor_entries["ogrn"].get().strip() or sample.vendor.ogrn
        sample.vendor.legal_address = self.vendor_entries["legal_address"].get().strip() or sample.vendor.legal_address
        sample.vendor.signatory_name = self.vendor_entries["signatory_name"].get().strip() or sample.vendor.signatory_name
        sample.vendor.bank_requisites.bik = self.vendor_entries["bik"].get().strip() or sample.vendor.bank_requisites.bik
        sample.vendor.bank_requisites.account = self.vendor_entries["account"].get().strip() or sample.vendor.bank_requisites.account

        return sample

    def _export_docx(self):
        try:
            contract = self._collect_current_contract()
            num_clean = contract.metadata.contract_number.replace("/", "_")
            default_filename = f"Contract_{self.current_contract_type.get()}_{num_clean}.docx"

            out_path = filedialog.asksaveasfilename(
                title="Сохранить договор DOCX",
                defaultextension=".docx",
                initialfile=default_filename,
                filetypes=[("Word Document", "*.docx")]
            )
            if not out_path:
                return

            buf = DocxEngine.generate(contract)
            with open(out_path, "wb") as f:
                f.write(buf.getvalue())

            messagebox.showinfo("Успех", f"Документ успешно сформирован и сохранен по ГОСТ Р 7.0.97-2016:\n{out_path}")
        except Exception as e:
            messagebox.showerror("Ошибка генерации", str(e))

    def _export_pdf(self):
        try:
            contract = self._collect_current_contract()
            num_clean = contract.metadata.contract_number.replace("/", "_")
            default_filename = f"Contract_{self.current_contract_type.get()}_{num_clean}.pdf"

            out_path = filedialog.asksaveasfilename(
                title="Сохранить договор PDF",
                defaultextension=".pdf",
                initialfile=default_filename,
                filetypes=[("PDF Document", "*.pdf"), ("Typst Source", "*.typ")]
            )
            if not out_path:
                return

            pdf_bytes = TypstEngine.compile_pdf(contract)
            with open(out_path, "wb") as f:
                f.write(pdf_bytes)

            messagebox.showinfo("Успех", f"Файл успешно сохранен:\n{out_path}")
        except Exception as e:
            messagebox.showerror("Ошибка генерации", str(e))


def main():
    root = tk.Tk()
    app = DocGenDesktopApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
