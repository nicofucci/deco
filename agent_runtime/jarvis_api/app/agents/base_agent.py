"""
Base Agent Framework for Autonomous AI Agents
Provides LLM integration, tool execution, memory, and decision-making patterns.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import json

from app.services.ollama_client import JarvisOllamaClient

logger = logging.getLogger(__name__)


class Tool:
    """Represents an executable tool available to agents."""
    
    def __init__(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: Dict[str, Any]
    ):
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters


class AgentMemory:
    """Simple in-memory storage for agent session context."""
    
    def __init__(self):
        self.observations: List[str] = []
        self.actions: List[Dict[str, Any]] = []
        self.reflections: List[str] = []
    
    def add_observation(self, observation: str):
        self.observations.append(observation)
    
    def add_action(self, action: Dict[str, Any]):
        self.actions.append(action)
    
    def add_reflection(self, reflection: str):
        self.reflections.append(reflection)
    
    def get_context(self) -> str:
        """Returns formatted context for LLM."""
        context = "## Agent Memory\n\n"
        
        if self.observations:
            context += "### Observations:\n"
            for i, obs in enumerate(self.observations[-5:], 1):  # Last 5
                context += f"{i}. {obs}\n"
            context += "\n"
        
        if self.actions:
            context += "### Actions Taken:\n"
            for i, action in enumerate(self.actions[-5:], 1):
                context += f"{i}. {action.get('tool', 'unknown')}: {action.get('summary', 'N/A')}\n"
            context += "\n"
        
        if self.reflections:
            context += "### Reflections:\n"
            for i, ref in enumerate(self.reflections[-3:], 1):
                context += f"{i}. {ref}\n"
        
        return context


class BaseAgent(ABC):
    """
    Abstract base class for all autonomous AI agents.
    
    Implements Plan → Execute → Reflect loop with LLM reasoning.
    """
    
    def __init__(self, agent_id: str, ollama_client: Optional[JarvisOllamaClient] = None):
        self.agent_id = agent_id
        self.ollama = ollama_client or JarvisOllamaClient()
        self.memory = AgentMemory()
        self.tools: Dict[str, Tool] = {}
        self.max_iterations = 10
        self.current_iteration = 0
        
        # Register tools specific to this agent
        self._register_tools()
    
    @abstractmethod
    def _register_tools(self):
        """Subclasses must implement to register their specific tools."""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Returns the system prompt defining agent behavior."""
        pass
    
    def register_tool(self, tool: Tool):
        """Register a tool for this agent."""
        self.tools[tool.name] = tool
        logger.info(f"[{self.agent_id}] Registered tool: {tool.name}")
    
    async def plan(self, objective: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to create an execution plan.
        
        Returns:
            Dict with 'steps', 'reasoning', and 'confidence'
        """
        system_prompt = self.get_system_prompt()
        
        # Build planning prompt
        tools_desc = "\n".join([
            f"- **{name}**: {tool.description}"
            for name, tool in self.tools.items()
        ])
        
        memory_context = self.memory.get_context()
        
        user_prompt = f"""
**Objective:** {objective}

**Available Tools:**
{tools_desc}

**Context:**
{json.dumps(context, indent=2)}

{memory_context}

Please analyze the objective and create a step-by-step execution plan. For each step, specify:
1. Tool to use
2. Parameters for that tool
3. Expected outcome

Respond in JSON format:
{{
    "reasoning": "Your analysis of the situation",
    "steps": [
        {{"step": 1, "tool": "tool_name", "params": {{}}, "goal": "what this accomplishes"}},
        ...
    ],
    "confidence": 0.85
}}
"""
        
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.ollama.chat(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    model="llama3.1:8b-instruct-q4_K_M"
                )
            )
            
            if "error" in response:
                raise Exception(f"LLM error: {response['error']}")
            
            content = response.get("message", {}).get("content", "")
            
            # Try to extract JSON from response
            # LLMs sometimes wrap JSON in markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            plan = json.loads(content)
            self.memory.add_reflection(f"Created plan: {plan.get('reasoning', 'N/A')}")
            
            return plan
            
        except Exception as e:
            logger.error(f"[{self.agent_id}] Planning failed: {e}")
            # Fallback to a simple plan
            return {
                "reasoning": f"Unable to create detailed plan due to error: {e}",
                "steps": [],
                "confidence": 0.0
            }
    
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a registered tool with given parameters."""
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "output": None
            }
        
        tool = self.tools[tool_name]
        
        try:
            logger.info(f"[{self.agent_id}] Executing tool: {tool_name} with params: {params}")
            
            # Execute the tool function
            result = await tool.function(**params)
            
            action_record = {
                "tool": tool_name,
                "params": params,
                "summary": f"Executed {tool_name}",
                "timestamp": datetime.now().isoformat()
            }
            self.memory.add_action(action_record)
            
            return {
                "success": True,
                "tool": tool_name,
                "output": result
            }
            
        except Exception as e:
            logger.error(f"[{self.agent_id}] Tool execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name,
                "output": None
            }
    
    async def reflect(self, execution_results: List[Dict[str, Any]]) -> str:
        """
        Use LLM to reflect on execution results and determine next action.
        
        Returns:
            Reflection text with next action recommendation
        """
        system_prompt = self.get_system_prompt()
        
        results_summary = "\n".join([
            f"Step {i+1}: Tool={r.get('tool', 'N/A')}, Success={r.get('success', False)}, Output={str(r.get('output', 'N/A'))[:200]}..."
            for i, r in enumerate(execution_results)
        ])
        
        memory_context = self.memory.get_context()
        
        user_prompt = f"""
**Execution Results:**
{results_summary}

{memory_context}

Analyze the results and provide:
1. What was learned/discovered
2. Whether the objective is accomplished
3. What should be done next (continue, stop, adjust approach)

Keep your reflection concise and actionable.
"""
        
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.ollama.chat(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    model="llama3.1:8b-instruct-q4_K_M"
                )
            )
            
            reflection = response.get("message", {}).get("content", "Unable to reflect on results.")
            self.memory.add_reflection(reflection)
            
            return reflection
            
        except Exception as e:
            logger.error(f"[{self.agent_id}] Reflection failed: {e}")
            return f"Reflection error: {e}"
    
    async def run(self, objective: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main execution loop: Plan → Execute → Reflect
        
        Args:
            objective: What the agent should accomplish
            context: Additional context and parameters
        
        Returns:
            Final execution results
        """
        context = context or {}
        self.current_iteration = 0
        
        logger.info(f"[{self.agent_id}] Starting autonomous execution: {objective}")
        self.memory.add_observation(f"Objective: {objective}")
        
        all_results = []
        
        while self.current_iteration < self.max_iterations:
            self.current_iteration += 1
            
            # PLAN
            plan = await self.plan(objective, context)
            
            if not plan.get("steps"):
                logger.warning(f"[{self.agent_id}] No steps in plan, stopping.")
                break
            
            # EXECUTE
            iteration_results = []
            for step in plan["steps"]:
                tool_name = step.get("tool")
                params = step.get("params", {})
                
                result = await self.execute_tool(tool_name, params)
                iteration_results.append(result)
                all_results.append(result)
                
                # If a tool fails, break this iteration
                if not result.get("success"):
                    logger.warning(f"[{self.agent_id}] Tool failed: {tool_name}")
                    break
            
            # REFLECT
            reflection = await self.reflect(iteration_results)
            
            # Check if objective is complete (simple heuristic for now)
            if "objective accomplished" in reflection.lower() or "task complete" in reflection.lower():
                logger.info(f"[{self.agent_id}] Objective accomplished!")
                break
        
        logger.info(f"[{self.agent_id}] Execution complete after {self.current_iteration} iterations")
        
        return {
            "agent_id": self.agent_id,
            "objective": objective,
            "iterations": self.current_iteration,
            "results": all_results,
            "final_reflection": self.memory.reflections[-1] if self.memory.reflections else "No reflections",
            "memory": {
                "observations": self.memory.observations,
                "actions": self.memory.actions,
                "reflections": self.memory.reflections
            }
        }
