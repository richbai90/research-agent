from pydantic import BaseModel, Field
from typing import TypedDict, List, Literal


class IdeaCard(BaseModel):
    title: str = Field(description="5-10 word title")
    hypothesis: str = Field(description="One-sentence falsifiable hypothesis")
    novelty_claim: str = Field(description="What is new relative to baselines")
    why_it_matters: str = Field(description="2-3 sentences explaining significance")
    differentiator: str = Field(description="Comparison against specific baselines")
    key_assumptions: List[str] = Field(description="3-6 critical assumptions")
    failure_modes: List[str] = Field(description="3-8 ways this dies")
    experimental_details: str = Field(
        description="Detailed breakdown of the decisive test, setup, and measurements to fit the time horizon."
    )
    refinement_process: str = Field(
        description="Explicit details on how this experiment was formulated and refined based on previous feedback. If this is attempt 1, state 'Initial formulation based on gap analysis'."
    )
    stop_pivot_rules: str = Field(description="Explicit stop and pivot conditions")
    week_one_plan: List[str] = Field(description="3-6 actionable steps")
    risk_assessment: str = Field(
        description="Technical, Novelty, Execution, and Confidence levels"
    )
    relevant_sources: List[str] = Field(
        description="List of specific papers (Title, DOI, or Author) from the provided literature context that support or baseline this idea."
    )


class GenerationOutput(BaseModel):
    idea_cards: List[IdeaCard]
    go_no_go_summary: str = Field(
        description="Top ideas to pursue, ideas to kill, missing info"
    )


class ResearchState(TypedDict):
    domain: str
    optimized_query: str
    settings: dict
    raw_papers: str
    gaps_and_baselines: str
    idea_cards: List[dict]
    feedback: str
    iteration: int
    status: Literal["continue", "loop", "final"]
