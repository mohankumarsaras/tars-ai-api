from sqlalchemy import Column, Integer, String, Boolean, Date, Text, ForeignKey, Table, Float, DateTime
from sqlalchemy.orm import relationship
from .database.database import Base

# Association table for Project <-> Skill
project_skills = Table(
    "project_skills",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id"), primary_key=True),
)

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    location = Column(String(100), nullable=True)
    professional_summary = Column(Text, nullable=True)
    current_role = Column(String(150), nullable=True)
    career_start_date = Column(Date, nullable=True)
    career_interests = Column(Text, nullable=True)
    target_roles = Column(Text, nullable=True)
    portfolio_url = Column(String(255), nullable=True)
    
    education = relationship("Education", back_populates="user")
    certifications = relationship("Certification", back_populates="user")
    career_experiences = relationship("CareerExperience", back_populates="user")
    projects = relationship("Project", back_populates="user")
    evidence = relationship("Evidence", back_populates="user")
    career_goals = relationship("CareerGoal", back_populates="user")

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    industry = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    
    experiences = relationship("CareerExperience", back_populates="company")

class CareerExperience(Base):
    __tablename__ = "career_experiences"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    title = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    is_current = Column(Boolean, default=False)
    technologies = Column(Text, nullable=True)
    achievements = Column(Text, nullable=True)
    problems_solved = Column(Text, nullable=True)
    
    user = relationship("UserProfile", back_populates="career_experiences")
    company = relationship("Company", back_populates="experiences")
    evidence = relationship("Evidence", back_populates="career_experience")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    url = Column(String(255), nullable=True)
    technologies = Column(Text, nullable=True)
    responsibilities = Column(Text, nullable=True)
    architecture = Column(Text, nullable=True)
    repository_url = Column(String(255), nullable=True)
    deployment_url = Column(String(255), nullable=True)
    lessons_learned = Column(Text, nullable=True)
    
    user = relationship("UserProfile", back_populates="projects")
    skills = relationship("Skill", secondary=project_skills, back_populates="projects")
    evidence = relationship("Evidence", back_populates="project")

class SkillCategory(Base):
    __tablename__ = "skill_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    
    skills = relationship("Skill", back_populates="category")

class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("skill_categories.id"), nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    familiarity = Column(String(50), nullable=True)
    
    category = relationship("SkillCategory", back_populates="skills")
    projects = relationship("Project", secondary=project_skills, back_populates="skills")
    evidence = relationship("Evidence", back_populates="skill")

class Education(Base):
    __tablename__ = "education"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    institution = Column(String(150), nullable=False)
    degree = Column(String(100), nullable=True)
    field_of_study = Column(String(100), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    subjects = Column(Text, nullable=True)
    academic_projects = Column(Text, nullable=True)
    courses = Column(Text, nullable=True)
    
    user = relationship("UserProfile", back_populates="education")

class Certification(Base):
    __tablename__ = "certifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    name = Column(String(150), nullable=False)
    issuer = Column(String(100), nullable=False)
    issue_date = Column(Date, nullable=True)
    expiration_date = Column(Date, nullable=True)
    credential_id = Column(String(100), nullable=True)
    credential_url = Column(String(255), nullable=True)
    related_skills = Column(Text, nullable=True)
    
    user = relationship("UserProfile", back_populates="certifications")

class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    description = Column(Text, nullable=False)
    url = Column(String(255), nullable=True)
    source_type = Column(String(50), nullable=True)
    
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    career_experience_id = Column(Integer, ForeignKey("career_experiences.id"), nullable=True)
    
    user = relationship("UserProfile", back_populates="evidence")
    skill = relationship("Skill", back_populates="evidence")
    project = relationship("Project", back_populates="evidence")
    career_experience = relationship("CareerExperience", back_populates="evidence")

class CareerGoal(Base):
    __tablename__ = "career_goals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    target_date = Column(Date, nullable=True)
    is_achieved = Column(Boolean, default=False)
    
    user = relationship("UserProfile", back_populates="career_goals")

from sqlalchemy import DateTime
import datetime

class KnowledgeRecord(Base):
    __tablename__ = "knowledge_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    source = Column(String(255), nullable=True)
    source_type = Column(String(100), nullable=True)
    verification_status = Column(String(50), default="UNVERIFIED")
    confidence = Column(String(50), default="MEDIUM")
    tags = Column(Text, nullable=True)
    knowledge_type = Column(String(50), default="PERSONAL KNOWLEDGE")
    related_skills = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    user = relationship("UserProfile")

class SkillEvaluation(Base):
    __tablename__ = "skill_evaluations"
    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    overall_score = Column(Integer, default=0)
    knowledge_score = Column(Integer, default=0)
    hands_on_score = Column(Integer, default=0)
    troubleshooting_score = Column(Integer, default=0)
    architecture_score = Column(Integer, default=0)
    security_score = Column(Integer, default=0)
    cost_score = Column(Integer, default=0)
    communication_score = Column(Integer, default=0)
    confidence_level = Column(String(50), nullable=False)
    missing_evidence = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    last_calculated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    skill = relationship("Skill")

class CareerAnalysis(Base):
    __tablename__ = "career_analyses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    strengths = Column(Text, nullable=True)
    weaknesses = Column(Text, nullable=True)
    skill_gaps = Column(Text, nullable=True)
    career_risks = Column(Text, nullable=True)
    opportunities = Column(Text, nullable=True)
    recommended_skills = Column(Text, nullable=True)
    recommended_projects = Column(Text, nullable=True)
    suitable_roles = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Assessment(Base):
    __tablename__ = "assessments"
    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    assessment_type = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)  # JSON string of questions
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    skill = relationship("Skill")

class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    user_responses = Column(Text, nullable=False)  # JSON string of answers
    score = Column(Integer, nullable=True)
    feedback = Column(Text, nullable=True)
    evidence_id = Column(Integer, ForeignKey("evidence.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    assessment = relationship("Assessment")
    evidence = relationship("Evidence")

class ForecastScenario(Base):
    __tablename__ = "forecast_scenarios"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    query = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    paths = relationship("ForecastPath", back_populates="scenario", cascade="all, delete-orphan")

class ForecastPath(Base):
    __tablename__ = "forecast_paths"
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("forecast_scenarios.id"), nullable=False)
    path_name = Column(String(255), nullable=False)
    current_skill_fit = Column(Text, nullable=True)
    experience_leverage = Column(Text, nullable=True)
    skill_gap = Column(Text, nullable=True)
    learning_effort = Column(Text, nullable=True)
    transition_difficulty = Column(Text, nullable=True)
    market_relevance = Column(Text, nullable=True)
    growth_potential = Column(Text, nullable=True)
    summary_assessment = Column(Text, nullable=True)
    
    scenario = relationship("ForecastScenario", back_populates="paths")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    action = Column(String(100), nullable=False)
    ip_address = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class LearningActivity(Base):
    __tablename__ = "learning_activities"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    knowledge_id = Column(Integer, ForeignKey("knowledge_records.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    status = Column(String(50), default="PENDING_ASSESSMENT")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("UserProfile")
    knowledge = relationship("KnowledgeRecord")
    skill = relationship("Skill")

class LearningHistory(Base):
    __tablename__ = "learning_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("learning_activities.id"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=True)
    evidence_id = Column(Integer, ForeignKey("evidence.id"), nullable=True)
    skill_improvement_delta = Column(Float, nullable=True)
    next_recommendation = Column(Text, nullable=True)
    completed_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("UserProfile")
    activity = relationship("LearningActivity")
