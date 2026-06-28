from fastapi import FastAPI
from app.api.assets import router
from app.api.relationships import router as relationships_router
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Asset API")
app.include_router(router)
app.include_router(relationships_router)
