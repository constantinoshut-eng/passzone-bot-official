import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# --- Конфигурация ---
TOKEN = "7973091517:AAHBgg_Yn_E3VbNh3gDYwYuXKZekV25NRDU"
ADMIN_ID = 7585723570
VISA_CARD = "4175420010122027"
TRC20_ADDR = "TFXoVhmTC7E6M8R3rVycXaJvAMR84Vy9fY"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# --- Состояния ---
class Form(StatesGroup):
    awaiting_sizes = State()

# --- Клавиатуры ---
def make_start_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ℹ️ Ознакомиться с информацией", callback_data="to_details")]
    ])
    return kb


def kb_details_to_prep():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Мне подходит, хочу узнать о подготовке", callback_data="to_prep")]
    ])
    return kb

def kb_prep():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Указать размеры", callback_data="sizes")],
        [InlineKeyboardButton(text="➡️ Продолжить", callback_data="to_meet")]
    ])
    return kb

def kb_to_payment():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить — VISA", callback_data="pay_visa")],
        [InlineKeyboardButton(text="₿ Оплатить — USDT (TRC20)", callback_data="pay_trc20")]
    ])
    return kb

def kb_send_check():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Я оплатил(а), отправить чек", callback_data="i_sent_check")]
    ])
    return kb

# --- Хранилища временных данных ---
last_payment_method = {}
pending_payments = set()

# --- Handlers ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    text = (
        "👋 Добро пожаловать!\n\n"
        "Этот бот помогает организовать переход из страны А в страну Б.\n"
        "Мы поделимся с вами только фактами — без лишней воды. Всё основано на нашем реальном опыте.\n\n"
        "Вы сможете шаг за шагом узнать всю нужную информацию и подготовиться к переходу."
    )
    await message.answer(text, reply_markup=make_start_kb())

@dp.callback_query(F.data == "to_details")
async def cb_to_details(query: types.CallbackQuery):
    text = (
        "⛰ Наш опыт\n\n"
        "Мы лично прошли этот путь — не на словах, а на деле. 🌄\n"
        "Это был переход через горы: переменчивая погода, длинные подъёмы, холодные ночи и тёплые рассветы.\n"
        "Каждый участок маршрута мы проверили сами, чтобы убедиться, что он безопасен, скрыт от посторонних и надёжен.\n\n"
        "Мы не доверяем слухам — только реальный опыт и точная координация. "
        "Каждая точка маршрута, остановка и встреча спланированы заранее. "
        "Вы не окажетесь наугад — у вас будет чёткий, безопасный маршрут от старта до конца.\n\n"
        "✨ Основные моменты:\n\n"
        "🔹 Проверенный маршрут: Никаких случайных троп — только проверенные пути, по которым уже проходили люди.\n"
        "🔹 Безопасность: Мы ежедневно отслеживаем обстановку: погоду, маршруты и возможные риски.\n"
        "🔹 Комфорт: Вам не придётся нести тяжёлые сумки — всё подготовлено заранее, чтобы вы шли налегке.\n"
        "🔹 Поддержка: Вы не будете одни — опытный гид знает каждый поворот и будет рядом весь путь.\n"
        "🔹 Связь и контроль: Мы остаёмся с вами на связи на каждом этапе, чтобы вы чувствовали уверенность и спокойствие. 📡\n\n"
        "Каждая деталь маршрута продумана. Всё, что нужно от вас — следовать инструкциям и сохранять спокойствие."
    )
    await query.message.answer(text, reply_markup=kb_details_to_prep())


@dp.callback_query(F.data == "to_prep")
async def cb_to_prep(query: types.CallbackQuery):
    text = (
        "🛠 Подготовка\n\n"
        "Перед выездом мы берём на себя все организационные задачи.\n"
        "Вам не нужно беспокоиться о деталях — всё готовим мы.\n\n"
        "Что именно мы делаем для вас:\n\n"
        "📍 Маршрут\n"
        "- У нас уже есть готовый и проверенный маршрут.\n"
        "- Он полностью пройден и надёжен.\n"
        "- Мы учитываем погоду, патрули и возможные риски, чтобы переход был максимально безопасным.\n\n"
        "🎒 Снаряжение\n"
"- Вам не нужно ничего брать с собой.\n"
"- Всё необходимое будет ждать у гида.\n"
"- Мы формируем комплект индивидуально под каждого участника, с учётом размеров, времени года и условий маршрута.\n\n"
"В набор входит:\n"
"• Одежда для перехода — лёгкая, удобная, непромокаемая и подобранная по погоде.\n"
"• Обувь — устойчивая и комфортная, чтобы выдержать неровности рельефа.\n"
"• Маск-халат — лёгкий камуфляжный костюм, который помогает сливаться с окружающей средой и не привлекать внимание во время движения.\n"
"• Фонарь и запасные батареи — на случай перехода в сумерках или при слабой видимости.\n"
"• Продовольственный набор — лёгкая еда, перекусы и вода в индивидуальной упаковке.\n"
"• Аптечка первой необходимости — перевязочные материалы, антисептик, обезболивающее и всё, что может пригодиться в дороге.\n\n"
"Всё снаряжение подобрано так, чтобы не вызывать подозрений и при этом обеспечить максимальный комфорт и безопасность.\n"
"Вам остаётся только прибыть в назначенное место — всё остальное мы уже подготовили.\n\n"

        "📖 Инструкции\n"
        "- Вы получите пошаговый план: куда ехать, когда прибыть, как себя вести.\n\n"
        "⚠️ Важно: чего НЕ брать с собой — большие сумки, лишние документы, дорогие вещи."
    )
    await query.message.answer(text, reply_markup=kb_prep())

@dp.callback_query(F.data == "sizes")
async def cb_sizes(query: types.CallbackQuery, state: FSMContext):
    await query.message.answer(
        "👕 Напишите свои размеры:\n\n"
        "1️⃣ Верх (футболка/куртка)\n"
        "2️⃣ Низ (брюки)\n"
        "3️⃣ Обувь\n"
        "4️⃣ Особые пожелания"
    )
    await state.set_state(Form.awaiting_sizes)

@dp.message(Form.awaiting_sizes)
async def process_sizes(message: types.Message, state: FSMContext):
    await bot.send_message(ADMIN_ID, f"📥 Размеры от @{message.from_user.username}:\n{message.text}")
    await message.answer("✅ Размеры получены. Спасибо! Для продолжения нажмите на кнопку Продолжить")
    await state.clear()

# Callback: next -> meeting
@dp.callback_query(lambda c: c.data == "to_meet")
async def cb_to_meet(query: types.CallbackQuery):
    await query.answer()
    text = (
        "🤝 Встреча с гидом\n\n"
        "В точке перехода вас встретит наш гид — человек, который отлично знает маршрут и все его особенности.\n"
        "Он заранее будет проинформирован о вашем прибытии и подготовит всё необходимое к встрече.\n\n"
        "🔹 Что происходит при встрече:\n"
        "- Гид передаёт вам полный комплект снаряжения, заранее подобранный под ваши размеры и погодные условия.\n"
        "- Объясняет последние детали маршрута, особенности рельефа и даёт рекомендации по темпу движения.\n"
        "- Проверяет, чтобы вы чувствовали себя уверенно и спокойно перед началом перехода.\n\n"
        "🔹 Как проходит переход:\n"
        "После инструктажа вы вместе начинаете движение по заранее проверенному и безопасному маршруту.\n"
        "Путь спланирован так, чтобы минимизировать вероятность встречи с посторонними и обеспечить вам максимальную безопасность.\n\n"
        "🔹 Поддержка на всём пути:\n"
        "Гид сопровождает вас до самой конечной точки, помогает ориентироваться, контролирует темп и следит за вашим состоянием.\n"
        "В случае непредвиденных ситуаций он знает, как действовать, и всегда имеет резервный план.\n\n"
        "🧭 К точке сбора вы прибываете налегке, без излишнего груза и риска привлечь внимание.\n"
        "Всё необходимое уже находится у гида, а наша команда отслеживает обстановку и погоду по маршруту, чтобы вы могли просто двигаться вперёд спокойно и уверенно."
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Перейти к оплате", callback_data="to_payment")]
    ])
    await bot.send_message(query.from_user.id, text, reply_markup=kb)

# === Блок ОПЛАТА ===

@dp.callback_query(F.data == "to_payment")
async def cb_to_payment(query: types.CallbackQuery):
    await query.message.answer(
        "💰 Оплата\n\n"
        "Полная стоимость всей процедуры составляет 5000$.\n\n"
        "Оплата делится на два этапа:\n"
        "• Первый взнос — 2500$: до начала подготовки (мы сразу начинаем проверку маршрута, подготовку снаряжения и организацию встречи с гидом);\n"
        "• Второй взнос — 2500$: при встрече с гидом в точке отправления.\n\n"
        "Так вы оплачиваете только за реальный результат — всё прозрачно и поэтапно.\n\n"
        "После первого взноса начинается подготовительный этап (20–30 дней):\n"
        "мы проверяем маршрут, подбираем снаряжение и готовим всё необходимое.\n\n"
        "Выберите удобный способ оплаты 👇",
        reply_markup=kb_to_payment()
    )

@dp.callback_query(F.data == "pay_visa")
async def cb_pay_visa(query: types.CallbackQuery):
    last_payment_method[query.from_user.id] = "VISA"
    await query.message.answer(
        f"💳 Реквизиты для оплаты (VISA)\n\n"
        f"Номер карты: {VISA_CARD}\n"
       
        "После перевода нажмите кнопку ниже и прикрепите фото/скриншот чека 👇",
        reply_markup=kb_send_check()
    )

@dp.callback_query(F.data == "pay_trc20")
async def cb_pay_trc20(query: types.CallbackQuery):
    last_payment_method[query.from_user.id] = "TRC20"
    await query.message.answer(
        f"₿ **Оплата в USDT (TRC20)**\n\n"
        f"**Адрес кошелька:**\n`{TRC20_ADDR}`\n\n"
        "⚠️ *ВНИМАНИЕ!* Копируйте адрес внимательно — без пробелов и не пропуская символов.\n\n"
        "После перевода нажмите кнопку ниже и прикрепите фото или скриншот транзакции 👇",
        reply_markup=kb_send_check(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "i_sent_check")
async def i_sent_check(query: types.CallbackQuery):
    await query.message.answer(
        "📤 Прикрепите фото или скриншот платежа прямо сюда в чат.\n"
        "Как только вы это сделаете, чек автоматически уйдёт на проверку администратору."
    )

@dp.message(lambda message: message.photo or message.document)
async def handle_check(message: types.Message):
    user_id = message.from_user.id
    method = last_payment_method.get(user_id, "Не указан")

    # Определяем ID файла
    file_id = None
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        file_id = message.document.file_id

    if not file_id:
        await message.answer("❌ Ошибка: не удалось получить файл.")
        return

    # Кнопки для подтверждения/отклонения
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить оплату", callback_data=f"confirm:{user_id}")],
        [InlineKeyboardButton(text="❌ Отклонить оплату", callback_data=f"reject:{user_id}")]
    ])

    # Отправляем админу чек с кнопками
    caption = (
        f"📥 Новый чек на проверку\n\n"
        f"👤 Пользователь ID: {user_id}\n"
        f"💳 Метод оплаты: {method}\n\n"
        "Выберите действие ниже 👇"
    )

    try:
        if message.photo:
            await bot.send_photo(ADMIN_ID, photo=file_id, caption=caption, reply_markup=kb)
        else:
            await bot.send_document(ADMIN_ID, document=file_id, caption=caption, reply_markup=kb)
    except Exception as e:
        await message.answer(f"⚠️ Ошибка при отправке админу: {e}")
        return

    # Подтверждение пользователю
    await message.answer(
        "✅ Чек получен и отправлен на проверку.\n"
        "Проверка занимает до 30 минут. Ожидайте уведомления."
    )

@dp.callback_query(F.data.startswith("confirm:"))
async def confirm_payment(query: types.CallbackQuery):
    if query.from_user.id != ADMIN_ID:
        await query.answer("Вы не авторизованы.", show_alert=True)
        return

    uid = int(query.data.split(":")[1])
    await bot.send_message(
        uid,
        "✅ Оплата успешно подтверждена!\n\n"
        "Мы приступили к подготовительным работам:\n"
        "- Проверяем маршрут и актуальную обстановку.\n"
        "- Подбираем комплект вашего индивидуального снаряжения.\n"
        "- Координируем место и время встречи с гидом.\n\n"
        "🕒 Подготовка займёт от 20 до 30 дней.\n\n"
        "💪 Используйте это время для лёгкой физической подготовки — прогулки, растяжка, дыхательные упражнения.\n\n"
        "📩 После завершения подготовки вы получите уведомление с точной датой и временем выезда."
    )

    await query.answer("Подтверждение отправлено пользователю.", show_alert=True)
    await bot.send_message(ADMIN_ID, f"✅ Оплата пользователя {uid} подтверждена.")

@dp.callback_query(F.data.startswith("reject:"))
async def reject_payment(query: types.CallbackQuery):
    if query.from_user.id != ADMIN_ID:
        await query.answer("Вы не авторизованы.", show_alert=True)
        return

    uid = int(query.data.split(":")[1])
    await bot.send_message(
        uid,
        "❌ Оплата не подтверждена.\n\n"
        "Проверьте правильность перевода и отправьте чек повторно.\n"
        "Если вопрос не решён — свяжитесь с поддержкой."
    )

    await query.answer("Отказ отправлен пользователю.", show_alert=True)
    await bot.send_message(ADMIN_ID, f"❌ Оплата пользователя {uid} отклонена.")
# --- Запуск ---
async def main():
    print("Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
