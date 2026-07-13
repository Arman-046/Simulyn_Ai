import json
from backend.skpi.knowledge_graph import KnowledgeGraph, KnowledgeNode
from backend.skpi.uncertainty_engine import UncertaintyEngine

def run_tests():
    print("--- 1. Testing KnowledgeGraph ---")
    graph = KnowledgeGraph()
    
    # Create some mock nodes
    node1 = KnowledgeNode(type="Company", label="SimulynTech", source="User Input")
    node2 = KnowledgeNode(type="Product", label="Simulyn Edge Device", source="User Input")
    node3 = KnowledgeNode(type="Economy", label="Recession looming", source="Market Extraction")
    
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)
    
    # Create a relationship
    graph.add_relationship(source_id=node2.id, target_id=node1.id, relation_type="MANUFACTURED_BY", weight=1.0)
    graph.add_relationship(source_id=node2.id, target_id=node3.id, relation_type="IMPACTED_BY", weight=0.8)
    
    print(f"Graph Nodes Count: {len(graph.nodes)}")
    assert len(graph.nodes) == 3
    
    # Retrieve by type
    products = graph.get_nodes_by_type("Product")
    assert len(products) == 1
    assert products[0].label == "Simulyn Edge Device"
    
    print("KnowledgeGraph: Basic structure and relationship testing passed.\n")
    
    print("--- 2. Testing UncertaintyEngine ---")
    # For testing, we use the real LLM endpoint (which requires FIREWORKS_API_KEY to be set in .env)
    # The integration should automatically pick it up via backend.config
    engine = UncertaintyEngine()
    
    global_context = "A startup is launching a high-end edge AI device during a mild economic downturn."
    
    print(f"Evaluating node: {node3.label} (Source: {node3.source})")
    evaluated_node = engine.evaluate(node3, global_context=global_context)
    
    print("Evaluation Results:")
    print(f"  Confidence:  {evaluated_node.confidence}")
    print(f"  Reliability: {evaluated_node.reliability}")
    print(f"  Freshness:   {evaluated_node.freshness}")
    print(f"  Coverage:    {evaluated_node.coverage}")
    print(f"  Reason:      {evaluated_node.reason}")
    
    assert evaluated_node.confidence is not None
    assert evaluated_node.reason is not None
    
    print("\n--- 3. Sample JSON Output ---")
    print(json.dumps(graph.to_dict(), indent=2))

if __name__ == "__main__":
    run_tests()
