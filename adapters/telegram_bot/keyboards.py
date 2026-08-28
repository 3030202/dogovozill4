"""Inline and Reply Keyboards for Telegram Bot."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from core.templates.registry import ContractRegistry


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Main persistent reply keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📄 Создать договор"), KeyboardButton(text="🚀 Быстрый пример")],
            [KeyboardButton(text="ℹ️ Помощь и ГОСТ"), KeyboardButton(text="📋 Доступные договоры")],
        ],
        resize_keyboard=True,
    )


def get_contract_types_inline_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard for selecting contract type."""
    buttons = []
    for info in ContractRegistry.list_types():
        buttons.append([
            InlineKeyboardButton(
                text=f"{info.title} ({info.law_reference})",
                callback_data=f"type:{info.key}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_party_type_keyboard(party_role: str) -> InlineKeyboardMarkup:
    """Party legal form selection."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="ООО (Юр. лицо)", callback_data=f"{party_role}_type:OOO"),
                InlineKeyboardButton(text="ИП", callback_data=f"{party_role}_type:IP"),
            ],
            [
                InlineKeyboardButton(text="Самозанятый (НПД)", callback_data=f"{party_role}_type:SELF_EMPLOYED"),
                InlineKeyboardButton(text="Физ. лицо", callback_data=f"{party_role}_type:INDIVIDUAL"),
            ]
        ]
    )


def get_vat_keyboard() -> InlineKeyboardMarkup:
    """VAT rate selector."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="НДС 20% (включен)", callback_data="vat:20_incl"),
                InlineKeyboardButton(text="НДС 10%", callback_data="vat:10_incl"),
            ],
            [
                InlineKeyboardButton(text="Без НДС (УСН)", callback_data="vat:exempt"),
            ]
        ]
    )


def get_payment_terms_keyboard() -> InlineKeyboardMarkup:
    """Payment schedule selector."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="100% Предоплата", callback_data="pay:100_PREPAYMENT")],
            [InlineKeyboardButton(text="50% Аванс / 50% Постоплата", callback_data="pay:50_50")],
            [InlineKeyboardButton(text="100% Постоплата (5 раб. дней)", callback_data="pay:100_POSTPAYMENT")],
        ]
    )


def get_download_format_keyboard(draft_id: str) -> InlineKeyboardMarkup:
    """Final document download selector."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📥 Скачать DOCX (ГОСТ)", callback_data=f"gen:docx:{draft_id}"),
                InlineKeyboardButton(text="📄 Скачать PDF (Вектор)", callback_data=f"gen:pdf:{draft_id}"),
            ],
            [
                InlineKeyboardButton(text="📦 Скачать оба формата (ZIP/Doc)", callback_data=f"gen:both:{draft_id}"),
            ]
        ]
    )
