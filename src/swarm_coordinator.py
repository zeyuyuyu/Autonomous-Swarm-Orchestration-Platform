import time
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

@dataclass
class SwarmNode:
    id: str
    ip: str
    load: float = 0.0
    last_heartbeat: float = 0.0
    status: str = 'active'

class SwarmCoordinator:
    def __init__(self):
        self.nodes: Dict[str, SwarmNode] = {}
        self.health_check_interval = 5.0  # seconds
        self.node_timeout = 15.0  # seconds
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def register_node(self, node_id: str, ip: str) -> None:
        """Register a new node in the swarm"""
        self.nodes[node_id] = SwarmNode(
            id=node_id,
            ip=ip,
            last_heartbeat=time.time()
        )
        self.logger.info(f'Node {node_id} registered with IP {ip}')

    def update_node_health(self, node_id: str, load: float) -> None:
        """Update node health metrics"""
        if node_id in self.nodes:
            self.nodes[node_id].load = load
            self.nodes[node_id].last_heartbeat = time.time()
            self.nodes[node_id].status = 'active'

    def check_node_health(self) -> List[str]:
        """Return list of failed nodes"""
        current_time = time.time()
        failed_nodes = []

        for node_id, node in self.nodes.items():
            if current_time - node.last_heartbeat > self.node_timeout:
                node.status = 'failed'
                failed_nodes.append(node_id)
                self.logger.warning(f'Node {node_id} appears to be down')

        return failed_nodes

    def get_optimal_node(self) -> Optional[SwarmNode]:
        """Return node with lowest load for task assignment"""
        active_nodes = [
            node for node in self.nodes.values()
            if node.status == 'active'
        ]
        
        if not active_nodes:
            return None
            
        return min(active_nodes, key=lambda x: x.load)

    def rebalance_load(self) -> Dict[str, List[str]]:
        """Redistribute tasks from heavily loaded nodes"""
        migrations = {}
        high_load_threshold = 0.8

        # Find overloaded nodes
        overloaded = [
            node for node in self.nodes.values()
            if node.status == 'active' and node.load > high_load_threshold
        ]

        # Find available capacity
        available = [
            node for node in self.nodes.values()
            if node.status == 'active' and node.load < high_load_threshold
        ]

        for source in overloaded:
            if not available:
                break
                
            target = min(available, key=lambda x: x.load)
            migrations[source.id] = [target.id]
            
            # Update theoretical loads
            load_to_move = (source.load - high_load_threshold) / 2
            source.load -= load_to_move
            target.load += load_to_move

        return migrations

    def get_swarm_status(self) -> Dict[str, dict]:
        """Return current status of all nodes"""
        return {
            node_id: {
                'ip': node.ip,
                'load': node.load,
                'status': node.status,
                'last_heartbeat': node.last_heartbeat
            }
            for node_id, node in self.nodes.items()
        }