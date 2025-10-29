from fastapi import APIRouter
from pydantic import BaseModel
from ..core.agents import run_agent

router = APIRouter()

class CleanRequest(BaseModel):
    content: str

@router.post("/clean")
async def clean_code(request: CleanRequest):
    result = run_agent("import_cleaner", request.content)
    return {"result": result}
