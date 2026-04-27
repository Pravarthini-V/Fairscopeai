# bias_rules.py
from typing import List, Dict

class BiasRulesEngine:
    def __init__(self):
        self.domain_rules = {
            "finance": ["credit_score", "income", "loan_amount", "interest_rate"],
            "healthcare": ["diagnosis", "treatment_cost", "medication", "visit_frequency"],
            "employment": ["salary", "promotion", "performance_score", "tenure"],
            "education": ["gpa", "test_score", "attendance_rate", "graduation"]
        }
        
        self.sensitive_attributes = {
            "finance": ["race", "gender", "age", "income_level"],
            "healthcare": ["race", "ethnicity", "age", "gender", "insurance_status"],
            "employment": ["gender", "race", "age", "religion", "disability"],
            "education": ["race", "gender", "socioeconomic_status", "disability"]
        }
    
    def get_sensitive_attributes(self, domain: str) -> List[str]:
        """Get sensitive attributes for a domain"""
        return self.sensitive_attributes.get(domain, ["protected_class"])
    
    def get_domain_rules(self, domain: str) -> Dict:
        """Get fairness rules for a domain"""
        return {
            "target_columns": self.domain_rules.get(domain, []),
            "sensitive_attrs": self.sensitive_attributes.get(domain, []),
            "fairness_metrics": ["demographic_parity", "equal_opportunity", "predictive_parity"]
        }