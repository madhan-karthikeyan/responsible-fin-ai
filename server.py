from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from query import QueryEngine

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # your frontend tunnel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str

@app.api_route("/query", methods=["POST"])
def handle_query(request: QueryRequest):
    query_engine = QueryEngine()
    response = query_engine.query(request.query)
    return {"answer": response.response}

# @app.api_route("/health", methods=["GET", "OPTIONS"])
# def health_check():
#     return {"status": "ok"}