"""FSM Wizard Handlers for interactive contract assembly and delivery."""

import io
import time
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from adapters.telegram_bot.keyboards import (
    get_download_format_keyboard,
    get_payment_terms_keyboard,
    get_vat_keyboard,
)
from core.templates.registry import ContractRegistry
from core.rendering.docx_engine import DocxEngine
from core.rendering.typst_engine import TypstEngine
from core.validator import validate_inn, validate_bik, validate_bank_account

router = Router()


class ContractWizard(StatesGroup):
    contract_type = State()
    number_and_date = State()
    client_name = State()
    client_inn = State()
    client_bank = State()
    vendor_name = State()
    vendor_inn = State()
    vendor_bank = State()
    amount_and_items = State()
    payment_terms = State()
    vat_mode = State()
    ready_to_generate = State()


@router.message(F.text == "🚀 Быстрый пример")
async def cmd_quick_sample(message: Message):
    """Instantly generate and send realistic sample DOCX document."""
    await message.answer("⚡ *Генерация эталонного договора поставки по ГОСТ...*", parse_mode="Markdown")

    sample_contract = ContractRegistry.get_sample_contract("supply")
    docx_buf = DocxEngine.generate(sample_contract)

    docx_file = BufferedInputFile(
        file=docx_buf.getvalue(),
        filename=f"Sample_Supply_Contract_{sample_contract.metadata.contract_number.replace('/', '_')}.docx"
    )

    await message.answer_document(
        document=docx_file,
        caption=(
            f"✅ **Договор поставки № {sample_contract.metadata.contract_number} сгенерирован!**\n\n"
            f"• **Сумма:** {sample_contract.total_amount:,.2f} руб. (с НДС 20%)\n"
            f"• **Покупатель:** {sample_contract.client.full_name}\n"
            f"• **Поставщик:** {sample_contract.vendor.full_name}\n"
            f"• **Оформление:** ГОСТ Р 7.0.97-2016 (поля 25/15/20/20, XML шрифты, таблицы)"
        ),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("type:"))
async def on_contract_type_selected(callback: CallbackQuery, state: FSMContext):
    """Handle contract type selection."""
    contract_type = callback.data.split(":")[1]
    await state.update_data(contract_type=contract_type)

    # Initialize draft based on sample data
    sample = ContractRegistry.get_sample_contract(contract_type)
    await state.update_data(contract_data=sample.model_dump())

    await state.set_state(ContractWizard.number_and_date)
    await callback.message.edit_text(
        f"📝 **Выбран договор:** {ContractRegistry._metadata[contract_type]['title']}\n\n"
        f"Введите **номер и дату договора** через запятую\n"
        f"_(например: `2025/П-01, 15.02.2025` или нажмите /skip для значений по умолчанию)_:",
        parse_mode="Markdown"
    )


@router.message(ContractWizard.number_and_date)
async def process_number_date(message: Message, state: FSMContext):
    """Process contract number and date."""
    data = await state.get_data()
    contract_data = data.get("contract_data", {})

    if message.text and message.text != "/skip":
        parts = [p.strip() for p in message.text.split(",")]
        if len(parts) >= 1 and parts[0]:
            contract_data["metadata"]["contract_number"] = parts[0]
        if len(parts) >= 2 and parts[1]:
            contract_data["metadata"]["contract_date"] = parts[1]

    await state.update_data(contract_data=contract_data)
    await state.set_state(ContractWizard.client_inn)

    await message.answer(
        f"🏢 **Реквизиты Заказчика / Покупателя:**\n\n"
        f"Введите **ИНН Заказчика** (10 цифр для ЮЛ или 12 цифр для ИП)\n"
        f"_(или /skip для значения `{contract_data['client']['inn']}`):_",
        parse_mode="Markdown"
    )


@router.message(ContractWizard.client_inn)
async def process_client_inn(message: Message, state: FSMContext):
    """Process and algorithmically validate client INN."""
    data = await state.get_data()
    contract_data = data.get("contract_data", {})

    if message.text and message.text != "/skip":
        inn = message.text.strip()
        is_ok, msg = validate_inn(inn)
        if not is_ok:
            await message.answer(f"⚠️ **Ошибка контрольной суммы ИНН:** {msg}\nПопробуйте ввести ИНН снова или введите /skip:")
            return
        contract_data["client"]["inn"] = inn

    await state.update_data(contract_data=contract_data)
    await state.set_state(ContractWizard.vendor_inn)

    await message.answer(
        f"🏬 **Реквизиты Исполнителя / Поставщика:**\n\n"
        f"Введите **ИНН Поставщика** (10 цифр для ЮЛ или 12 цифр для ИП)\n"
        f"_(или /skip для значения `{contract_data['vendor']['inn']}`):_",
        parse_mode="Markdown"
    )


@router.message(ContractWizard.vendor_inn)
async def process_vendor_inn(message: Message, state: FSMContext):
    """Process and algorithmically validate vendor INN."""
    data = await state.get_data()
    contract_data = data.get("contract_data", {})

    if message.text and message.text != "/skip":
        inn = message.text.strip()
        is_ok, msg = validate_inn(inn)
        if not is_ok:
            await message.answer(f"⚠️ **Ошибка контрольной суммы ИНН:** {msg}\nПопробуйте ввести ИНН снова или /skip:")
            return
        contract_data["vendor"]["inn"] = inn

    await state.update_data(contract_data=contract_data)
    await state.set_state(ContractWizard.payment_terms)

    await message.answer(
        "💳 **Выберите условия и график оплаты:**",
        reply_markup=get_payment_terms_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("pay:"))
async def process_payment_selection(callback: CallbackQuery, state: FSMContext):
    """Process payment term button."""
    pay_mode = callback.data.split(":")[1]
    data = await state.get_data()
    contract_data = data.get("contract_data", {})

    contract_data["payment_terms"]["type"] = pay_mode
    if pay_mode == "50_50":
        contract_data["payment_terms"]["advance_percent"] = 50.0

    await state.update_data(contract_data=contract_data)
    await state.set_state(ContractWizard.vat_mode)

    await callback.message.edit_text(
        "📊 **Выберите ставку и режим НДС:**",
        reply_markup=get_vat_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("vat:"))
async def process_vat_selection(callback: CallbackQuery, state: FSMContext):
    """Process VAT selection and generate contract preview."""
    vat_choice = callback.data.split(":")[1]
    data = await state.get_data()
    contract_type = data.get("contract_type", "supply")
    contract_data = data.get("contract_data", {})

    if vat_choice == "exempt":
        contract_data["is_exempt_vat"] = True
        contract_data["vat_rate"] = 0
    elif vat_choice == "10_incl":
        contract_data["vat_rate"] = 10
        contract_data["vat_included"] = True
        contract_data["is_exempt_vat"] = False
    else:
        contract_data["vat_rate"] = 20
        contract_data["vat_included"] = True
        contract_data["is_exempt_vat"] = False

    await state.update_data(contract_data=contract_data)
    await state.set_state(ContractWizard.ready_to_generate)

    # Parse and generate docx
    contract = ContractRegistry.parse_contract(contract_type, contract_data)
    total = getattr(contract, "total_amount", 0.0)

    summary_text = (
        f"✅ **Все параметры договора согласованы!**\n\n"
        f"• **Договор:** {contract.metadata.contract_number} от {contract.metadata.contract_date}\n"
        f"• **Заказчик:** {contract.client.full_name} (ИНН {contract.client.inn})\n"
        f"• **Поставщик:** {contract.vendor.full_name} (ИНН {contract.vendor.inn})\n"
        f"• **Итоговая сумма:** {total:,.2f} руб.\n"
        f"• **Условия оплаты:** {contract.payment_terms.type}\n\n"
        f"Выберите формат для мгновенного скачивания:"
    )

    await callback.message.edit_text(
        summary_text,
        reply_markup=get_download_format_keyboard(draft_id="current"),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("gen:"))
async def generate_and_send_document(callback: CallbackQuery, state: FSMContext):
    """Generate DOCX / PDF and deliver as attachment."""
    fmt = callback.data.split(":")[1]
    data = await state.get_data()
    contract_type = data.get("contract_type", "supply")
    contract_data = data.get("contract_data")

    if not contract_data:
        # Fallback to sample contract
        contract = ContractRegistry.get_sample_contract(contract_type)
    else:
        contract = ContractRegistry.parse_contract(contract_type, contract_data)

    num_str = contract.metadata.contract_number.replace("/", "_")

    if fmt in ("docx", "both"):
        docx_buf = DocxEngine.generate(contract)
        docx_file = BufferedInputFile(
            file=docx_buf.getvalue(),
            filename=f"Contract_{contract_type}_{num_str}.docx"
        )
        await callback.message.answer_document(
            document=docx_file,
            caption=f"📄 **Договор DOCX (ГОСТ Р 7.0.97-2016)** № {contract.metadata.contract_number}",
            parse_mode="Markdown"
        )

    if fmt in ("pdf", "both"):
        pdf_bytes = TypstEngine.compile_pdf(contract)
        if pdf_bytes.startswith(b"%PDF"):
            pdf_file = BufferedInputFile(
                file=pdf_bytes,
                filename=f"Contract_{contract_type}_{num_str}.pdf"
            )
            await callback.message.answer_document(
                document=pdf_file,
                caption=f"📑 **Векторный PDF** № {contract.metadata.contract_number}",
                parse_mode="Markdown"
            )
        else:
            typ_file = BufferedInputFile(
                file=pdf_bytes,
                filename=f"Contract_{contract_type}_{num_str}.typ"
            )
            await callback.message.answer_document(
                document=typ_file,
                caption="📝 **Исходный Typst-код документа** (скомпилируйте через `typst compile`)",
                parse_mode="Markdown"
            )

    await callback.answer("Документ успешно сформирован!")
