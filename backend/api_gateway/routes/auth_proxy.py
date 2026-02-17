from fastapi import APIRouter, status, Response, Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import httpx
from ..schemas import auth_schema

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication Proxy"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

REQUEST_TIMEOUT = httpx.Timeout(10.0, read=10.0)


async def _request_with_timeout(method: str, url: str, **kwargs) -> httpx.Response:
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            return await client.request(method, url, **kwargs)
        except httpx.ReadTimeout:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Auth service did not respond in time",
            )


@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    payload = {"username": form_data.username, "password": form_data.password}

    response = await _request_with_timeout(
        "POST",
        "http://localhost:8001/auth/login",
        data=payload,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
    )

    if response.status_code != 200:
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers={"Content-Type": "application/json"},
        )

    success_response = Response(
        content=response.content, status_code=status.HTTP_200_OK
    )
    success_response.set_cookie(
        key="access_token",
        value=response.json().get("access_token"),
        httponly=True,
        secure=True,
        samesite="lax",
    )
    success_response.set_cookie(
        key="refresh_token",
        value=response.json().get("refresh_token"),
        httponly=True,
        secure=True,
        samesite="lax",
    )

    return success_response
    
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: auth_schema.UserCreate):
    response = await _request_with_timeout(
        "POST",
        "http://localhost:8001/auth/register",
        json=user.model_dump(),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    if response.status_code != 201:
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers={"Content-Type": "application/json"},
        )

    return Response(
        content=response.content,
        status_code=status.HTTP_201_CREATED,
        headers={"Content-Type": "application/json"},
    )
    
@router.get("/validate-user", status_code=status.HTTP_200_OK)
async def validate_user(Authorization: str = Header(...)):
    bearer_token = Authorization

    if not bearer_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing access token")

    response = await _request_with_timeout(
        "GET",
        "http://localhost:8001/auth/validate-user",
        headers={"Authorization": bearer_token, "Accept": "application/json"},
    )

    if response.status_code != 200:
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers={"Content-Type": "application/json"},
        )

    return Response(
        content=response.content,
        status_code=status.HTTP_200_OK,
        headers={"Content-Type": "application/json"},
    )

@router.post("/refresh-token", status_code=status.HTTP_200_OK)
async def refresh_token(Authorization: str = Header(...)):
    bearer_token = Authorization

    if not bearer_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing access token")

    response = await _request_with_timeout(
        "GET",
        "http://localhost:8001/auth/refresh-token",
        headers={"Authorization": bearer_token, "Accept": "application/json"},
    )

    if response.status_code != 200:
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers={"Content-Type": "application/json"},
        )

    return Response(
        content=response.content,
        status_code=status.HTTP_200_OK,
        headers={"Content-Type": "application/json"},
    )

@router.patch("/update-user", status_code=status.HTTP_200_OK)
async def update_user(user: auth_schema.UpdateUser, Authorization: str = Header(...)):
    bearer_token = Authorization

    if not bearer_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing access token")
    print("Received update user request with data:", user.model_dump())
    response = await _request_with_timeout(
        "PATCH",
        "http://localhost:8001/auth/update-user",
        json=user.model_dump(exclude_unset=True),
        headers={
            "Authorization": bearer_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    if response.status_code != 200:
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers={"Content-Type": "application/json"},
        )

    return Response(
        content=response.content,
        status_code=status.HTTP_200_OK,
        headers={"Content-Type": "application/json"},
    )
    
@router.delete("/delete-user", status_code=status.HTTP_202_ACCEPTED)
async def delete_user(user: auth_schema.DeleteUser, Authorization: str = Header(...)):
    bearer_token = Authorization

    if not bearer_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing access token")

    response = await _request_with_timeout(
        "POST",
        "http://localhost:8001/auth/delete-user",
        json=user.model_dump(),
        headers={
            "Authorization": bearer_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    if response.status_code != 202:
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers={"Content-Type": "application/json"},
        )

    return Response(
        content=response.content,
        status_code=status.HTTP_202_ACCEPTED,
        headers={"Content-Type": "application/json"},
    )

@router.post("/password-reset-request", status_code=status.HTTP_202_ACCEPTED)
async def password_reset_request(email: dict):
    response = await _request_with_timeout(
        "POST",
        "http://localhost:8001/auth/password-reset-request",
        json=email,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )

    if response.status_code != 202:
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers={"Content-Type": "application/json"},
        )

    return Response(
        content=response.content,
        status_code=status.HTTP_202_ACCEPTED,
        headers={"Content-Type": "application/json"},
    )

@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def password_reset(password: dict):
    response = await _request_with_timeout(
        "POST",
        "http://localhost:8001/auth/reset-password",
        json=password,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )

    if response.status_code != 200:
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers={"Content-Type": "application/json"},
        )

    return Response(
        content=response.content,
        status_code=status.HTTP_200_OK,
        headers={"Content-Type": "application/json"},
    )

@router.post("/password-update", status_code=status.HTTP_200_OK)
async def update_password(data: auth_schema.UpdatePassword, Authorization: str = Header(...)):
    bearer_token = Authorization

    if not bearer_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing access token")
    
    response = await _request_with_timeout("POST", "http://localhost:8001/auth/password-update", json=data.model_dump(), headers={"Authorization": bearer_token, "Content-Type": "application/json", "Accept": "application/json"})

    if response.status_code != 200:
        return Response(content=response.content, status_code=response.status_code, headers={"Content-Type": "application/json"})
    
    return Response(content=response.content, status_code=status.HTTP_200_OK, headers={"Content-Type": "application/json"})
