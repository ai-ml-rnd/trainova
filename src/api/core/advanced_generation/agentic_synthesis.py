"""Agentic trajectory synthesis."""

from typing import List, Dict, Optional
from pydantic import BaseModel


class TrajectoryStep(BaseModel):
    """Step in agentic trajectory."""
    
    action: str
    observation: Optional[str] = None
    thought: Optional[str] = None


class Trajectory(BaseModel):
    """Agentic trajectory."""
    
    trajectory_id: str
    steps: List[TrajectoryStep]
    final_output: Optional[str] = None


class AgenticSynthesizer:
    """Synthesize trajectories from agent interactions."""
    
    def __init__(self):
        self._trajectories: Dict[str, Trajectory] = {}
    
    async def synthesize(
        self,
        agent_interactions: List[Dict],
    ) -> Trajectory:
        """Synthesize trajectory from agent interactions."""
        steps = []
        
        for interaction in agent_interactions:
            step = TrajectoryStep(
                action=interaction.get("action", ""),
                observation=interaction.get("observation"),
                thought=interaction.get("thought"),
            )
            steps.append(step)
        
        trajectory = Trajectory(
            trajectory_id="traj-1",
            steps=steps,
            final_output=steps[-1].observation if steps else None,
        )
        
        self._trajectories[trajectory.trajectory_id] = trajectory
        return trajectory
    
    def get_trajectory(self, trajectory_id: str) -> Optional[Trajectory]:
        """Get trajectory by ID."""
        return self._trajectories.get(trajectory_id)


def synthesize_trajectory(interactions: List[Dict]) -> Dict:
    """Synthesize trajectory from interactions."""
    synthesizer = AgenticSynthesizer()
    trajectory = synthesizer.synthesize(interactions)
    
    return {
        "trajectory_id": trajectory.trajectory_id,
        "steps": [s.dict() for s in trajectory.steps],
        "final_output": trajectory.final_output,
    }
