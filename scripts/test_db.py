from sqlalchemy import create_engine, text

from backend.app.config import DATABASE_URL


def main():
    engine = create_engine(DATABASE_URL)

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

        print("Database connection successful.")
        print("Result:", result.scalar())


if __name__ == "__main__":
    main()