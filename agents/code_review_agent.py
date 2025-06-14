"""
AI Agent for Autonomous Code Review.

This module implements a LangGraph-based AI agent that can autonomously
perform code review tasks using multiple tools and reasoning patterns.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from datetime import datetime

from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field

from .tools import AgentTools
from providers.model_registry import ModelRegistry

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State for the code review agent."""

    messages: Annotated[List[Any], "The conversation messages"]
    code: str
    language: str
    model_id: str
    user_request: str
    analysis_results: List[Dict[str, Any]]
    next_action: Optional[str]
    reasoning: str
    final_response: Optional[str]
    iteration_count: int


class CodeReviewRequest(BaseModel):
    """Request schema for the code review agent."""

    code: str = Field(description="Code to review")
    language: str = Field(default="python", description="Programming language")
    model_id: str = Field(default="gpt-4", description="LLM model to use")
    user_request: str = Field(
        default="Perform a comprehensive code review",
        description="Specific user request or focus area",
    )
    max_iterations: int = Field(default=5, description="Maximum reasoning iterations")


class CodeReviewAgent:
    """
    LangGraph-based AI agent for autonomous code review.

    This agent uses the ReAct pattern (Reason, Act, Observe) to:
    1. Analyze the code and user request
    2. Decide which tools to use (RAG, traditional, comparison, etc.)
    3. Execute the chosen approach
    4. Provide comprehensive results
    """

    def __init__(self, model_id: str = "gpt-4"):
        """
        Initialize the code review agent.

        Args:
            model_id: Default LLM model to use
        """
        self.model_id = model_id
        self.tools = AgentTools()
        self.model_registry = ModelRegistry()

        # Initialize the LLM
        self.llm = self._create_llm(model_id)

        # Create the agent workflow
        self.workflow = self._create_workflow()

        logger.info(f"CodeReviewAgent initialized with model: {model_id}")

    def _create_llm(self, model_id: str):
        """Create LLM instance based on model ID."""
        try:
            # Use the existing model registry
            return self.model_registry.create_model(model_id)
        except Exception as e:
            logger.warning(
                f"Failed to create model {model_id}, falling back to GPT-4: {str(e)}"
            )
            return ChatOpenAI(
                model="gpt-4",
                temperature=0.1,
                openai_api_key=os.getenv("OPENAI_API_KEY"),
            )

    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for the agent."""

        # Create tool node
        tool_node = ToolNode(self.tools.get_all_tools())

        # Create the workflow graph
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("analyzer", self._analyze_request)
        workflow.add_node("reasoner", self._reason_and_plan)
        workflow.add_node("tool_executor", tool_node)
        workflow.add_node("synthesizer", self._synthesize_results)

        # Define the workflow edges
        workflow.set_entry_point("analyzer")

        workflow.add_edge("analyzer", "reasoner")
        workflow.add_conditional_edges(
            "reasoner",
            self._should_use_tools,
            {
                "use_tools": "tool_executor",
                "synthesize": "synthesizer",
                "continue_reasoning": "reasoner",
            },
        )
        workflow.add_edge("tool_executor", "reasoner")
        workflow.add_edge("synthesizer", END)

        return workflow.compile()

    def _analyze_request(self, state: AgentState) -> AgentState:
        """Analyze the incoming code review request."""
        try:
            logger.info("Analyzing code review request...")

            analysis_prompt = f"""
            Analyze this code review request and determine the best approach:
            
            CODE:
            ```{state['language']}
            {state['code']}
            ```
            
            USER REQUEST: {state['user_request']}
            LANGUAGE: {state['language']}
            
            Based on the code and request, determine:
            1. What type of review is most appropriate (RAG-enhanced, traditional, comparative)
            2. What specific aspects to focus on (security, performance, style, etc.)
            3. What information might be needed from the knowledge base
            4. The complexity level of the code
            
            Respond with your analysis and initial plan.
            """

            messages = [
                SystemMessage(
                    content="You are an expert code review strategist. Analyze requests and plan the best review approach."
                ),
                HumanMessage(content=analysis_prompt),
            ]

            response = self.llm.invoke(messages)

            state["messages"] = messages + [response]
            state["reasoning"] = f"Initial analysis: {response.content}"
            state["iteration_count"] = 1

            logger.info("Request analysis completed")
            return state

        except Exception as e:
            logger.error(f"Error in analysis: {str(e)}")
            state["reasoning"] = f"Analysis failed: {str(e)}"
            return state

    def _reason_and_plan(self, state: AgentState) -> AgentState:
        """Reason about the current state and plan next actions."""
        try:
            logger.info(f"Reasoning iteration {state['iteration_count']}")

            # Build context from previous results
            context = self._build_reasoning_context(state)

            reasoning_prompt = f"""
            Current context:
            {context}
            
            Based on the analysis and any previous tool results, decide what to do next:
            
            Available tools:
            - rag_code_review: RAG-enhanced review with guidelines
            - traditional_code_review: Standard LLM review
            - search_guidelines: Search for specific guidelines
            - compare_review_approaches: Compare different review methods
            - get_knowledge_base_stats: Check RAG system status
            
            Decide:
            1. Should I use a tool? If so, which one and with what parameters?
            2. Do I have enough information to provide a final response?
            3. What specific action should I take next?
            
            Respond with your reasoning and the action to take.
            Format your response as:
            REASONING: [your thought process]
            ACTION: [tool_name with parameters OR "synthesize" if ready to conclude]
            """

            messages = state["messages"] + [HumanMessage(content=reasoning_prompt)]
            response = self.llm.invoke(messages)

            # Parse the response to extract action
            action = self._parse_action(response.content)

            state["messages"] = messages + [response]
            state[
                "reasoning"
            ] += f"\n\nIteration {state['iteration_count']}: {response.content}"
            state["next_action"] = action
            state["iteration_count"] += 1

            logger.info(f"Planned action: {action}")
            return state

        except Exception as e:
            logger.error(f"Error in reasoning: {str(e)}")
            state["next_action"] = "synthesize"
            return state

    def _should_use_tools(self, state: AgentState) -> str:
        """Decide whether to use tools, continue reasoning, or synthesize."""
        action = state.get("next_action", "synthesize")

        # Check iteration limit
        if state["iteration_count"] > 5:
            logger.warning("Max iterations reached, moving to synthesis")
            return "synthesize"

        if action == "synthesize":
            return "synthesize"
        elif action.startswith("tool:"):
            # Set up tool invocation
            tool_call = action.replace("tool:", "")
            state["messages"].append(HumanMessage(content=tool_call))
            return "use_tools"
        else:
            return "continue_reasoning"

    def _synthesize_results(self, state: AgentState) -> AgentState:
        """Synthesize all results into a final comprehensive response."""
        try:
            logger.info("Synthesizing final results...")

            synthesis_prompt = f"""
            Based on all the analysis and tool results, provide a comprehensive code review response:
            
            ORIGINAL REQUEST: {state['user_request']}
            CODE LANGUAGE: {state['language']}
            
            ANALYSIS RESULTS:
            {json.dumps(state.get('analysis_results', []), indent=2)}
            
            REASONING PROCESS:
            {state['reasoning']}
            
            Provide a final, comprehensive code review that:
            1. Summarizes the key findings
            2. Highlights the most important issues and suggestions
            3. Explains the review approach taken
            4. Provides actionable recommendations
            5. Notes any limitations or areas for further investigation
            
            Format as a professional code review report.
            """

            messages = [
                SystemMessage(
                    content="You are an expert code reviewer providing final comprehensive analysis."
                ),
                HumanMessage(content=synthesis_prompt),
            ]

            response = self.llm.invoke(messages)

            state["final_response"] = response.content
            state["messages"] = state["messages"] + messages + [response]

            logger.info("Results synthesis completed")
            return state

        except Exception as e:
            logger.error(f"Error in synthesis: {str(e)}")
            state["final_response"] = f"Error synthesizing results: {str(e)}"
            return state

    def _build_reasoning_context(self, state: AgentState) -> str:
        """Build context string for reasoning."""
        context_parts = [
            f"User Request: {state['user_request']}",
            f"Language: {state['language']}",
            f"Iteration: {state['iteration_count']}",
        ]

        if state.get("analysis_results"):
            context_parts.append(
                f"Previous Results: {len(state['analysis_results'])} tool executions"
            )

        return "\n".join(context_parts)

    def _parse_action(self, response_content: str) -> str:
        """Parse the action from the LLM response."""
        try:
            # Look for ACTION: line
            lines = response_content.split("\n")
            for line in lines:
                if line.strip().upper().startswith("ACTION:"):
                    action = line.split(":", 1)[1].strip()
                    return action

            # Fallback: look for tool names
            tools = [
                "rag_code_review",
                "traditional_code_review",
                "search_guidelines",
                "compare_review_approaches",
                "get_knowledge_base_stats",
            ]

            for tool in tools:
                if tool in response_content:
                    return f"tool:{tool}"

            return "synthesize"

        except Exception as e:
            logger.error(f"Error parsing action: {str(e)}")
            return "synthesize"

    async def review_code(self, request: CodeReviewRequest) -> Dict[str, Any]:
        """
        Perform autonomous code review using the agent workflow.

        Args:
            request: Code review request with code, language, and preferences

        Returns:
            Comprehensive code review results
        """
        try:
            logger.info(f"Starting autonomous code review for {request.language} code")

            # Initialize state
            initial_state = AgentState(
                messages=[],
                code=request.code,
                language=request.language,
                model_id=request.model_id,
                user_request=request.user_request,
                analysis_results=[],
                next_action=None,
                reasoning="",
                final_response=None,
                iteration_count=0,
            )

            # Run the workflow
            result = await self.workflow.ainvoke(initial_state)

            # Format the response
            response = {
                "request": {
                    "language": request.language,
                    "model_id": request.model_id,
                    "user_request": request.user_request,
                },
                "agent_analysis": {
                    "iterations": result["iteration_count"],
                    "reasoning_process": result["reasoning"],
                    "tools_used": len(result.get("analysis_results", [])),
                },
                "review_results": result["final_response"],
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "agent_version": "1.0",
                    "workflow_complete": result["final_response"] is not None,
                },
            }

            logger.info("Autonomous code review completed successfully")
            return response

        except Exception as e:
            logger.error(f"Error in autonomous code review: {str(e)}")
            return {
                "error": f"Agent review failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "fallback_recommendation": "Try traditional or RAG review directly",
            }

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agent and its capabilities."""
        return {
            "agent_type": "CodeReviewAgent",
            "model_id": self.model_id,
            "capabilities": [
                "Autonomous code analysis",
                "Multi-tool coordination",
                "RAG-enhanced reviews",
                "Comparative analysis",
                "Adaptive reasoning",
            ],
            "available_tools": self.tools.get_tool_descriptions(),
            "workflow_nodes": ["analyzer", "reasoner", "tool_executor", "synthesizer"],
            "max_iterations": 5,
        }
