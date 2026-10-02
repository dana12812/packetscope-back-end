from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI

# Controllers
from controllers.users import router as UsersRouter
from controllers.captures import router as CapturesRouter
from controllers.annotations import router as AnnotationsRouter
from controllers.tags import router as TagsRouter

app = FastAPI()

app.include_router(UsersRouter, prefix='/api')
app.include_router(CapturesRouter, prefix='/api')
app.include_router(AnnotationsRouter, prefix='/api')
app.include_router(TagsRouter, prefix='/api')


@app.get('/health')
def health_check():
  return {'message': 'Api is running'}