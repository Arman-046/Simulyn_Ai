import json
from backend.skpi.knowledge_graph import KnowledgeNode
from backend.skpi.providers.llm import call_llm

class UncertaintyEngine:
    """
    Analyzes raw extracted knowledge and assigns quantitative uncertainty and
    qualitative explanation (reason) to each node using LLM evaluation.
    """
    
    def evaluate(self, node: KnowledgeNode, global_context: str = "") -> KnowledgeNode:
        """
        Dynamically evaluates the knowledge node's metrics and injects them back.
        Returns the mutated node.
        """
        prompt = f"""Evaluate the following piece of knowledge for a market simulation.
You MUST provide structured metrics representing uncertainty.

Knowledge Type: {node.type}
Knowledge Label: {node.label}
Source: {node.source}
Global Context: {global_context}

Provide realistic and critical evaluations. Do not default to 1.0. 
If the knowledge is highly speculative, lower the confidence and reliability.
If the knowledge is very general, lower the coverage.

Return exactly this JSON structure (all values are strictly floats 0.0 to 1.0, except reason which is a string):
{{
  "confidence": <float>,
  "reliability": <float>,
  "freshness": <float>,
  "coverage": <float>,
  "reason": "<string explaining exactly why these scores were assigned based on the source and label>"
}}
"""
        
        try:
            # We call the Fireworks LLM which returns a parsed dict (zero fake functionality)
            result = call_llm(prompt, json_mode=True)
            
            # Map the dynamically computed results to the node
            node.confidence = float(result.get("confidence", 0.5))
            node.reliability = float(result.get("reliability", 0.5))
            node.freshness = float(result.get("freshness", 0.5))
            node.coverage = float(result.get("coverage", 0.5))
            node.reason = result.get("reason", "No reason provided by LLM.")
            
        except Exception as e:
            # Fallback only when LLM fails entirely (e.g. timeout or auth issue)
            print(f"[UncertaintyEngine] Error evaluating node {node.id}: {e}")
            node.confidence = 0.5
            node.reliability = 0.5
            node.freshness = 0.5
            node.coverage = 0.5
            node.reason = "Fallback due to LLM failure: " + str(e)
            
        return node

    def evaluate_batch(self, nodes: list[KnowledgeNode], global_context: str = "") -> list[KnowledgeNode]:
        """
        Convenience method to evaluate a list of nodes.
        In a production scenario, this could be batched into a single LLM call for efficiency.
        """
        evaluated_nodes = []
        for node in nodes:
            evaluated_nodes.append(self.evaluate(node, global_context))
        return evaluated_nodes
