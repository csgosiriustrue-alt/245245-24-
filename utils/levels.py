"""Система уровней игрока."""
import logging

logger = logging.getLogger(__name__)

MAX_LEVEL = 80
BASE_THRESHOLD = 100_000
SCALING_FACTOR = 1.25
MIN_TRANSFER_LEVEL = 5

# Кэш порогов чтобы не считать каждый раз
_xp_cache: dict[int, int] = {}


def get_required_xp(level: int) -> int:
    """Порог XP для перехода с level на level+1."""
    if level >= MAX_LEVEL:
        return 0
    if level in _xp_cache:
        return _xp_cache[level]

    if level < 5:
        threshold = BASE_THRESHOLD
    else:
        threshold = BASE_THRESHOLD
        for _ in range(5, level + 1):
            threshold = int(threshold * SCALING_FACTOR)

    _xp_cache[level] = threshold
    return threshold


def add_xp(user, amount: int) -> list[int]:
    """
    Начисляет XP и проверяет повышение уровня.
    Возвращает список новых уровней (может быть несколько за раз).

    Вызывай после ЛЮБОГО заработка монет:
    - Выигрыш казино
    - Успешное ограбление
    - Продажа генов
    - Лут из сейфа
    - НЕ переводы!
    """
    if amount <= 0:
        return []

    user.xp += amount
    new_levels = []

    while user.level < MAX_LEVEL:
        required = get_required_xp(user.level)
        if required <= 0:
            break
        if user.xp >= required:
            user.xp -= required
            user.level += 1
            new_levels.append(user.level)
            logger.info(f"🆙 User {user.tg_id} → level {user.level}")
        else:
            break

    return new_levels


def can_transfer(user) -> tuple[bool, str]:
    """Проверяет может ли игрок делать переводы."""
    if user.level < MIN_TRANSFER_LEVEL:
        return False, (
            f"❌ <b>Переводы доступны с {MIN_TRANSFER_LEVEL} уровня!</b>\n\n"
            f"⭐ Ваш уровень: <b>{user.level}</b>\n"
            f"📈 До {MIN_TRANSFER_LEVEL} уровня: зарабатывайте монеты (казино, ограбления, продажа генов)"
        )
    return True, ""


def build_progress_bar(current_xp: int, required_xp: int, length: int = 10) -> str:
    """Прогресс-бар: [▓▓▓▓░░░░░░] 40%"""
    if required_xp <= 0:
        return "[▓▓▓▓▓▓▓▓▓▓] MAX"
    ratio = min(1.0, current_xp / required_xp)
    filled = int(ratio * length)
    empty = length - filled
    pct = int(ratio * 100)
    return f"[{'▓' * filled}{'░' * empty}] {pct}%"


def format_level_line(user) -> str:
    """Готовая строка для /profile."""
    req = get_required_xp(user.level)
    bar = build_progress_bar(user.xp, req)
    if user.level >= MAX_LEVEL:
        return f"⭐ Уровень: <b>{user.level}</b> {bar}"
    return f"⭐ Уровень: <b>{user.level}</b> {bar} <code>{user.xp:,}/{req:,}</code>"
