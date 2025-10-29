from fastapi import APIRouter
from pydantic import BaseModel
from ..core.agents import run_agent

router = APIRouter()

class AnalyzeRequest(BaseModel):
    content: str

@router.post("/analyze")
async def analyze(request: AnalyzeRequest):
    result = run_agent("analyze", request.content)
    return {"result": result}
