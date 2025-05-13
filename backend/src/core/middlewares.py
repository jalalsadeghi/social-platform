# src/core/middlewares.py
from fastapi import Request, HTTPException, status
from modules.auth.utils import verify_token

@app.middleware("http")
async def jwt_cookie_auth(request: Request, call_next):
    if request.url.path.startswith("/auth"):
        return await call_next(request)

    token = request.cookies.get('access_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    token = token.replace("Bearer ", "")
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    request.state.user_id = user_id
    response = await call_next(request)
    return response


@app.middleware("http")
async def exception_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})
