"""API v1 router composition."""

from fastapi import APIRouter

from app.api.v1.routers import (
    auth,
    authors,
    books,
    branches,
    copies,
    countries,
    fines,
    loans,
    members,
    publishers,
    reservations,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(authors.router)
api_router.include_router(books.router)
api_router.include_router(branches.router)
api_router.include_router(copies.router)
api_router.include_router(countries.router)
api_router.include_router(fines.router)
api_router.include_router(loans.router)
api_router.include_router(members.router)
api_router.include_router(publishers.router)
api_router.include_router(reservations.router)
