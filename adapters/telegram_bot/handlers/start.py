"""Start, Help and Info Command Handlers for Telegram Bot."""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from adapters.telegram_bot.keyboards import (
    get_main_menu_keyboard,
    get_contract_types_inline_keyboard,
)
from core.templates.registry import ContractRegistry

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command."""
    await state.clear()
    welcome_text = (
        "👋 **Добро пожаловать в DocGen Omnichannel Platform!**\n\n"
        "🏛️ **Детерминированный генератор юридических договоров РФ** (Zero-LLM Runtime).\n\n"
        "✨ **Преимущества:**\n"
        "• 100% алгоритмическая точность без галлюцинаций\n"
        "• Валидация контрольных разрядов ИНН, ОГРН, БИК, расчетных счетов\n"
        "• Оформление Word по ГОСТ Р 7.0.97-2016\n"
        "• Автоматический расчет сумм, НДС и суммы прописью\n\n"
        "Выберите действие в меню ниже:"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu_keyboard(), parse_mode="Markdown")


@router.message(F.text == "📄 Создать договор")
@router.message(Command("new"))
async def cmd_new_contract(message: Message, state: FSMContext):
    """Start contract creation wizard."""
    await state.clear()
    await message.answer(
        "📋 **Выберите вид договора для генерации:**",
        reply_markup=get_contract_types_inline_keyboard(),
        parse_mode="Markdown"
    )


@router.message(F.text == "📋 Доступные договоры")
async def cmd_list_contracts(message: Message):
    """List supported contract types."""
    lines = ["📑 **Поддерживаемые типы договоров по законодательству РФ:**\n"]
    for t in ContractRegistry.list_types():
        lines.append(f"• **{t.title}** ({t.law_reference})\n  _{t.description}_\n")
    await message.answer("\n".join(lines), parse_mode="Markdown")


@router.message(F.text == "ℹ️ Помощь и ГОСТ")
@router.message(Command("help"))
async def cmd_help(message: Message):
    """Show help info."""
    help_text = (
        "💡 **Справка по платформе DocGen:**\n\n"
        "1. **Валидация реквизитов**: Система алгоритмически проверяет корректность ИНН юридических лиц (10 цифр) "
        "и ИП (12 цифр), а также связку БИК + Расчетный счет по контрольным коэффициентам ЦБ РФ.\n"
        "2. **Форматирование DOCX**: Документы формируются со строгим соблюдением ГОСТ: "
        "поля 25/15/20/20 мм, шрифт Liberation Serif, абзацный отступ 1.25 см, межстрочный 1.15, "
        "защита строк таблиц от разрывов (`cantSplit`) и повтор шапки (`tblHeader`).\n"
        "3. **Zero-LLM**: Текст договора собирается из выверенных правовых блоков ГК РФ."
    )
    await message.answer(help_text, parse_mode="Markdown")
