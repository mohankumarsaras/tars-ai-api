from fastapi import APIRouter
from . import profile, chat, intelligence, assessments, forecasts, dashboard, learning, search, knowledge, education, career, projects, skills, evidence, career_goals, certifications, health

api_router = APIRouter()
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(education.router, prefix="/education", tags=["education"])
api_router.include_router(career.router, prefix="/career", tags=["career"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(skills.router, prefix="/skills", tags=["skills"])
api_router.include_router(evidence.router, prefix="/evidence", tags=["evidence"])
api_router.include_router(career_goals.router, prefix="/career-goals", tags=["career-goals"])

api_router.include_router(certifications.router, prefix="/certifications", tags=["certifications"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(health.router, prefix="/health", tags=["health"])

api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

api_router.include_router(intelligence.router, prefix="/intelligence", tags=["intelligence"])

api_router.include_router(assessments.router, prefix="/assessments", tags=["assessments"])

api_router.include_router(forecasts.router, prefix="/forecasts", tags=["forecasts"])

api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

api_router.include_router(learning.router, prefix="/learning", tags=["learning"])
