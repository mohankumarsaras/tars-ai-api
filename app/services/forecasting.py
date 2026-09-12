from sqlalchemy.orm import Session
from app import models
from app.services.llm.gateway import AIGateway
from app.services.intelligence import IntelligenceEngine
import json

class ForecastingEngine:
    def __init__(self, db: Session):
        self.db = db
        self.llm = AIGateway.get_llm_provider()
        self.intel = IntelligenceEngine(db)

    def generate_forecast(self, user_id: int, query: str) -> models.ForecastScenario:
        profile_summary = self.intel.aggregate_profile(user_id)
        
        system_msg = """You are TARS, a highly realistic Career Forecasting Engine.
You evaluate a user's "What if" scenario against their current profile and generate 2-3 distinct potential career paths.

STRICT RULES:
1. Do NOT present predictions as guaranteed.
2. Use probabilistic/qualitative language ("This appears to be...", "Likely requires...", "Might be challenging...").
3. Format output strictly as JSON representing a list of paths:
[
  {
    "path_name": "...",
    "current_skill_fit": "...",
    "experience_leverage": "...",
    "skill_gap": "...",
    "learning_effort": "...",
    "transition_difficulty": "...",
    "market_relevance": "...",
    "growth_potential": "...",
    "summary_assessment": "..."
  }
]"""

        prompt = f"User Query: {query}\n\nCurrent Profile:\n{profile_summary}"
        response = self.llm.generate_response(prompt, system_message=system_msg)
        
        scenario = models.ForecastScenario(user_id=user_id, query=query)
        self.db.add(scenario)
        self.db.commit()
        self.db.refresh(scenario)
        
        try:
            clean_resp = response.replace('`json', '').replace('`', '').strip()
            paths_data = json.loads(clean_resp)
            if not isinstance(paths_data, list):
                paths_data = [paths_data]
                
            for path_data in paths_data:
                path = models.ForecastPath(
                    scenario_id=scenario.id,
                    path_name=path_data.get("path_name", "Unknown Path"),
                    current_skill_fit=path_data.get("current_skill_fit", ""),
                    experience_leverage=path_data.get("experience_leverage", ""),
                    skill_gap=path_data.get("skill_gap", ""),
                    learning_effort=path_data.get("learning_effort", ""),
                    transition_difficulty=path_data.get("transition_difficulty", ""),
                    market_relevance=path_data.get("market_relevance", ""),
                    growth_potential=path_data.get("growth_potential", ""),
                    summary_assessment=path_data.get("summary_assessment", "")
                )
                self.db.add(path)
                
            self.db.commit()
            self.db.refresh(scenario)
        except:
            # Fallback path on JSON parse failure
            path = models.ForecastPath(
                scenario_id=scenario.id,
                path_name="Error parsing LLM output",
                summary_assessment=response
            )
            self.db.add(path)
            self.db.commit()
            self.db.refresh(scenario)
            
        return scenario
