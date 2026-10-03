from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.environment import CORS_ORIGINS
from database import engine
from models import Base

# Controllers
from controllers.users import router as UsersRouter
from controllers.captures import router as CapturesRouter
from controllers.annotations import router as AnnotationsRouter
from controllers.tags import router as TagsRouter
from controllers.admin import router as AdminRouter

# Create any missing tables (no data) so a fresh production database works without seed.py
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(UsersRouter, prefix='/api')
app.include_router(CapturesRouter, prefix='/api')
app.include_router(AnnotationsRouter, prefix='/api')
app.include_router(TagsRouter, prefix='/api')
app.include_router(AdminRouter, prefix='/api')


@app.get('/health')
def health_check():
  return {'message': 'Api is running'}
