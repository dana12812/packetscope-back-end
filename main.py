from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI



app = FastAPI()


@app.get('/health')
def health_check():
  return {'message': 'Api is running'}