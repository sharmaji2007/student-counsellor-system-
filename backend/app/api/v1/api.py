from fastapi import APIRouter
from app.api.v1.endpoints import auth, students, assignments, ocr, chat, risk

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(assignments.router, prefix="/assignments", tags=["assignments"])
api_router.include_router(ocr.router, prefix="/ocr", tags=["ocr"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(risk.router, prefix="/risk", tags=["risk"])