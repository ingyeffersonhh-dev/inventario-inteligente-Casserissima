import json
import logging
from typing import Dict, Any, cast

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from mcp import ClientSession
from mcp.client.sse import sse_client

from agent.state import AgentState
from agent.llm.factory import get_llm
from agent.prompts.system_prompt import SYSTEM_PROMPT, ROUTER_PROMPT

logger = logging.getLogger(__name__)

# URL del servidor MCP
MCP_SERVER_URL = "http://localhost:8001/sse"

# --- NODOS ---

def _get_text(content) -> str:
    if isinstance(content, list):
        return " ".join([c.get("text", "") if isinstance(c, dict) else str(c) for c in content])
    return str(content)

async def router_node(state: AgentState) -> dict:
    """Clasifica la intención del mensaje del usuario."""
    if state.get("is_proactive"):
        # Si es un job programado, la intención ya viene dada
        return {"intent": state["intent"]}
        
    llm = get_llm(temperature=0.0)
    last_message = state["messages"][-1].content
    
    prompt = ROUTER_PROMPT.format(message=last_message)
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    
    intent = _get_text(response.content).strip().replace('"', '').replace("'", "")
    valid_intents = ["demand_forecast", "production_planning", "inventory_check", "schedule_job", "general_chat", "unknown"]
    
    if intent not in valid_intents:
        intent = "unknown"
        
    return {"intent": intent}


async def tool_planner_node(state: AgentState) -> dict:
    """Decide qué herramientas MCP invocar basado en la intención y extrae parámetros."""
    intent = state["intent"]
    last_message = state["messages"][-1].content
    
    # Mapeo simple de intención a herramientas (para el MVP, el LLM podría hacerlo dinámico)
    tools_to_call = []
    
    if intent == "demand_forecast":
        # Extraer producto del mensaje
        llm = get_llm()
        extract_prompt = f"Extrae el ID del producto (ej. TF-001, TC-001) del mensaje: '{last_message}'. Si no hay ID, responde SOLO 'TF-001' como default."
        res = await llm.ainvoke([HumanMessage(content=extract_prompt)])
        product_id = _get_text(res.content).strip()
        tools_to_call.append({"name": "predict_demand", "args": {"product_id": product_id}})
        
    elif intent == "production_planning":
        llm = get_llm()
        extract_prompt = f"Extrae el ID del producto del mensaje: '{last_message}'. Si no hay, responde SOLO 'TF-001'."
        res = await llm.ainvoke([HumanMessage(content=extract_prompt)])
        product_id = _get_text(res.content).strip()
        tools_to_call.append({"name": "calculate_optimal_production", "args": {"product_id": product_id}})
        
    elif intent == "inventory_check":
        tools_to_call.append({"name": "get_rop_alerts", "args": {}})
        tools_to_call.append({"name": "check_inventory", "args": {}})
        
    # TODO: schedule_job se manejará en otro nodo o directamente
        
    return {"tools_to_call": tools_to_call}


async def tool_executor_node(state: AgentState) -> dict:
    """Ejecuta las herramientas vía cliente MCP (SSE)."""
    tools = state.get("tools_to_call", [])
    if not tools:
        return {"tool_results": []}
        
    results = []
    
    # Conectar al servidor MCP por SSE
    try:
        async with sse_client(MCP_SERVER_URL) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                
                for tool in tools:
                    logger.info(f"Ejecutando tool MCP: {tool['name']}")
                    try:
                        result = await session.call_tool(tool["name"], tool.get("args", {}))
                        # Asumiendo que el resultado MCP viene en result.content[0].text
                        text_result = result.content[0].text if result.content else str(result)
                        results.append({
                            "tool": tool["name"],
                            "result": text_result
                        })
                    except Exception as e:
                        logger.error(f"Error ejecutando tool {tool['name']}: {e}")
                        results.append({
                            "tool": tool["name"],
                            "error": str(e)
                        })
    except Exception as e:
        logger.error(f"Error conectando al MCP Server: {e}")
        return {"tool_results": [{"error": f"MCP Server no disponible: {e}"}]}
        
    return {"tool_results": results}


async def responder_node(state: AgentState) -> dict:
    """Genera la respuesta final en lenguaje natural."""
    llm = get_llm(temperature=0.2)
    
    # Construir el prompt con el historial y los resultados de las herramientas
    system_msg = SystemMessage(content=SYSTEM_PROMPT)
    messages = [system_msg] + list(state["messages"])
    
    if state.get("tool_results"):
        context = "DATOS DE HERRAMIENTAS:\n"
        for res in state["tool_results"]:
            context += f"- {res['tool']}: {res.get('result', res.get('error'))}\n"
        context += "\nResponde con el dato clave primero. Máximo 1-3 frases. Sin relleno."
        
        # Añadir como un mensaje simulado del sistema
        messages.append(SystemMessage(content=context))
        
    response = await llm.ainvoke(messages)
    
    return {"messages": [response]}


# --- EDGES CONDICIONALES ---

def route_after_router(state: AgentState) -> str:
    intent = state["intent"]
    if intent in ["general_chat", "unknown"]:
        return "responder"
    return "tool_planner"


def route_after_executor(state: AgentState) -> str:
    # Podríamos añadir ResultAnalyzer, por ahora vamos directo a responder
    return "responder"


# --- BUILD GRAPH ---

workflow = StateGraph(AgentState)

workflow.add_node("router", router_node)
workflow.add_node("tool_planner", tool_planner_node)
workflow.add_node("tool_executor", tool_executor_node)
workflow.add_node("responder", responder_node)

workflow.add_edge(START, "router")
workflow.add_conditional_edges("router", route_after_router)
workflow.add_edge("tool_planner", "tool_executor")
workflow.add_conditional_edges("tool_executor", route_after_executor)
workflow.add_edge("responder", END)

# Compilar grafo
graph = workflow.compile()
