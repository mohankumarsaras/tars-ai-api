from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date

class UserProfileBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    bio: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    professional_summary: Optional[str] = None
    current_role: Optional[str] = None
    career_start_date: Optional[date] = None
    career_interests: Optional[str] = None
    target_roles: Optional[str] = None
    portfolio_url: Optional[str] = None
    technologies: Optional[str] = None
    responsibilities: Optional[str] = None
    architecture: Optional[str] = None
    repository_url: Optional[str] = None
    deployment_url: Optional[str] = None
    lessons_learned: Optional[str] = None

class UserProfileCreate(UserProfileBase):
    pass

class UserProfile(UserProfileBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class EducationBase(BaseModel):
    user_id: int
    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    subjects: Optional[str] = None
    academic_projects: Optional[str] = None
    courses: Optional[str] = None

class EducationCreate(EducationBase):
    pass

class Education(EducationBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class CompanyBase(BaseModel):
    name: str
    industry: Optional[str] = None
    website: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CareerExperienceBase(BaseModel):
    user_id: int
    title: str
    start_date: date
    end_date: Optional[date] = None
    description: Optional[str] = None
    is_current: bool = False
    technologies: Optional[str] = None
    achievements: Optional[str] = None
    problems_solved: Optional[str] = None

class CareerExperienceCreate(CareerExperienceBase):
    company: CompanyCreate

class CareerExperience(CareerExperienceBase):
    id: int
    company_id: int
    model_config = ConfigDict(from_attributes=True)

class ProjectBase(BaseModel):
    user_id: int
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    url: Optional[str] = None

class ProjectCreate(ProjectBase):
    skill_ids: Optional[List[int]] = []

class Project(ProjectBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class SkillBase(BaseModel):
    category_id: int
    name: str
    description: Optional[str] = None
    familiarity: Optional[str] = None

class SkillCreate(SkillBase):
    pass

class Skill(SkillBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class EvidenceBase(BaseModel):
    user_id: int
    description: str
    url: Optional[str] = None
    skill_id: Optional[int] = None
    project_id: Optional[int] = None
    career_experience_id: Optional[int] = None

class EvidenceCreate(EvidenceBase):
    pass

class Evidence(EvidenceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class CareerGoalBase(BaseModel):
    user_id: int
    title: str
    description: Optional[str] = None
    target_date: Optional[date] = None
    is_achieved: bool = False

class CareerGoalCreate(CareerGoalBase):
    pass

class CareerGoal(CareerGoalBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class CertificationBase(BaseModel):
    user_id: int
    name: str
    issuer: str
    issue_date: Optional[date] = None
    expiration_date: Optional[date] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    related_skills: Optional[str] = None

class CertificationCreate(CertificationBase):
    pass

class Certification(CertificationBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

from datetime import datetime

class KnowledgeRecordBase(BaseModel):
    user_id: int
    title: str
    content: str
    category: Optional[str] = None
    source: Optional[str] = None
    source_type: Optional[str] = None
    verification_status: Optional[str] = "UNVERIFIED"
    confidence: Optional[str] = "MEDIUM"
    tags: Optional[str] = None
    related_skills: Optional[str] = None

class KnowledgeRecordCreate(KnowledgeRecordBase):
    pass

class KnowledgeRecordUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    source: Optional[str] = None
    source_type: Optional[str] = None
    verification_status: Optional[str] = None
    confidence: Optional[str] = None
    tags: Optional[str] = None
    related_skills: Optional[str] = None

class KnowledgeRecord(KnowledgeRecordBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class SkillEvaluation(BaseModel):
    id: int
    skill_id: int
    overall_score: int
    knowledge_score: int
    hands_on_score: int
    troubleshooting_score: int
    architecture_score: int
    security_score: int
    cost_score: int
    communication_score: int
    confidence_level: str
    missing_evidence: Optional[str] = None
    explanation: Optional[str] = None
    last_calculated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CareerAnalysis(BaseModel):
    id: int
    user_id: int
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    skill_gaps: Optional[str] = None
    career_risks: Optional[str] = None
    opportunities: Optional[str] = None
    recommended_skills: Optional[str] = None
    recommended_projects: Optional[str] = None
    suitable_roles: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Assessment(BaseModel):
    id: int
    skill_id: int
    assessment_type: str
    content: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AssessmentAttempt(BaseModel):
    id: int
    assessment_id: int
    user_responses: str
    score: Optional[int] = None
    feedback: Optional[str] = None
    evidence_id: Optional[int] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ForecastPathBase(BaseModel):
    path_name: str
    current_skill_fit: Optional[str] = None
    experience_leverage: Optional[str] = None
    skill_gap: Optional[str] = None
    learning_effort: Optional[str] = None
    transition_difficulty: Optional[str] = None
    market_relevance: Optional[str] = None
    growth_potential: Optional[str] = None
    summary_assessment: Optional[str] = None

class ForecastPath(ForecastPathBase):
    id: int
    scenario_id: int
    model_config = ConfigDict(from_attributes=True)

class ForecastScenario(BaseModel):
    id: int
    user_id: int
    query: str
    created_at: datetime
    paths: list[ForecastPath] = []
    model_config = ConfigDict(from_attributes=True)

class AuditLog(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    ip_address: Optional[str]
    details: Optional[str]
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class LearningActivity(BaseModel):
    id: int
    user_id: int
    knowledge_id: int
    skill_id: int
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class LearningHistory(BaseModel):
    id: int
    user_id: int
    activity_id: int
    assessment_id: Optional[int]
    evidence_id: Optional[int]
    skill_improvement_delta: Optional[float]
    next_recommendation: Optional[str]
    completed_at: datetime
    model_config = ConfigDict(from_attributes=True)
