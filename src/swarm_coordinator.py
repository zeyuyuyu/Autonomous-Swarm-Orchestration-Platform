import math
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np

class SwarmRole(Enum):
    SCOUT = 'scout'
    WORKER = 'worker'
    COORDINATOR = 'coordinator'

@dataclass
class SwarmAgent:
    id: str
    position: Tuple[float, float]
    role: SwarmRole
    energy: float
    payload_capacity: float
    
class SwarmCoordinator:
    def __init__(self):
        self.agents: Dict[str, SwarmAgent] = {}
        self.tasks: List[Dict] = []
        self.role_distributions = {
            SwarmRole.SCOUT: 0.2,
            SwarmRole.WORKER: 0.7,
            SwarmRole.COORDINATOR: 0.1
        }

    def register_agent(self, agent_id: str, position: Tuple[float, float], 
                      energy: float, payload_capacity: float) -> None:
        role = self._assign_optimal_role()
        self.agents[agent_id] = SwarmAgent(
            id=agent_id,
            position=position,
            role=role,
            energy=energy,
            payload_capacity=payload_capacity
        )

    def _assign_optimal_role(self) -> SwarmRole:
        current_distribution = self._get_role_distribution()
        
        # Find the role that needs more agents
        target_role = SwarmRole.WORKER
        max_deficit = -1
        
        for role in SwarmRole:
            target_pct = self.role_distributions[role]
            current_pct = current_distribution.get(role, 0)
            deficit = target_pct - current_pct
            
            if deficit > max_deficit:
                max_deficit = deficit
                target_role = role
                
        return target_role

    def _get_role_distribution(self) -> Dict[SwarmRole, float]:
        if not self.agents:
            return {}
            
        distribution = {role: 0 for role in SwarmRole}
        total = len(self.agents)
        
        for agent in self.agents.values():
            distribution[agent.role] += 1
        
        return {role: count/total for role, count in distribution.items()}

    def optimize_task_allocation(self) -> Dict[str, List[Dict]]:
        # Group agents by role
        scouts = [a for a in self.agents.values() if a.role == SwarmRole.SCOUT]
        workers = [a for a in self.agents.values() if a.role == SwarmRole.WORKER]
        
        # Calculate task assignments using Hungarian algorithm
        cost_matrix = np.zeros((len(workers), len(self.tasks)))
        
        for i, worker in enumerate(workers):
            for j, task in enumerate(self.tasks):
                cost = self._calculate_task_cost(worker, task)
                cost_matrix[i][j] = cost
                
        # Optimize assignments
        row_ind, col_ind = self._hungarian_algorithm(cost_matrix)
        
        # Create assignment mapping
        assignments = {SwarmRole.WORKER: [], SwarmRole.SCOUT: []}
        
        for worker_idx, task_idx in zip(row_ind, col_ind):
            worker = workers[worker_idx]
            task = self.tasks[task_idx]
            assignments[SwarmRole.WORKER].append({
                'agent_id': worker.id,
                'task': task
            })
            
        # Assign exploration zones to scouts
        for scout in scouts:
            zone = self._get_exploration_zone(scout)
            assignments[SwarmRole.SCOUT].append({
                'agent_id': scout.id,
                'zone': zone
            })
            
        return assignments

    def _calculate_task_cost(self, agent: SwarmAgent, task: Dict) -> float:
        # Distance cost
        dx = agent.position[0] - task['position'][0]
        dy = agent.position[1] - task['position'][1]
        distance_cost = math.sqrt(dx*dx + dy*dy)
        
        # Energy cost
        energy_cost = task['energy_required'] / agent.energy
        
        # Payload compatibility cost
        payload_cost = task['payload_required'] / agent.payload_capacity
        
        return distance_cost + energy_cost + payload_cost

    def _hungarian_algorithm(self, cost_matrix: np.ndarray) -> Tuple[List[int], List[int]]:
        from scipy.optimize import linear_sum_assignment
        return linear_sum_assignment(cost_matrix)

    def _get_exploration_zone(self, scout: SwarmAgent) -> Dict:
        # Implement zone assignment logic based on current coverage
        return {
            'center': scout.position,
            'radius': 100.0  # Configurable exploration radius
        }

    def update_agent_status(self, agent_id: str, new_position: Tuple[float, float],
                          energy_level: float) -> None:
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.position = new_position
            agent.energy = energy_level
            
            # Trigger role reassignment if energy is critically low
            if energy_level < 0.2:  # 20% threshold
                agent.role = self._assign_optimal_role()