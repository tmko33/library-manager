"""Country endpoints."""

from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import PageDep, SessionDep, StaffMember
from app.core.pagination import Page
from app.schemas.common import Message
from app.schemas.country import CountryCreate, CountryRead, CountryUpdate
from app.services.country_service import CountryService

router = APIRouter(prefix="/countries", tags=["countries"])


@router.get("", response_model=Page[CountryRead], summary="List countries")
async def list_countries(
    session: SessionDep,
    params: PageDep,
    q: Annotated[str | None, Query(max_length=100)] = None,
) -> Page[CountryRead]:
    countries, total = await CountryService(session).list_countries(
        offset=params.offset, limit=params.limit, q=q
    )
    return Page.from_orm_items(countries, total, params, CountryRead)


@router.post(
    "",
    response_model=CountryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a country",
)
async def create_country(data: CountryCreate, session: SessionDep, _: StaffMember) -> CountryRead:
    country = await CountryService(session).create_country(data)
    return CountryRead.model_validate(country)


@router.get("/{country_id}", response_model=CountryRead, summary="Get a country")
async def get_country(country_id: int, session: SessionDep) -> CountryRead:
    country = await CountryService(session).get_country(country_id)
    return CountryRead.model_validate(country)


@router.patch("/{country_id}", response_model=CountryRead, summary="Update a country")
async def update_country(
    country_id: int, data: CountryUpdate, session: SessionDep, _: StaffMember
) -> CountryRead:
    country = await CountryService(session).update_country(country_id, data)
    return CountryRead.model_validate(country)


@router.delete("/{country_id}", response_model=Message, summary="Delete a country")
async def delete_country(country_id: int, session: SessionDep, _: StaffMember) -> Message:
    await CountryService(session).delete_country(country_id)
    return Message(message="Country deleted.")
