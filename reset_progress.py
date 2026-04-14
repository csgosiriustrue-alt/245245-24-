"""
Сброс прогресса всех игроков без удаления аккаунтов.
Запуск: python scripts/reset_progress.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, update, delete, select

from models import User, Inventory, PurchaseLog, GroupChat


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL не найден!")
    sys.exit(1)


async def reset_all_progress():
    engine = create_async_engine(DATABASE_URL, echo=False, poolclass=NullPool)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            # ── 1. Считаем игроков ──
            count_r = await session.execute(select(User))
            total_users = len(count_r.scalars().all())
            print(f"👥 Найдено игроков: {total_users}")

            # ── 2. Сброс баланса и зарядов ──
            await session.execute(
                update(User).values(
                    balance_vv=0,
                    balance_stars=0,
                    box_count=6,
                    jail_until=None,
                    safety_until=None,
                    is_masked=False,
                    black_market_until=None,
                    last_market_check=None,
                    safe_type=None,
                    safe_code=None,
                    safe_health=3,
                    hidden_item_ids=None,
                    hidden_coins=0,
                    safe_level_rusty=1,
                    safe_level_elite=1,
                    security_active=False,
                    security_until=None,
                    roof_active=False,
                    roof_until=None,
                    magazine_until=None,
                    doll_until=None,
                    putana_until=None,
                    casino_bets_today=0,
                    last_casino_reset=None,
                    hazbik_until=None,
                    last_safe_coin_purchase=None,
                    purchase_cooldowns=None,
                )
            )
            print("✅ Баланс, заряды, сейфы, бусты, кулдауны — сброшены")

            # ── 3. Удаляем весь инвентарь ──
            inv_result = await session.execute(delete(Inventory))
            print(f"✅ Инвентарь очищен ({inv_result.rowcount} записей)")

            # ── 4. Удаляем логи покупок ──
            purchases_result = await session.execute(delete(PurchaseLog))
            print(f"✅ Логи покупок удалены ({purchases_result.rowcount} записей)")

            # ── 5. Обнуляем общак во всех чатах ──
            await session.execute(
                update(GroupChat).values(
                    common_pot=0,
                    is_event_active=False,
                )
            )
            print("✅ Общак всех чатов обнулён")

            # ── 6. Удаляем указанных игроков ──
            users_to_delete = ["sslayvibe", "neanarh1a"]
            for username in users_to_delete:
                user_r = await session.execute(
                    select(User).where(User.username == username)
                )
                user = user_r.scalar_one_or_none()
                if user:
                    # Удаляем инвентарь (на случай если cascade не сработал)
                    await session.execute(
                        delete(Inventory).where(Inventory.user_id == user.tg_id)
                    )
                    await session.execute(
                        delete(PurchaseLog).where(PurchaseLog.user_id == user.tg_id)
                    )
                    await session.delete(user)
                    print(f"🗑 Удалён игрок: @{username} (tg_id={user.tg_id})")
                else:
                    print(f"⚠️ Игрок @{username} не найден")

            # ── КОММИТ ──
            await session.commit()
            print("\n" + "=" * 50)
            print("🎉 СБРОС ЗАВЕРШЁН УСПЕШНО!")
            print(f"👥 Осталось игроков: {total_users - len([u for u in users_to_delete])}")
            print("=" * 50)

        except Exception as e:
            await session.rollback()
            print(f"\n❌ ОШИБКА: {e}")
            raise
        finally:
            await session.close()

    await engine.dispose()


if __name__ == "__main__":
    print("=" * 50)
    print("⚠️  СБРОС ПРОГРЕССА ВСЕХ ИГРОКОВ")
    print("=" * 50)
    confirm = input("\nВведите 'RESET' для подтверждения: ")
    if confirm.strip() != "RESET":
        print("❌ Отменено.")
        sys.exit(0)

    print("\nЗапуск сброса...\n")
    asyncio.run(reset_all_progress())