import uuid

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.tenant import Tenant
from app.models.user import User
from app.models.widget import Widget


DEMO_TENANT_ID = uuid.UUID(
    "11111111-1111-1111-1111-111111111111"
)

DEMO_USER_ID = uuid.UUID(
    "22222222-2222-2222-2222-222222222222"
)

DEMO_WIDGET_ID = uuid.UUID(
    "33333333-3333-3333-3333-333333333333"
)

DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "DemoPassword123!"


def seed():
    db = SessionLocal()

    try:
        tenant = db.get(
            Tenant,
            DEMO_TENANT_ID
        )

        if tenant is None:
            tenant = Tenant(
                id=DEMO_TENANT_ID,
                name="Demo Company"
            )

            db.add(tenant)

        user = db.scalar(
            select(User).where(
                User.email == DEMO_EMAIL
            )
        )

        if user is None:
            user = User(
                id=DEMO_USER_ID,
                tenant_id=DEMO_TENANT_ID,
                email=DEMO_EMAIL,
                password_hash=hash_password(
                    DEMO_PASSWORD
                )
            )

            db.add(user)

        widget = db.get(
            Widget,
            DEMO_WIDGET_ID
        )

        if widget is None:
            widget = Widget(
                id=DEMO_WIDGET_ID,
                tenant_id=DEMO_TENANT_ID,
                name="Demo Contact Form",
                type="CONTACT_FORM",
                title="Contact Us",
                description="Send us a message.",
                button_text="Send Message",
                fields=[
                    {
                        "name": "email",
                        "type": "email",
                        "label": "Email",
                        "required": True
                    },
                    {
                        "name": "message",
                        "type": "text",
                        "label": "Message",
                        "required": True
                    }
                ],
                display_options={
                    "position": "bottom-right"
                },
                is_active=True
            )

            db.add(widget)

        db.commit()

        print("Seed complete.")
        print()
        print(f"Email:      {DEMO_EMAIL}")
        print(f"Password:   {DEMO_PASSWORD}")
        print(f"Widget ID:  {DEMO_WIDGET_ID}")
        print()
        print(
            "Customer site: "
            "http://localhost:5500"
        )

    finally:
        db.close()


if __name__ == "__main__":
    seed()