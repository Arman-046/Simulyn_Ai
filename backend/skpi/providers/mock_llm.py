import random
from typing import List, Dict, Any
from ..models import Evidence, UncertaintyMetrics

def generate_mock_evidence(product_name: str, industry: str) -> List[Evidence]:
    """Generates mock multi-source evidence for Hackathon MVP."""
    return [
        Evidence(
            source="TechReview.com",
            claim=f"{product_name} introduces groundbreaking features but lacks polish.",
            sentiment=0.6,
            uncertainty=UncertaintyMetrics(confidence=0.9, freshness=1.0, reliability=0.8, coverage=1500)
        ),
        Evidence(
            source="Reddit /r/technology",
            claim=f"Battery life on the new {industry} product is terrible.",
            sentiment=-0.8,
            uncertainty=UncertaintyMetrics(confidence=0.4, freshness=0.5, reliability=0.4, coverage=350)
        ),
        Evidence(
            source="Financial Times",
            claim=f"Pricing strategy for {product_name} is aggressive, likely to capture market share.",
            sentiment=0.7,
            uncertainty=UncertaintyMetrics(confidence=0.95, freshness=3.0, reliability=0.9, coverage=50000)
        )
    ]
