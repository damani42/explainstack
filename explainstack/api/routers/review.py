from fastapi import APIRouter
from pydantic import BaseModel
from ..core.agents import run_agent

router = APIRouter()

class ReviewRequest(BaseModel):
    content: str

@router.post("/review")
async def review(request: ReviewRequest):
    result = run_agent("review", request.content)
    return {"result": result}
