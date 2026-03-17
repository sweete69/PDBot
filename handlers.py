from __future__ import annotations

import io
import time
from typing import Optional, Tuple

from aiogram import Bot, Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.enums import ChatAction

from config import Settings
from gemini_service import GeminiService, ContentPolicyError, GeminiServiceError
from keyboards import (
    main_menu_kb,
    banner_kb,
    desc_menu_kb,
    buy_points_kb,
    back_to_menu_kb,
    desc_result_kb,
    banner_result_kb,
    CB_MENU_MAIN,
    CB_MENU_BANNER,
    CB_MENU_DESC,
    CB_MENU_BUY,
    CB_MENU_POLICY,
    CB_DESC_BY_PHOTO,
    CB_DESC_BY_TEXT,
    CB_BUY_PREFIX,
    CB_DESC_REGEN,
    CB_DESC_BACK,
    CB_BANNER_REGEN,
    CB_BANNER_BACK,
)
from states import BannerFlow, DescByTextFlow, DescByPhotoFlow, DescResultFlow, BannerResultFlow

router = Router()

POLICY_TEXT = (
    "📄 Политика сервиса\n\n"
    "1) Бот предназначен для генерации описаний и рекламных баннеров товаров.\n"
    "2) Не отправляйте персональные данные и запрещённый контент.\n"
    "3) Тексты и изображения используются только для формирования ответа.\n"
)

DESC_STYLES = [
    "дружелюбный, живой",
    "премиальный, лаконичный",
    "деловой, уверенный",
    "мягкий, заботливый",
]

MIN_REGEN_INTERVAL_S = 2.0


# ---------------- Helpers ----------------

async def _download_photo_bytes(bot: Bot, photo_file_id: str) -> bytes:
    file = await bot.get_file(photo_file_id)
    buf = io.BytesIO()
    await bot.download_file(file.file_path, destination=buf)
    return buf.getvalue()


async def _safe_delete_message(message: Message) -> None:
    try:
        await message.delete()
    except Exception:
        pass


async def _safe_delete_message_by_id(bot: Bot, chat_id: int, message_id: int) -> None:
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass


async def _set_ui_message(state: FSMContext, message_id: int) -> None:
    await state.update_data(ui_message_id=message_id)


async def _get_ui_message_id(state: FSMContext) -> Optional[int]:
    data = await state.get_data()
    return data.get("ui_message_id")


async def _edit_ui_text(
    state: FSMContext,
    bot: Bot,
    chat_id: int,
    text: str,
    reply_markup=None,
) -> None:
    ui_id = await _get_ui_message_id(state)
    if ui_id:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=ui_id,
                text=text,
                reply_markup=reply_markup,
            )
        except Exception:
            # если не смогли отредактировать (сообщение удалили/устарело) — просто молчим
            pass


async def _show_main_menu(message_or_query, state: FSMContext) -> None:
    text = "👋 Привет! Выбери действие в меню:"
    if isinstance(message_or_query, Message):
        msg = await message_or_query.answer(text, reply_markup=main_menu_kb())
        await _set_ui_message(state, msg.message_id)
    else:
        await message_or_query.message.edit_text(text, reply_markup=main_menu_kb())
        await _set_ui_message(state, message_or_query.message.message_id)


async def _show_desc_choice(query: CallbackQuery, state: FSMContext) -> None:
    """Возврат к выбору способа генерации описания."""
    await query.message.edit_text(
        "📝 Создание описания товара\n\nВыбери способ:",
        reply_markup=desc_menu_kb(),
    )
    await _set_ui_message(state, query.message.message_id)


def _rate_limit_ok(data: dict, *, key: str, min_interval_s: float) -> bool:
    now = time.time()
    last = float(data.get(key, 0.0) or 0.0)
    return (now - last) >= min_interval_s


def _pick_style(idx: int) -> str:
    return DESC_STYLES[idx % len(DESC_STYLES)]


def _make_desc_message(text: str) -> str:
    return (text or "").strip()


async def _generate_desc(
    *,
    ai: GeminiService,
    settings: Settings,
    product_text: Optional[str],
    image_bytes: Optional[bytes],
    style_index: int,
) -> str:
    style_hint = _pick_style(style_index)
    temperature = 0.82 + (0.04 * (style_index % 3))

    # ✅ Совместимость со старым gemini_service.py:
    # если он не принимает temperature/style_hint — вызываем без них
    try:
        return ai.generate_product_description(
            product_text=product_text,
            image_bytes=image_bytes,
            max_chars=settings.max_output_chars,
            temperature=min(0.98, temperature),
            style_hint=style_hint,
        )
    except TypeError:
        return ai.generate_product_description(
            product_text=product_text,
            image_bytes=image_bytes,
            max_chars=settings.max_output_chars,
        )


# ---------------- Start / Menu ----------------

@router.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext) -> None:
    await state.clear()
    await _show_main_menu(message, state)


@router.callback_query(F.data == CB_MENU_MAIN)
async def cb_main_menu(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await query.answer()
    await _show_main_menu(query, state)


@router.callback_query(F.data == CB_MENU_BANNER)
async def cb_banner(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await query.answer()
    await query.message.edit_text(
        "🖼 Создание баннера\n\n"
        "Пришли название/описание товара ИЛИ фото товара.\n"
        "Фото можно без подписи — но подпись помогает точнее.",
        reply_markup=banner_kb(),
    )
    await _set_ui_message(state, query.message.message_id)
    await state.set_state(BannerFlow.waiting_input)


@router.callback_query(F.data == CB_MENU_DESC)
async def cb_desc(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await query.answer()
    await _show_desc_choice(query, state)


@router.callback_query(F.data == CB_MENU_BUY)
async def cb_buy_points(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await query.answer()
    await query.message.edit_text(
        "⭐ Покупка поинтов\n\nВыбери количество:",
        reply_markup=buy_points_kb(),
    )
    await _set_ui_message(state, query.message.message_id)


@router.callback_query(F.data.startswith(CB_BUY_PREFIX))
async def cb_buy_amount(query: CallbackQuery, state: FSMContext) -> None:
    await query.answer("Покупка поинтов пока не реализована 🙌", show_alert=True)


@router.callback_query(F.data == CB_MENU_POLICY)
async def cb_policy(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await query.answer()
    await query.message.edit_text(POLICY_TEXT, reply_markup=back_to_menu_kb())
    await _set_ui_message(state, query.message.message_id)


# ---------------- Description flows ----------------

@router.callback_query(F.data == CB_DESC_BY_TEXT)
async def cb_desc_by_text(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await query.answer()
    await query.message.edit_text(
        "✏️ Описание по тексту\n\n"
        "Пришли название товара одним сообщением.\n"
        "Я удалю твоё сообщение и пришлю готовое описание 👇",
        reply_markup=back_to_menu_kb(),
    )
    await _set_ui_message(state, query.message.message_id)
    await state.set_state(DescByTextFlow.waiting_text)


@router.callback_query(F.data == CB_DESC_BY_PHOTO)
async def cb_desc_by_photo(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await query.answer()
    await query.message.edit_text(
        "📸 Описание по фото\n\n"
        "Загрузи фото товара (подпись необязательна).\n"
        "Я удалю твоё сообщение и пришлю описание 👇",
        reply_markup=back_to_menu_kb(),
    )
    await _set_ui_message(state, query.message.message_id)
    await state.set_state(DescByPhotoFlow.waiting_photo)


@router.message(DescByTextFlow.waiting_text)
async def desc_by_text(
    message: Message,
    state: FSMContext,
    bot: Bot,
    settings: Settings,
    ai: GeminiService,
) -> None:
    user_text = (message.text or "").strip()
    if not user_text:
        await message.answer("Пришли название товара текстом 🙂", reply_markup=back_to_menu_kb())
        return

    await _safe_delete_message(message)
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    await _edit_ui_text(state, bot, message.chat.id, "⏳ Генерирую описание…", reply_markup=None)

    style_index = 0
    try:
        result = await _generate_desc(
            ai=ai,
            settings=settings,
            product_text=user_text,
            image_bytes=None,
            style_index=style_index,
        )
        result = _make_desc_message(result)
        if not result:
            raise RuntimeError("Empty result")
    except ContentPolicyError as e:
        result = f"⚠️ {e}"
    except GeminiServiceError:
        result = "❌ Ошибка Gemini API. Проверь ключ/модель/биллинг и попробуй ещё раз."
    except Exception:
        # ✅ теперь это реально “кодовая” ошибка/пустой результат, а не несовпадение сигнатуры
        result = "❌ Не удалось сгенерировать описание. Попробуй ещё раз."

    sent = await bot.send_message(
        chat_id=message.chat.id,
        text=result,
        reply_markup=desc_result_kb(),
    )

    await state.clear()
    await state.set_state(DescResultFlow.viewing)
    await state.update_data(
        last_desc_text=user_text,
        last_desc_image=None,
        last_desc_msg_id=sent.message_id,
        last_style_index=style_index,
        last_regen_ts=time.time(),
    )


@router.message(DescByPhotoFlow.waiting_photo)
async def desc_by_photo(
    message: Message,
    state: FSMContext,
    bot: Bot,
    settings: Settings,
    ai: GeminiService,
) -> None:
    if not message.photo:
        await message.answer("Пришли фото товара 📸", reply_markup=back_to_menu_kb())
        return

    caption = (message.caption or "").strip() or None
    photo_id = message.photo[-1].file_id

    img = await _download_photo_bytes(bot, photo_id)
    await _safe_delete_message(message)

    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    await _edit_ui_text(state, bot, message.chat.id, "⏳ Анализирую фото и пишу описание…", reply_markup=None)

    style_index = 0
    try:
        result = await _generate_desc(
            ai=ai,
            settings=settings,
            product_text=caption,
            image_bytes=img,
            style_index=style_index,
        )
        result = _make_desc_message(result)
        if not result:
            raise RuntimeError("Empty result")
    except ContentPolicyError as e:
        result = f"⚠️ {e}"
    except GeminiServiceError:
        result = "❌ Ошибка Gemini API. Проверь ключ/модель/биллинг и попробуй ещё раз."
    except Exception:
        result = "❌ Не удалось сгенерировать описание. Попробуй ещё раз."

    sent = await bot.send_message(
        chat_id=message.chat.id,
        text=result,
        reply_markup=desc_result_kb(),
    )

    await state.clear()
    await state.set_state(DescResultFlow.viewing)
    await state.update_data(
        last_desc_text=caption,
        last_desc_image=img,
        last_desc_msg_id=sent.message_id,
        last_style_index=style_index,
        last_regen_ts=time.time(),
    )


@router.callback_query(DescResultFlow.viewing, F.data == CB_DESC_REGEN)
async def cb_desc_regen(
    query: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    settings: Settings,
    ai: GeminiService,
) -> None:
    data = await state.get_data()

    if not _rate_limit_ok(data, key="last_regen_ts", min_interval_s=MIN_REGEN_INTERVAL_S):
        await query.answer("Подожди секунду 🙂", show_alert=False)
        return

    await query.answer("🔁 Генерирую новый вариант…", show_alert=False)
    await bot.send_chat_action(chat_id=query.message.chat.id, action=ChatAction.TYPING)

    last_text = data.get("last_desc_text")
    last_img = data.get("last_desc_image")
    msg_id = int(data.get("last_desc_msg_id") or query.message.message_id)
    style_index = int(data.get("last_style_index") or 0) + 1

    try:
        await bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=msg_id,
            text="⏳ Генерирую новый вариант описания…",
            reply_markup=None,
        )
    except Exception:
        pass

    try:
        new_text = await _generate_desc(
            ai=ai,
            settings=settings,
            product_text=last_text,
            image_bytes=last_img,
            style_index=style_index,
        )
        new_text = _make_desc_message(new_text)
        if not new_text:
            raise RuntimeError("Empty result")
    except ContentPolicyError as e:
        new_text = f"⚠️ {e}"
    except GeminiServiceError:
        new_text = "❌ Ошибка Gemini API. Проверь ключ/модель/биллинг и попробуй ещё раз."
    except Exception:
        new_text = "❌ Не удалось сгенерировать. Попробуй ещё раз."

    await bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=msg_id,
        text=new_text,
        reply_markup=desc_result_kb(),
    )

    await state.update_data(
        last_style_index=style_index,
        last_regen_ts=time.time(),
    )


@router.callback_query(DescResultFlow.viewing, F.data == CB_DESC_BACK)
async def cb_desc_back(query: CallbackQuery, state: FSMContext) -> None:
    await query.answer()
    await _safe_delete_message_by_id(query.bot, query.message.chat.id, query.message.message_id)

    await state.clear()
    # ✅ назад теперь ведёт к выбору способа генерации описания
    await _show_desc_choice(query, state)


# ---------------- Banner flow ----------------

@router.message(BannerFlow.waiting_input)
async def banner_waiting_input(
    message: Message,
    state: FSMContext,
    bot: Bot,
    settings: Settings,
    ai: GeminiService,
) -> None:
    prompt_text = (message.caption or message.text or "").strip() or None
    image_bytes = None

    if message.photo:
        image_bytes = await _download_photo_bytes(bot, message.photo[-1].file_id)

    if not prompt_text and not image_bytes:
        await message.answer("Пришли название/описание или фото товара 🙂", reply_markup=banner_kb())
        return

    await _safe_delete_message(message)

    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_PHOTO)
    await _edit_ui_text(state, bot, message.chat.id, "⏳ Генерирую баннер…", reply_markup=None)

    try:
        banner_png, copy = ai.generate_banner(product_text=prompt_text, image_bytes=image_bytes)
        await bot.send_photo(chat_id=message.chat.id, photo=banner_png, caption="✅ Баннер готов")

        sent = await bot.send_message(
            chat_id=message.chat.id,
            text=(copy or "").strip(),
            reply_markup=banner_result_kb(),
        )

        await state.clear()
        await state.set_state(BannerResultFlow.viewing)
        await state.update_data(
            last_banner_text=prompt_text,
            last_banner_image=image_bytes,
            last_banner_msg_id=sent.message_id,
            last_regen_ts=time.time(),
        )
    except ContentPolicyError as e:
        await bot.send_message(chat_id=message.chat.id, text=f"⚠️ {e}", reply_markup=back_to_menu_kb())
        await state.clear()
    except GeminiServiceError:
        await bot.send_message(
            chat_id=message.chat.id,
            text="❌ Ошибка Gemini API. Проверь ключ/модель/биллинг и попробуй ещё раз.",
            reply_markup=back_to_menu_kb(),
        )
        await state.clear()
    except Exception:
        await bot.send_message(
            chat_id=message.chat.id,
            text="❌ Не удалось сгенерировать баннер. Попробуй ещё раз.",
            reply_markup=back_to_menu_kb(),
        )
        await state.clear()


@router.callback_query(BannerResultFlow.viewing, F.data == CB_BANNER_REGEN)
async def cb_banner_regen(
    query: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    ai: GeminiService,
) -> None:
    data = await state.get_data()
    if not _rate_limit_ok(data, key="last_regen_ts", min_interval_s=MIN_REGEN_INTERVAL_S):
        await query.answer("Подожди секунду 🙂", show_alert=False)
        return

    await query.answer("🔁 Генерирую новый баннер…", show_alert=False)
    await bot.send_chat_action(chat_id=query.message.chat.id, action=ChatAction.UPLOAD_PHOTO)

    prompt_text = data.get("last_banner_text")
    image_bytes = data.get("last_banner_image")
    msg_id = int(data.get("last_banner_msg_id") or query.message.message_id)

    await bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=msg_id,
        text="⏳ Генерирую новый вариант…",
        reply_markup=None,
    )

    try:
        banner_png, copy = ai.generate_banner(product_text=prompt_text, image_bytes=image_bytes)
        await bot.send_photo(chat_id=query.message.chat.id, photo=banner_png, caption="✅ Новый баннер готов")
        await bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=msg_id,
            text=(copy or "").strip(),
            reply_markup=banner_result_kb(),
        )
        await state.update_data(last_regen_ts=time.time())
    except ContentPolicyError as e:
        await bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=msg_id,
            text=f"⚠️ {e}",
            reply_markup=banner_result_kb(),
        )
        await state.update_data(last_regen_ts=time.time())
    except Exception:
        await bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=msg_id,
            text="❌ Не удалось сгенерировать новый баннер. Попробуй ещё раз.",
            reply_markup=banner_result_kb(),
        )
        await state.update_data(last_regen_ts=time.time())


@router.callback_query(BannerResultFlow.viewing, F.data == CB_BANNER_BACK)
async def cb_banner_back(query: CallbackQuery, state: FSMContext) -> None:
    await query.answer()
    await _safe_delete_message_by_id(query.bot, query.message.chat.id, query.message.message_id)
    await state.clear()
    await _show_main_menu(query, state)