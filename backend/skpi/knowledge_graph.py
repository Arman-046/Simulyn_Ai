import uuid
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Relationship(BaseModel):
    target_id: str
    relation_type: str
    weight: float = 1.0

class KnowledgeNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str  # e.g., "Company", "Product", "Industry", "Competitors", "Assumptions", "Unknowns", etc.
    label: str # The value of the node, e.g., "Apple", "Smartphones", "$999"
    source: str # e.g., "User Input", "LLM Extraction", "News API"
    
    # Injected by UncertaintyEngine
    confidence: Optional[float] = None
    reliability: Optional[float] = None
    freshness: Optional[float] = None
    coverage: Optional[float] = None
    reason: Optional[str] = None
    
    relationships: List[Relationship] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def add_relationship(self, target_id: str, relation_type: str, weight: float = 1.0):
        self.relationships.append(Relationship(
            target_id=target_id,
            relation_type=relation_type,
            weight=weight
        ))

class KnowledgeGraph(BaseModel):
    nodes: Dict[str, KnowledgeNode] = Field(default_factory=dict)
    
    def add_node(self, node: KnowledgeNode):
        self.nodes[node.id] = node
        
    def add_relationship(self, source_id: str, target_id: str, relation_type: str, weight: float = 1.0):
        if source_id in self.nodes and target_id in self.nodes:
            self.nodes[source_id].add_relationship(target_id, relation_type, weight)
        else:
            raise ValueError(f"Both source ({source_id}) and target ({target_id}) nodes must exist in the graph.")
            
    def get_nodes_by_type(self, type_str: str) -> List[KnowledgeNode]:
        return [n for n in self.nodes.values() if n.type == type_str]
        
    def get_node_by_label(self, label: str) -> Optional[KnowledgeNode]:
        for n in self.nodes.values():
            if n.label == label:
                return n
        return None
        
    def to_dict(self) -> dict:
        return self.model_dump()
