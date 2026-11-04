"""Auth endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentMember, SessionDep
from app.schemas.auth import Token
from app.schemas.member import MemberCreate, MemberRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=MemberRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new member",
)
async def register(data: MemberCreate, session: SessionDep) -> MemberRead:
    member = await AuthService(session).register(data)
    return MemberRead.model_validate(member)


@router.post("/login", response_model=Token, summary="Obtain an access token")
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
) -> Token:
    service = AuthService(session)
    member = await service.authenticate(form.username, form.password)
    return service.issue_token(member)


@router.get("/me", response_model=MemberRead, summary="Return the current member")
async def read_current_member(current: CurrentMember) -> MemberRead:
    return MemberRead.model_validate(current)
