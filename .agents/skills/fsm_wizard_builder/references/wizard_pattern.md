# Эталонный паттерн FSM-визарда

Полная структура хэндлер-цепочки из `adapters/telegram_bot/handlers/wizard.py`.

## Архитектура потока

```
/start → Выбор типа (callback) → Номер/Дата → ИНН Заказчика → ИНН Поставщика
  → Условия оплаты (callback) → НДС (callback) → Сводка + Генерация (callback)
```

## StatesGroup

```python
class ContractWizard(StatesGroup):
    contract_type = State()       # inline-кнопки выбора типа
    number_and_date = State()     # free-text: "2025/П-01, 15.02.2025"
    client_inn = State()          # free-text + validate_inn()
    vendor_inn = State()          # free-text + validate_inn()
    payment_terms = State()       # inline-кнопки (prepay/postpay/50_50)
    vat_mode = State()            # inline-кнопки (20%/10%/exempt)
    ready_to_generate = State()   # сводка + кнопки генерации (docx/pdf/both)
```

## Инициализация (callback → первый state)

```python
@router.callback_query(F.data.startswith("type:"))
async def on_contract_type_selected(callback: CallbackQuery, state: FSMContext):
    contract_type = callback.data.split(":")[1]
    await state.update_data(contract_type=contract_type)

    # Загрузить эталонные данные как базу
    sample = ContractRegistry.get_sample_contract(contract_type)
    await state.update_data(contract_data=sample.model_dump())

    await state.set_state(ContractWizard.number_and_date)
    await callback.message.edit_text("Введите номер и дату...")
```

## Free-text хэндлер с валидацией

```python
@router.message(ContractWizard.client_inn)
async def process_client_inn(message: Message, state: FSMContext):
    data = await state.get_data()
    contract_data = data.get("contract_data", {})

    if message.text and message.text != "/skip":
        inn = message.text.strip()
        is_ok, msg = validate_inn(inn)
        if not is_ok:
            # Ошибка → остаёмся в текущем state
            await message.answer(f"⚠️ Ошибка: {msg}\nПопробуйте снова или /skip:")
            return
        contract_data["client"]["inn"] = inn

    await state.update_data(contract_data=contract_data)
    await state.set_state(ContractWizard.vendor_inn)
    await message.answer("Введите ИНН Поставщика...")
```

## Callback хэндлер (enum-поля)

```python
@router.callback_query(F.data.startswith("pay:"))
async def process_payment_selection(callback: CallbackQuery, state: FSMContext):
    pay_mode = callback.data.split(":")[1]
    data = await state.get_data()
    contract_data = data.get("contract_data", {})

    contract_data["payment_terms"]["type"] = pay_mode

    await state.update_data(contract_data=contract_data)
    await state.set_state(ContractWizard.vat_mode)
    await callback.message.edit_text(
        "Выберите ставку НДС:",
        reply_markup=get_vat_keyboard()
    )
```

## Финализация и генерация

```python
@router.callback_query(F.data.startswith("gen:"))
async def generate_and_send_document(callback: CallbackQuery, state: FSMContext):
    fmt = callback.data.split(":")[1]  # "docx" | "pdf" | "both"
    data = await state.get_data()
    contract_type = data.get("contract_type", "supply")
    contract_data = data.get("contract_data")

    # Финальная валидация через Pydantic
    contract = ContractRegistry.parse_contract(contract_type, contract_data)

    if fmt in ("docx", "both"):
        docx_buf = DocxEngine.generate(contract)
        # ... отправка BufferedInputFile

    if fmt in ("pdf", "both"):
        pdf_bytes = TypstEngine.compile_pdf(contract)
        # ... отправка BufferedInputFile

    await callback.answer("Документ успешно сформирован!")
```

## Клавиатуры (keyboards.py)

```python
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_payment_terms_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💯 100% предоплата", callback_data="pay:prepay")],
        [InlineKeyboardButton(text="50/50", callback_data="pay:50_50")],
        [InlineKeyboardButton(text="Постоплата", callback_data="pay:postpay")],
    ])
```

**Правило callback_data:** Формат `prefix:value`, где prefix уникален для каждого enum-поля.

## Регистрация роутера (bot.py)

```python
from adapters.telegram_bot.handlers.wizard import router as wizard_router
dp.include_router(wizard_router)
```
