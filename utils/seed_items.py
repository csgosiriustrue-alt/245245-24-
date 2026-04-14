"""Сид предметов — все цены после дефляции x10."""
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Item, RarityEnum

logger = logging.getLogger(__name__)

# ============================================================================
# ГОЛОВАСТИКИ
# ============================================================================

TADPOLE_ITEMS = [
    # ── ЛЕГЕНДЫ (0.35%) ──
    ("Гены Павла Дурова",            "🧬", 60_000, 0.18, RarityEnum.LEGENDARY),
    ("Гены Президента",              "🧬", 13_500, 0.17, RarityEnum.LEGENDARY),

    # ── ТОП-ТИР (9.65%) ──
    ("Гены Криминального Авторитета", "🧬",  6_000, 2.50, RarityEnum.EPIC),
    ("Гены Программиста",            "🧬",  3_000, 2.50, RarityEnum.EPIC),
    ("Гены Бизнесмена",              "🧬",  1_800, 2.40, RarityEnum.EPIC),
    ("Гены Меллстроя",               "🧬",  5_000, 2.25, RarityEnum.EPIC),

    # ── МИД-ТИР (25.0%) ──
    ("Гены Артиста",                 "🧬",  1_250, 3.50, RarityEnum.RARE),
    ("Гены Саши Ноткоин",           "🧬",    800, 3.50, RarityEnum.RARE),
    ("Гены Инфоцигана",             "🧬",    500, 3.25, RarityEnum.RARE),
    ("Гены Онлифанщицы",            "🧬",    500, 3.25, RarityEnum.RARE),
    ("Гены Скамера",                "🧬",    350, 3.00, RarityEnum.COMMON),
    ("Гены Альтушки",               "🧬",    350, 3.00, RarityEnum.COMMON),
    ("Гены Лудомана",               "🧬",    250, 2.75, RarityEnum.COMMON),
    ("Гены Инцела",                 "🧬",    250, 2.75, RarityEnum.COMMON),

    # ── ЛОУ-ТИР (65.0%) ──
    ("Гены Холдера TON",            "🧬",    200, 5.50, RarityEnum.COMMON),
    ("Гены Холдера Подарков",       "🧬",    200, 5.50, RarityEnum.COMMON),
    ("Гены Холдера Стикеров",       "🧬",    150, 5.00, RarityEnum.COMMON),
    ("Гены Холдера NFT",            "🧬",    150, 5.00, RarityEnum.COMMON),
    ("Гены Доставщика",             "🧬",    150, 5.00, RarityEnum.COMMON),
    ("Гены Ивана Золо",             "🧬",     80, 5.00, RarityEnum.COMMON),
    ("Гены Фурри",                  "🧬",     75, 5.00, RarityEnum.COMMON),
    ("Гены Фитоняши",              "🧬",     75, 4.50, RarityEnum.COMMON),
    ("Гены Тиктокера",             "🧬",     75, 4.50, RarityEnum.COMMON),
    ("Гены Карлика",                "🧬",    100, 5.00, RarityEnum.COMMON),
    ("Гены Результата инцеста",     "🧬",     70, 4.00, RarityEnum.COMMON),
    ("Воздухан",                    "💨",     55, 4.00, RarityEnum.COMMON),
    ("Урод",                        "🤮",     35, 4.00, RarityEnum.COMMON),
    ("Нищета",                      "🪣",     25, 3.50, RarityEnum.COMMON),
    ("Пустышка",                    "❌",     10, 3.50, RarityEnum.COMMON),
]

# ── Стетоскоп и Рентген УДАЛЕНЫ из TOOL_ITEMS ──
TOOL_ITEMS = [
    # name, emoji, price, price_stars, rarity, max_inv, monthly_limit, desc
    ("Ржавый Сейф",      "🧰",  5_000, 10,  RarityEnum.RARE,      1, 1,  "Спрячь 1 предмет или 100К монет."),
    ("Элитный Сейф",     "🏦", 20_000, 35, RarityEnum.LEGENDARY, 1, 1,  "Спрячь 3 предмета или 700К монет."),
    ("Охрана",           "💂",  0, 15,  RarityEnum.RARE,      15, 5,  "Блокирует ограбление на 6ч."),
    ("Крыша",            "🕴",  2_500, 25,  RarityEnum.EPIC,      3, 5,  "Блокирует + 15% залог грабителя. 8ч."),
    ("Отмычка",          "🗝",    0, 1,   RarityEnum.COMMON,   30, 0,  "+1 попытка ввода кода сейфа."),
    ("Лом",              "🔨",  1_200, 12,  RarityEnum.RARE,      10, 0,  "70% шанс вскрыть Ржавый сейф."),
    ("Адвокат",          "💼",  0, 1,  RarityEnum.RARE,      30, 0,  "Мгновенно из тюрьмы."),
    ("Липкие Перчатки",  "🧤",  1_000, 7,   RarityEnum.COMMON,   10, 0,  "x1.25 к шансу ограбления."),
    ("Durov's Figure",   "🗿",100_000,1000, RarityEnum.LEGENDARY, 1, 0,  "Коллекционная фигурка Дурова. Бесценна."),
    ("Вышибала",         "👊",  5_000, 10,  RarityEnum.EPIC,      3, 0,  "Одноразовый. Игнорирует охрану жертвы при ограблении."),
]

BOOST_ITEMS = [
    ("Журнал для взрослых", "🔞", 1_500, 3,  RarityEnum.RARE,      5, 5,
     "КД теребления: 4ч → 2ч на 24 часа."),
    ("Резиновая кукла",     "🫦", 2_500, 5,  RarityEnum.EPIC,      3, 3,
     "Шанс топ-тир + легенд x2 на 24ч."),
    ("Путана",              "💋", 5_069, 20, RarityEnum.LEGENDARY,  2, 2,
     "Шанс топ-тир + легенд x5 на 24ч."),
]

CHARGE_ITEM = ("Заряд теребления", "⚡", 1_000, 3, RarityEnum.COMMON, 6, 15,
    "+1 заряд теребления. Макс 6.")

# Предметы для деактивации (удалённые из магазина)
DEPRECATED_ITEMS = {"Рентген", "Стетоскоп"}


async def seed_items(session: AsyncSession) -> None:
    existing_r = await session.execute(select(Item.name))
    existing_names = {row[0] for row in existing_r.all()}
    added = 0

    for name, emoji, price, drop_chance, rarity in TADPOLE_ITEMS:
        if name not in existing_names:
            session.add(Item(name=name, emoji=emoji, price=price, price_stars=0,
                drop_chance=drop_chance, rarity=rarity, is_starter=False,
                max_in_inventory=0, monthly_coin_limit=0,
                description=f"Генетический материал: {name}"))
            added += 1
        else:
            item_r = await session.execute(
                select(Item).where(Item.name == name).limit(1))
            item = item_r.scalars().first()
            if item:
                item.drop_chance = drop_chance
                item.price = price

    for name, emoji, price, price_stars, rarity, max_inv, monthly_limit, desc in TOOL_ITEMS:
        if name not in existing_names:
            session.add(Item(name=name, emoji=emoji, price=price, price_stars=price_stars,
                drop_chance=0, rarity=rarity, is_starter=False,
                max_in_inventory=max_inv, monthly_coin_limit=monthly_limit, description=desc))
            added += 1
        else:
            item_r = await session.execute(
                select(Item).where(Item.name == name).limit(1))
            item = item_r.scalars().first()
            if item:
                item.price = price
                item.price_stars = price_stars
                item.description = desc

    for name, emoji, price, price_stars, rarity, max_inv, monthly_limit, desc in BOOST_ITEMS:
        if name not in existing_names:
            session.add(Item(name=name, emoji=emoji, price=price, price_stars=price_stars,
                drop_chance=0, rarity=rarity, is_starter=False,
                max_in_inventory=max_inv, monthly_coin_limit=monthly_limit, description=desc))
            added += 1
        else:
            item_r = await session.execute(
                select(Item).where(Item.name == name).limit(1))
            item = item_r.scalars().first()
            if item:
                item.price = price
                item.price_stars = price_stars

    cn, ce, cp, cs, cr, cmi, cml, cd = CHARGE_ITEM
    if cn not in existing_names:
        session.add(Item(name=cn, emoji=ce, price=cp, price_stars=cs,
            drop_chance=0, rarity=cr, is_starter=False,
            max_in_inventory=cmi, monthly_coin_limit=cml, description=cd))
        added += 1
    else:
        item_r = await session.execute(
            select(Item).where(Item.name == cn).limit(1))
        item = item_r.scalars().first()
        if item:
            item.price = cp
            item.price_stars = cs

    if added > 0:
        await session.flush()
        logger.info(f"🧬 Добавлено {added} предметов")
    else:
        logger.info("🧬 Все предметы уже в БД (цены обновлены)")

    # Деактивируем удалённые предметы
    for dep_name in DEPRECATED_ITEMS:
        dep_r = await session.execute(
            select(Item).where(Item.name == dep_name).limit(1))
        dep = dep_r.scalars().first()
        if dep:
            dep.drop_chance = 0
            dep.price = 0
            dep.price_stars = 0
            dep.max_in_inventory = 0
            logger.info(f"🗑 Деактивирован: {dep_name}")

    tadpole_names = {t[0] for t in TADPOLE_ITEMS}
    old_r = await session.execute(select(Item).where(Item.drop_chance > 0))
    disabled = 0
    for item in old_r.scalars().all():
        if item.name not in tadpole_names:
            item.drop_chance = 0
            disabled += 1
    if disabled > 0:
        logger.info(f"🧬 Отключено {disabled} старых")

    # ── Удаляем дубликаты по имени (оставляем только первый) ──
    all_items_r = await session.execute(select(Item).order_by(Item.id.asc()))
    all_items = all_items_r.scalars().all()
    seen_names: dict[str, int] = {}
    dupes_removed = 0
    for item in all_items:
        if item.name in seen_names:
            await session.delete(item)
            dupes_removed += 1
        else:
            seen_names[item.name] = item.id
    if dupes_removed > 0:
        await session.flush()
        logger.info(f"🗑 Удалено {dupes_removed} дубликатов предметов")
