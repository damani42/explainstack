from fastapi import FastAPI

from .routers import analyze, review, clean, commit, auth, stats

app = FastAPI(title="ExplainStack API")

# Include routers with prefixes
app.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
app.include_router(review.router, prefix="/review", tags=["review"])
app.include_router(clean.router, prefix="/clean", tags=["clean"])
app.include_router(commit.router, prefix="/commit", tags=["commit"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(stats.router, prefix="/stats", tags=["stats"])
