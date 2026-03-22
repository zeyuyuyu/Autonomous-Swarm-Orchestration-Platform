import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
import asyncio

@dataclass
class SwarmAgent:
    id: str
    position: Tuple[float, float, float]
    capabilities: List[str]
    status: str = 'idle'
    current_task: str = None

class SwarmCoordinator:
    def __init__(self):
        self.agents: Dict[str, SwarmAgent] = {}
        self.tasks: Dict[str, Dict] = {}
        self.allocation_matrix = None
    
    async def register_agent(self, agent_id: str, position: Tuple[float, float, float], capabilities: List[str]):
        """Register a new agent in the swarm"""
        self.agents[agent_id] = SwarmAgent(
            id=agent_id,
            position=position,
            capabilities=capabilities
        )
        await self._update_allocation_matrix()
    
    async def add_task(self, task_id: str, position: Tuple[float, float, float], required_capabilities: List[str], priority: int = 1):
        """Add a new task to be allocated"""
        self.tasks[task_id] = {
            'position': position,
            'required_capabilities': required_capabilities,
            'priority': priority,
            'status': 'pending'
        }
        await self._update_allocation_matrix()
    
    async def _update_allocation_matrix(self):
        """Update the task allocation matrix using Hungarian algorithm"""
        n_agents = len(self.agents)
        n_tasks = len(self.tasks)
        
        if n_agents == 0 or n_tasks == 0:
            self.allocation_matrix = None
            return
            
        cost_matrix = np.zeros((n_agents, n_tasks))
        
        for i, agent in enumerate(self.agents.values()):
            for j, task in enumerate(self.tasks.values()):
                # Calculate cost based on distance and capability match
                distance = self._calculate_distance(agent.position, task['position'])
                capability_match = self._calculate_capability_match(
                    agent.capabilities, 
                    task['required_capabilities']
                )
                cost_matrix[i,j] = distance / capability_match * (1/task['priority'])
        
        self.allocation_matrix = cost_matrix
        await self._assign_tasks()
    
    def _calculate_distance(self, pos1: Tuple[float, float, float], pos2: Tuple[float, float, float]) -> float:
        """Calculate Euclidean distance between two 3D points"""
        return np.sqrt(sum((p1 - p2) ** 2 for p1, p2 in zip(pos1, pos2)))
    
    def _calculate_capability_match(self, agent_caps: List[str], required_caps: List[str]) -> float:
        """Calculate capability match score between agent and task"""
        matches = sum(1 for cap in required_caps if cap in agent_caps)
        return matches / len(required_caps) if required_caps else 1.0
    
    async def _assign_tasks(self):
        """Assign tasks to agents based on allocation matrix"""
        if self.allocation_matrix is None:
            return
            
        # Use Hungarian algorithm for optimal assignment
        from scipy.optimize import linear_sum_assignment
        agent_indices, task_indices = linear_sum_assignment(self.allocation_matrix)
        
        agent_list = list(self.agents.values())
        task_list = list(self.tasks.items())
        
        for agent_idx, task_idx in zip(agent_indices, task_indices):
            agent = agent_list[agent_idx]
            task_id, task = task_list[task_idx]
            
            if self.allocation_matrix[agent_idx, task_idx] < float('inf'):
                agent.status = 'assigned'
                agent.current_task = task_id
                task['status'] = 'assigned'
    
    async def update_agent_position(self, agent_id: str, new_position: Tuple[float, float, float]):
        """Update agent position and recalculate assignments if needed"""
        if agent_id in self.agents:
            self.agents[agent_id].position = new_position
            await self._update_allocation_matrix()
    
    async def complete_task(self, task_id: str):
        """Mark task as complete and reassign agents"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            for agent in self.agents.values():
                if agent.current_task == task_id:
                    agent.status = 'idle'
                    agent.current_task = None
            await self._update_allocation_matrix()
    
    def get_agent_status(self, agent_id: str) -> Dict:
        """Get current status of an agent"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            return {
                'status': agent.status,
                'position': agent.position,
                'current_task': agent.current_task
            }
        return None
    
    def get_task_status(self, task_id: str) -> Dict:
        """Get current status of a task"""
        return self.tasks.get(task_id)