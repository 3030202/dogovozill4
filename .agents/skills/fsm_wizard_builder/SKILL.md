---
name: fsm_wizard_builder
description: |
  Генерация FSM-визардов для Telegram (aiogram 3.x) на основе Pydantic-схем.
  Активировать при: создании нового типа договора для Telegram-бота, добавлении
  хэндлеров, FSM, wizard, диалогов ввода, StatesGroup, Telegram-визард.
---

# FSM Wizard Builder — Telegram (aiogram 3.x)

Этот скилл описывает паттерн генерации линейных и древовидных FSM-диалогов
для Telegram-бота на основе существующих Pydantic-схем договоров.

## Ключевые файлы проекта

- Эталонный визард: `adapters/telegram_bot/handlers/wizard.py`
- Клавиатуры: `adapters/telegram_bot/keyboards.py`
- Точка входа бота: `adapters/telegram_bot/bot.py`
- Pydantic-модели: `core/models/base.py` (Party, BankRequisites, BaseContract)
- Валидаторы: `core/validator.py`
- Реестр типов: `core/templates/registry.py`

## 1. Паттерн StatesGroup

Каждый визард начинается с `StatesGroup`, где состояния соответствуют
логическим блокам ввода (НЕ отдельным полям Pydantic-модели):

```python
from aiogram.fsm.state import State, StatesGroup

class ContractWizard(StatesGroup):
    contract_type = State()      # Выбор типа договора
    number_and_date = State()    # Номер + дата (группировка связанных полей)
    client_inn = State()         # ИНН заказчика (отдельно — требует валидации)
    vendor_inn = State()         # ИНН поставщика
    payment_terms = State()      # Условия оплаты (enum → inline-кнопки)
    vat_mode = State()           # НДС (enum → inline-кнопки)
    ready_to_generate = State()  # Подтверждение и генерация
```

### Правила маппинга Pydantic → States:

| Тип поля Pydantic | Тип State | UI |
|---|---|---|
| `str` (свободный ввод) | `State()` + `@router.message()` | Free-text input |
| `str` с валидатором (ИНН, БИК) | `State()` + валидация перед переходом | Free-text + ошибка при невалидном |
| `Enum` / ограниченный набор | `State()` + `@router.callback_query()` | Inline-кнопки |
| `Optional[...]` | Любой из выше | Поддержка `/skip` |
| Группа связанных полей | Один `State()` с парсингом | Ввод через запятую |

## 2. Структура хэндлера

Каждый хэндлер следует единому паттерну:

```python
@router.message(ContractWizard.some_state)
async def process_some_field(message: Message, state: FSMContext):
    """Обработка поля X."""
    # 1. Получить текущие данные
    data = await state.get_data()
    contract_data = data.get("contract_data", {})

    # 2. Валидация и сохранение (если не /skip)
    if message.text and message.text != "/skip":
        value = message.text.strip()
        # Валидация (если нужна)
        is_ok, msg = validate_something(value)
        if not is_ok:
            await message.answer(f"⚠️ **Ошибка:** {msg}\nПопробуйте снова или /skip:")
            return  # НЕ переходим — остаёмся в текущем состоянии
        contract_data["field"] = value

    # 3. Сохранить и перейти к следующему состоянию
    await state.update_data(contract_data=contract_data)
    await state.set_state(ContractWizard.next_state)

    # 4. Отправить промпт следующего шага
    await message.answer(
        "📝 **Следующий шаг:**\nВведите значение или /skip:",
        parse_mode="Markdown"
    )
```

### Для Enum-полей (через callback_query):

```python
@router.callback_query(F.data.startswith("prefix:"))
async def process_enum_field(callback: CallbackQuery, state: FSMContext):
    choice = callback.data.split(":")[1]
    data = await state.get_data()
    contract_data = data.get("contract_data", {})

    contract_data["enum_field"] = choice

    await state.update_data(contract_data=contract_data)
    await state.set_state(ContractWizard.next_state)

    await callback.message.edit_text(
        "Следующий шаг...",
        reply_markup=next_keyboard(),
        parse_mode="Markdown"
    )
```

## 3. Мгновенная валидация

Валидация выполняется **на каждом шаге** ДО перехода к следующему состоянию:

- **ИНН:** `validate_inn()` из `core/validator.py`
- **БИК:** `validate_bik()` из `core/validator.py`
- **Расчётный счёт:** `validate_bank_account()` из `core/validator.py`
- **Финальная:** `ContractRegistry.parse_contract()` собирает и валидирует
  через Pydantic (`model_validate`) перед генерацией документа

**Принцип:** При ошибке валидации — вернуть сообщение об ошибке и `return`
(не вызывать `set_state`), чтобы пользователь остался на текущем шаге.

## 4. Сериализация черновиков

Промежуточное состояние сохраняется в `storage/drafts/draft_<uuid>.json`
после каждого шага для возможности продолжения после перезапуска бота:

```python
import json
import uuid
from pathlib import Path

DRAFTS_DIR = Path("storage/drafts")
DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

async def save_draft(state: FSMContext):
    data = await state.get_data()
    draft_id = data.get("draft_id")
    if not draft_id:
        draft_id = str(uuid.uuid4())
        await state.update_data(draft_id=draft_id)

    draft_path = DRAFTS_DIR / f"draft_{draft_id}.json"
    draft_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return draft_id
```

### Формат draft JSON:
```json
{
  "draft_id": "a1b2c3d4-...",
  "contract_type": "supply",
  "current_state": "ContractWizard:vendor_inn",
  "contract_data": {
    "metadata": {"contract_number": "2025/П-01", "contract_date": "15.02.2025"},
    "client": {"inn": "7707083893", "full_name": "..."},
    "vendor": {"inn": "", "full_name": "..."},
    "...": "..."
  }
}
```

## 5. Инициализация визарда

Визард инициализируется эталонными данными из `ContractRegistry`:

```python
sample = ContractRegistry.get_sample_contract(contract_type)
await state.update_data(contract_data=sample.model_dump())
```

Это позволяет пользователю `/skip` любое поле — будет использовано значение по умолчанию.

## 6. Генерация документа (финальный шаг)

```python
contract = ContractRegistry.parse_contract(contract_type, contract_data)
docx_buf = DocxEngine.generate(contract)
pdf_bytes = TypstEngine.compile_pdf(contract)
```

## 7. Чек-лист при добавлении нового типа договора

- [ ] Создать Pydantic-модель в `core/models/<type>.py`
- [ ] Зарегистрировать в `core/templates/registry.py`
- [ ] Добавить States в `ContractWizard` (или создать отдельный StatesGroup)
- [ ] Хэндлеры: валидация на каждом шаге, `/skip` для optional
- [ ] Клавиатуры для enum-полей в `keyboards.py`
- [ ] Сериализация черновика через `save_draft()`
- [ ] Роутер зарегистрирован в `bot.py`

## Ссылки

- Эталонный паттерн: `references/wizard_pattern.md`
- Текущая реализация: `adapters/telegram_bot/handlers/wizard.py`
