import time
import random
from typing import List

class SwarmCoordinator:
    def __init__(self, num_agents: int):
        self.num_agents = num_agents
        self.agents = [Agent(f'Agent_{i}') for i in range(num_agents)]
        self.task_queue = []
        self.task_assignments = {}

    def add_task(self, task: dict):
        self.task_queue.append(task)
        self.schedule_tasks()

    def schedule_tasks(self):
        while self.task_queue:
            task = self.task_queue.pop(0)
            available_agents = [agent for agent in self.agents if not agent.is_busy()]
            if available_agents:
                agent = self.select_agent(available_agents)
                agent.assign_task(task)
                self.task_assignments[task['id']] = agent.name
            else:
                self.task_queue.append(task)
                time.sleep(1)

    def select_agent(self, agents: List[Agent]) -> Agent:
        # Implement a load balancing algorithm to select the best agent
        # e.g., round-robin, least-busy, etc.
        return random.choice(agents)

    def get_task_status(self, task_id: str) -> str:
        if task_id in self.task_assignments:
            agent_name = self.task_assignments[task_id]
            agent = next((a for a in self.agents if a.name == agent_name), None)
            if agent:
                return agent.get_task_status(task_id)
        return 'Unassigned'

class Agent:
    def __init__(self, name: str):
        self.name = name
        self.current_task = None
        self.start_time = 0

    def assign_task(self, task: dict):
        self.current_task = task
        self.start_time = time.time()

    def is_busy(self) -> bool:
        return self.current_task is not None

    def get_task_status(self, task_id: str) -> str:
        if self.current_task and self.current_task['id'] == task_id:
            elapsed_time = time.time() - self.start_time
            if elapsed_time >= self.current_task['duration']:
                self.current_task = None
                return 'Completed'
            else:
                return 'In Progress'
        return 'Unassigned'