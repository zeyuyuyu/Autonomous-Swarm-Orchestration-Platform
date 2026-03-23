import random
import time

class SwarmCoordinator:
    def __init__(self, swarm_size=10):
        self.swarm_size = swarm_size
        self.swarm = [self.create_agent() for _ in range(swarm_size)]
        self.load_balancer = LoadBalancer(self.swarm)

    def create_agent(self):
        return Agent()

    def monitor_swarm(self):
        while True:
            for agent in self.swarm:
                if not agent.is_healthy():
                    self.load_balancer.replace_agent(agent)
            time.sleep(60)  # Check swarm health every minute

    def execute_task(self, task):
        available_agents = self.load_balancer.get_available_agents()
        if available_agents:
            agent = random.choice(available_agents)
            agent.execute_task(task)
        else:
            print("No available agents to execute the task.")

class Agent:
    def __init__(self):
        self.health = 100

    def is_healthy(self):
        return self.health > 0

    def execute_task(self, task):
        print(f"Agent executing task: {task}")
        self.health -= random.randint(10, 30)  # Simulating task impact on agent health

class LoadBalancer:
    def __init__(self, swarm):
        self.swarm = swarm

    def get_available_agents(self):
        return [agent for agent in self.swarm if agent.is_healthy()]

    def replace_agent(self, unhealthy_agent):
        print(f"Replacing unhealthy agent: {unhealthy_agent}")
        index = self.swarm.index(unhealthy_agent)
        self.swarm[index] = self.create_new_agent()

    def create_new_agent(self):
        return Agent()