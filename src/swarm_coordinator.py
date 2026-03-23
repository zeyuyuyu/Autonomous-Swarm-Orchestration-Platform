from typing import Dict, List, Optional
import uuid
import time
from dataclasses import dataclass
from enum import Enum

class SwarmRole(Enum):
    SCOUT = 'scout'
    WORKER = 'worker'
    COORDINATOR = 'coordinator'
    RELAY = 'relay'

@dataclass
class SwarmAgent:
    id: str
    role: SwarmRole
    position: tuple
    status: str
    capabilities: List[str]
    current_task: Optional[str] = None

@dataclass
class Task:
    id: str
    type: str
    priority: int
    requirements: List[str]
    assigned_to: Optional[str] = None
    status: str = 'pending'

class SwarmCoordinator:
    def __init__(self):
        self.agents: Dict[str, SwarmAgent] = {}
        self.tasks: Dict[str, Task] = {}
        self.role_distributions = {
            SwarmRole.SCOUT: 0.2,
            SwarmRole.WORKER: 0.6,
            SwarmRole.RELAY: 0.15,
            SwarmRole.COORDINATOR: 0.05
        }

    def register_agent(self, position: tuple, capabilities: List[str]) -> str:
        agent_id = str(uuid.uuid4())
        role = self._determine_optimal_role()
        
        self.agents[agent_id] = SwarmAgent(
            id=agent_id,
            role=role,
            position=position,
            status='active',
            capabilities=capabilities
        )
        return agent_id

    def _determine_optimal_role(self) -> SwarmRole:
        current_distribution = self._get_role_distribution()
        
        # Find the role that's most under-represented
        target_role = SwarmRole.WORKER
        max_deficit = -1
        
        for role, target_ratio in self.role_distributions.items():
            current_ratio = current_distribution.get(role, 0)
            deficit = target_ratio - current_ratio
            if deficit > max_deficit:
                max_deficit = deficit
                target_role = role
                
        return target_role

    def _get_role_distribution(self) -> Dict[SwarmRole, float]:
        total_agents = len(self.agents)
        if total_agents == 0:
            return {}
            
        distribution = {}
        for role in SwarmRole:
            count = sum(1 for agent in self.agents.values() if agent.role == role)
            distribution[role] = count / total_agents
        return distribution

    def add_task(self, task_type: str, requirements: List[str], priority: int = 1) -> str:
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = Task(
            id=task_id,
            type=task_type,
            priority=priority,
            requirements=requirements
        )
        self._assign_tasks()
        return task_id

    def _assign_tasks(self):
        # Sort tasks by priority
        pending_tasks = sorted(
            [task for task in self.tasks.values() if task.status == 'pending'],
            key=lambda x: x.priority,
            reverse=True
        )
        
        # Find available agents
        available_agents = [
            agent for agent in self.agents.values()
            if agent.current_task is None and agent.status == 'active'
        ]
        
        for task in pending_tasks:
            best_agent = None
            best_score = -1
            
            for agent in available_agents:
                score = self._calculate_assignment_score(agent, task)
                if score > best_score:
                    best_score = score
                    best_agent = agent
            
            if best_agent:
                task.assigned_to = best_agent.id
                task.status = 'assigned'
                best_agent.current_task = task.id
                available_agents.remove(best_agent)

    def _calculate_assignment_score(self, agent: SwarmAgent, task: Task) -> float:
        # Calculate capability match
        capability_score = sum(1 for req in task.requirements if req in agent.capabilities)
        capability_score /= max(len(task.requirements), 1)
        
        # Role suitability
        role_weights = {
            SwarmRole.WORKER: 1.0 if task.type == 'work' else 0.2,
            SwarmRole.SCOUT: 1.0 if task.type == 'explore' else 0.3,
            SwarmRole.RELAY: 1.0 if task.type == 'communicate' else 0.4,
            SwarmRole.COORDINATOR: 0.5
        }
        
        role_score = role_weights.get(agent.role, 0.1)
        
        return (capability_score * 0.7) + (role_score * 0.3)

    def update_task_status(self, task_id: str, status: str):
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = status
            
            if status in ['completed', 'failed']:
                if task.assigned_to:
                    agent = self.agents.get(task.assigned_to)
                    if agent:
                        agent.current_task = None
                task.assigned_to = None

    def get_agent_status(self, agent_id: str) -> Optional[Dict]:
        agent = self.agents.get(agent_id)
        if not agent:
            return None
            
        return {
            'id': agent.id,
            'role': agent.role.value,
            'position': agent.position,
            'status': agent.status,
            'current_task': agent.current_task
        }