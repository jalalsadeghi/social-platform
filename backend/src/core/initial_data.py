# backend/src/core/initial_data.py
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from modules.user.models import Role, User
from modules.auth.utils import get_password_hash


ADMIN_PERMISSIONS = {
    "plan": {"read": True, "create": True, "delete": True, "update": True},
    "user": {"read": True, "create": True, "delete": True, "update": True},
    "content": {"read": True, "create": True, "delete": True, "update": True},
    "role": {"read": True, "create": True, "delete": True, "update": True},
    "prompt": {"read": True, "create": True, "delete": True, "update": True},
    "platform": {"read": True, "create": True, "delete": True, "update": True},
}

USER_PERMISSIONS = {
    "content": {"read": True, "create": True, "delete": True, "update": True},
    "prompt": {"read": True, "create": True, "delete": True, "update": True},
    "platform": {"read": True, "create": True, "delete": True, "update": True},
}


async def create_initial_data(db: AsyncSession):
    # بررسی وجود نقش‌ها
    result = await db.execute(select(Role).where(Role.name.in_(["user", "admin"])))
    roles = result.scalars().all()
    existing_role_names = {role.name for role in roles}

    # نقش‌های لازم
    roles_to_create = []
    if "user" not in existing_role_names:
        roles_to_create.append(
            Role(
                id=uuid.uuid4(),
                name="user",
                description="User role",
                permissions=USER_PERMISSIONS
            )
        )

    if "admin" not in existing_role_names:
        roles_to_create.append(
            Role(
                id=uuid.uuid4(),
                name="admin",
                description="Admin role",
                permissions=ADMIN_PERMISSIONS
            )
        )

    db.add_all(roles_to_create)
    await db.commit()

    # بارگیری نقش ادمین برای ایجاد کاربر
    result = await db.execute(select(Role).where(Role.name == "admin"))
    admin_role = result.scalars().first()

    # بررسی وجود ادمین
    result = await db.execute(select(User).where(User.username == "admin"))
    existing_admin = result.scalars().first()

    if not existing_admin:
        # ایجاد کاربر ادمین اولیه
        admin_user = User(
            id=uuid.uuid4(),
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin"),
            role_id=admin_role.id,
            full_name="Administrator"
        )

        db.add(admin_user)
        await db.commit()