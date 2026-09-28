from sqlalchemy import text

from app.database.database import engine


with engine.connect() as connection:
    result = connection.execute(text("SELECT 1"))
    print(result.scalar())
    
from app.config import settings
from sqlalchemy import text
from app.database.database import engine

print("DATABASE URL:", settings.DATABASE_URL)

with engine.connect() as connection:
    print(
        "DATABASE:",
        connection.execute(text("SELECT current_database()")).scalar()
    )

    print(
        "SCHEMA:",
        connection.execute(text("SELECT current_schema()")).scalar()
    )

    print(
        "INVOICE COUNT:",
        connection.execute(
            text("SELECT COUNT(*) FROM public.invoices")
        ).scalar()
    )