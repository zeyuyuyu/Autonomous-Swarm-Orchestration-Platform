import numpy as np

class SwarmCoordinator:
    def __init__(self, swarm_size, env_dimensions):
        self.swarm_size = swarm_size
        self.env_dimensions = env_dimensions
        self.swarm_positions = np.random.uniform(0, env_dimensions, (swarm_size, 2))
        self.swarm_velocities = np.random.uniform(-1, 1, (swarm_size, 2))
        self.obstacle_positions = []
        self.obstacle_radii = []

    def update_swarm(self, dt):
        """Update the positions and velocities of the swarm agents."""
        self.swarm_positions += self.swarm_velocities * dt
        self.swarm_positions = np.clip(self.swarm_positions, 0, self.env_dimensions)
        self.avoid_obstacles()
        self.maintain_cohesion()
        self.avoid_collisions()
        self.align_velocities()

    def avoid_obstacles(self):
        """Adjust the velocities of the swarm agents to avoid obstacles."""
        for i in range(self.swarm_size):
            for j in range(len(self.obstacle_positions)):
                distance = np.linalg.norm(self.swarm_positions[i] - self.obstacle_positions[j])
                if distance < self.obstacle_radii[j]:
                    self.swarm_velocities[i] -= (self.swarm_positions[i] - self.obstacle_positions[j]) / distance

    def maintain_cohesion(self):
        """Adjust the velocities of the swarm agents to maintain cohesion."""
        center_of_mass = np.mean(self.swarm_positions, axis=0)
        for i in range(self.swarm_size):
            self.swarm_velocities[i] += (center_of_mass - self.swarm_positions[i]) * 0.1

    def avoid_collisions(self):
        """Adjust the velocities of the swarm agents to avoid collisions."""
        for i in range(self.swarm_size):
            for j in range(i+1, self.swarm_size):
                distance = np.linalg.norm(self.swarm_positions[i] - self.swarm_positions[j])
                if distance < 2:
                    self.swarm_velocities[i] -= (self.swarm_positions[i] - self.swarm_positions[j]) / distance
                    self.swarm_velocities[j] += (self.swarm_positions[i] - self.swarm_positions[j]) / distance

    def align_velocities(self):
        """Adjust the velocities of the swarm agents to align with their neighbors."""
        for i in range(self.swarm_size):
            nearby_velocities = np.sum([self.swarm_velocities[j] for j in range(self.swarm_size) if np.linalg.norm(self.swarm_positions[i] - self.swarm_positions[j]) < 10], axis=0)
            self.swarm_velocities[i] = (self.swarm_velocities[i] + nearby_velocities * 0.1) / 1.1
