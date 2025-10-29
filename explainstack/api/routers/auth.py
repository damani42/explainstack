from fastapi import APIRouter

router = APIRouter()

@router.get("/auth/test")
async def auth_test():
    return {"status": "auth stub"}
