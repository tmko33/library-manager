"""Seed the database with demo data."""

import asyncio
from datetime import date, timedelta

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models import (
    Author,
    Book,
    BookCopy,
    Branch,
    Country,
    Member,
    MemberRole,
    Publisher,
)

DEMO_PASSWORD = "library12345"


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        existing = await session.scalar(select(Member).where(Member.email == "admin@library.dev"))
        if existing is not None:
            print("Database already seeded, nothing to do.")
            return

        colombia = Country(name="Colombia", iso_code="CO")
        argentina = Country(name="Argentina", iso_code="AR")
        spain = Country(name="España", iso_code="ES")
        chile = Country(name="Chile", iso_code="CL")
        session.add_all([colombia, argentina, spain, chile])
        await session.flush()

        sudamericana = Publisher(name="Sudamericana", website="https://sudamericana.com")
        anagrama = Publisher(name="Anagrama", website="https://anagrama-ed.es")
        session.add_all([sudamericana, anagrama])
        await session.flush()

        garcia_marquez = Author(
            name="Gabriel García Márquez",
            bio="Colombian novelist and Nobel laureate.",
            birth_year=1927,
            country_id=colombia.id,
        )
        borges = Author(
            name="Jorge Luis Borges",
            bio="Argentine writer of short stories and essays.",
            birth_year=1899,
            country_id=argentina.id,
        )
        cortazar = Author(
            name="Julio Cortázar",
            bio="Argentine novelist and short story writer.",
            birth_year=1914,
            country_id=argentina.id,
        )
        allende = Author(
            name="Isabel Allende",
            bio="Chilean-American novelist.",
            birth_year=1942,
            country_id=chile.id,
        )
        session.add_all([garcia_marquez, borges, cortazar, allende])
        await session.flush()

        books = [
            Book(
                isbn="9780307474728",
                title="Cien años de soledad",
                publication_year=1967,
                summary="The multi-generational story of the Buendía family.",
                language="es",
                pages=471,
                publisher_id=sudamericana.id,
                authors=[garcia_marquez],
            ),
            Book(
                isbn="9788420633135",
                title="El Aleph",
                publication_year=1949,
                summary="A collection of short stories about infinity and memory.",
                language="es",
                pages=146,
                publisher_id=anagrama.id,
                authors=[borges],
            ),
            Book(
                isbn="9788437604572",
                title="Rayuela",
                publication_year=1963,
                summary="An experimental novel that can be read in several orders.",
                language="es",
                pages=736,
                publisher_id=sudamericana.id,
                authors=[cortazar],
            ),
            Book(
                isbn="9788401352822",
                title="La casa de los espíritus",
                publication_year=1982,
                summary="A family saga spanning four generations.",
                language="es",
                pages=448,
                publisher_id=anagrama.id,
                authors=[allende],
            ),
        ]
        session.add_all(books)
        await session.flush()

        central = Branch(
            name="Biblioteca Central",
            address="Calle 10 # 5-20",
            city="Bogotá",
            country_id=colombia.id,
        )
        north = Branch(
            name="Biblioteca Norte",
            address="Carrera 45 # 120-30",
            city="Bogotá",
            country_id=colombia.id,
        )
        session.add_all([central, north])
        await session.flush()

        counter = 1
        for book in books:
            for _ in range(3):
                session.add(
                    BookCopy(
                        inventory_code=f"BC-{counter:04d}",
                        book_id=book.id,
                        branch_id=central.id,
                        acquired_at=date.today() - timedelta(days=90),
                    )
                )
                counter += 1

        session.add_all(
            [
                Member(
                    email="admin@library.dev",
                    hashed_password=hash_password(DEMO_PASSWORD),
                    full_name="Ada Admin",
                    role=MemberRole.ADMIN,
                ),
                Member(
                    email="librarian@library.dev",
                    hashed_password=hash_password(DEMO_PASSWORD),
                    full_name="Leo Librarian",
                    role=MemberRole.LIBRARIAN,
                ),
                Member(
                    email="member@library.dev",
                    hashed_password=hash_password(DEMO_PASSWORD),
                    full_name="Mia Member",
                    role=MemberRole.MEMBER,
                ),
            ]
        )

        await session.commit()
        print("Demo data created.")


if __name__ == "__main__":
    asyncio.run(seed())
