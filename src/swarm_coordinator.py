import random
import math

class SwarmCoordinator:
    def __init__(self, num_agents, task_locations):
        self.num_agents = num_agents
        self.task_locations = task_locations
        self.agent_positions = [(random.uniform(-100, 100), random.uniform(-100, 100)) for _ in range(num_agents)]
        self.agent_tasks = [[] for _ in range(num_agents)]

    def allocate_tasks(self):
        tasks_remaining = list(self.task_locations.keys())
        random.shuffle(tasks_remaining)

        for task in tasks_remaining:
            min_distance = float('inf')
            best_agent = None
            for i, agent_pos in enumerate(self.agent_positions):
                distance = math.sqrt((agent_pos[0] - self.task_locations[task][0])**2 + (agent_pos[1] - self.task_locations[task][1])**2)
                if distance < min_distance:
                    min_distance = distance
                    best_agent = i
            self.agent_tasks[best_agent].append(task)

    def coordinate_agents(self):
        for i, agent_pos in enumerate(self.agent_positions):
            print(f'Agent {i} is at position {agent_pos} and is assigned the following tasks: {self.agent_tasks[i]}')
            # Implement agent coordination and movement logic here
