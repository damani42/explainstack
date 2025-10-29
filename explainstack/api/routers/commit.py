from fastapi import APIRouter
from pydantic import BaseModel
from ..core.agents import run_agent

router = APIRouter()

class CommitRequest(BaseModel):
    content: str

@router.post("/commit")
async def write_commit(request: CommitRequest):
    result = run_agent("commit_writer", request.content)
    return {"result": result}
