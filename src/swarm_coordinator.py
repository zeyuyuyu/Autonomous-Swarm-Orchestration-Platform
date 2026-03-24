import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class SwarmNode:
    id: str
    capacity: float
    current_load: float
    tasks: List[str]
    status: str

class SwarmCoordinator:
    def __init__(self):
        self.nodes: Dict[str, SwarmNode] = {}
        self.task_queue: List[str] = []
        self.load_threshold = 0.8

    async def register_node(self, node_id: str, capacity: float) -> None:
        self.nodes[node_id] = SwarmNode(
            id=node_id,
            capacity=capacity,
            current_load=0.0,
            tasks=[],
            status='active'
        )

    async def remove_node(self, node_id: str) -> None:
        if node_id in self.nodes:
            tasks_to_reassign = self.nodes[node_id].tasks
            self.task_queue.extend(tasks_to_reassign)
            del self.nodes[node_id]
            await self.rebalance_tasks()

    def get_least_loaded_node(self) -> Optional[str]:
        available_nodes = [
            (node_id, node) for node_id, node in self.nodes.items()
            if node.current_load / node.capacity < self.load_threshold
        ]
        if not available_nodes:
            return None
        return min(available_nodes, key=lambda x: x[1].current_load / x[1].capacity)[0]

    async def assign_task(self, task_id: str, load_value: float) -> bool:
        target_node = self.get_least_loaded_node()
        if not target_node:
            self.task_queue.append(task_id)
            return False

        node = self.nodes[target_node]
        node.tasks.append(task_id)
        node.current_load += load_value
        return True

    async def complete_task(self, node_id: str, task_id: str, load_value: float) -> None:
        if node_id in self.nodes:
            node = self.nodes[node_id]
            if task_id in node.tasks:
                node.tasks.remove(task_id)
                node.current_load -= load_value
                await self.rebalance_tasks()

    async def rebalance_tasks(self) -> None:
        while self.task_queue:
            task_id = self.task_queue[0]
            if await self.assign_task(task_id, 1.0):  # Assuming default load of 1.0
                self.task_queue.pop(0)
            else:
                break

    async def monitor_health(self) -> None:
        while True:
            for node_id, node in self.nodes.items():
                if node.current_load / node.capacity > 0.95:
                    print(f'Warning: Node {node_id} is approaching capacity')
            await asyncio.sleep(10)

    def get_swarm_status(self) -> Dict:
        return {
            'active_nodes': len(self.nodes),
            'pending_tasks': len(self.task_queue),
            'total_load': sum(node.current_load for node in self.nodes.values()),
            'nodes': {
                node_id: {
                    'load': node.current_load,
                    'capacity': node.capacity,
                    'task_count': len(node.tasks)
                } for node_id, node in self.nodes.items()
            }
        }
