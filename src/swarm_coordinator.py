import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

class SwarmNodeStatus(Enum):
    ACTIVE = 'active'
    DEGRADED = 'degraded'
    OFFLINE = 'offline'

@dataclass
class SwarmNode:
    id: str
    status: SwarmNodeStatus
    load: float
    last_heartbeat: float
    capabilities: List[str]

class SwarmCoordinator:
    def __init__(self):
        self.nodes: Dict[str, SwarmNode] = {}
        self.min_nodes = 3
        self.load_threshold = 0.8
        self.heartbeat_timeout = 30.0
        self.logger = logging.getLogger(__name__)

    async def register_node(self, node_id: str, capabilities: List[str]) -> bool:
        if node_id in self.nodes:
            return False
        
        self.nodes[node_id] = SwarmNode(
            id=node_id,
            status=SwarmNodeStatus.ACTIVE,
            load=0.0,
            last_heartbeat=asyncio.get_event_loop().time(),
            capabilities=capabilities
        )
        self.logger.info(f'Node {node_id} registered with capabilities {capabilities}')
        return True

    async def update_node_status(self, node_id: str, load: float) -> None:
        if node_id not in self.nodes:
            return

        node = self.nodes[node_id]
        node.load = load
        node.last_heartbeat = asyncio.get_event_loop().time()

        if load > self.load_threshold:
            node.status = SwarmNodeStatus.DEGRADED
            await self.rebalance_load()

    async def rebalance_load(self) -> None:
        active_nodes = [n for n in self.nodes.values() 
                       if n.status == SwarmNodeStatus.ACTIVE]
        
        if not active_nodes:
            self.logger.error('No active nodes available for load balancing')
            return

        total_load = sum(n.load for n in active_nodes)
        target_load = total_load / len(active_nodes)

        for node in active_nodes:
            if node.load > target_load * 1.2:  # 20% above target
                await self.migrate_tasks(node, target_load)

    async def migrate_tasks(self, overloaded_node: SwarmNode, target_load: float) -> None:
        candidates = [
            n for n in self.nodes.values()
            if n.status == SwarmNodeStatus.ACTIVE 
            and n.load < target_load
            and n.id != overloaded_node.id
        ]

        if not candidates:
            return

        # Sort by current load ascending
        candidates.sort(key=lambda x: x.load)
        
        excess_load = overloaded_node.load - target_load
        self.logger.info(f'Migrating {excess_load:.2f} load from {overloaded_node.id}')

    async def monitor_health(self) -> None:
        while True:
            current_time = asyncio.get_event_loop().time()
            
            for node_id, node in list(self.nodes.items()):
                if current_time - node.last_heartbeat > self.heartbeat_timeout:
                    node.status = SwarmNodeStatus.OFFLINE
                    self.logger.warning(f'Node {node_id} marked as offline')
                    
                    if len([n for n in self.nodes.values() 
                           if n.status == SwarmNodeStatus.ACTIVE]) < self.min_nodes:
                        self.logger.error('Swarm below minimum node threshold!')

            await asyncio.sleep(5)

    def get_best_node(self, required_capabilities: List[str]) -> Optional[SwarmNode]:
        candidates = [
            n for n in self.nodes.values()
            if n.status == SwarmNodeStatus.ACTIVE
            and all(cap in n.capabilities for cap in required_capabilities)
        ]

        if not candidates:
            return None

        return min(candidates, key=lambda x: x.load)
