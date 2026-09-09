"""
Wires the nodes into a LangGraph StateGraph.

Flow:
    research -> identify_opportunities -> map_solutions -> generate_report -> send_email

Each node is defensive: if a step fails or comes back empty, it records the
error in state and downstream nodes degrade gracefully (e.g. an empty
opportunities list produces a thin report rather than crashing).
"""
from langgraph.graph import StateGraph, END

from proposal_iq.state import AgentState
from proposal_iq.tools.opportunities import identify_opportunities
from proposal_iq.tools.solutions import map_solutions
from proposal_iq.tools.report import generate_report, markdown_to_simple_html
from proposal_iq.tools.email_sender import send_report_email
from proposal_iq.tools.research import research_company, sections_to_text

def _append_error(state: AgentState, message: str | None) -> list[str]:
    errors = list(state.get("errors", []))
    if message:
        errors.append(message)
    return errors


def node_research(state: AgentState) -> dict:
    result = research_company(state["company_url"], state["company_name"])
    return {
         "research_sections": result["research_sections"],
        "research_sources": result["research_sources"],
        "errors": _append_error(state, result["error"]),
    }


def node_identify_opportunities(state: AgentState) -> dict:
    research_text = sections_to_text(state.get("research_sections", []))
    result = identify_opportunities(state["company_name"], research_text) 
    return {
        "opportunities": result["opportunities"],
        "errors": _append_error(state, result["error"]),
    }


def node_map_solutions(state: AgentState) -> dict:
    result = map_solutions(state.get("opportunities", []))
    return {
        "mapped_solutions": result["mapped_solutions"],
        "errors": _append_error(state, result["error"]),
    }


def node_generate_report(state: AgentState) -> dict:
    markdown_report = generate_report(
        company_name=state["company_name"],
        contact_name=state.get("contact_name", ""),
        research_notes=sections_to_text(state.get("research_sections", [])),  
        opportunities=state.get("opportunities", []),
        mapped_solutions=state.get("mapped_solutions", []),
    )
    return {
        "report_markdown": markdown_report,
        "report_html": markdown_to_simple_html(markdown_report),
    }


def node_send_email(state: AgentState) -> dict:
    result = send_report_email(
        to_email=state["contact_email"],
        company_name=state["company_name"],
        report_html=state.get("report_html", ""),
    )
    return {
        "email_sent": result["sent"],
        "email_error": result["error"],
        "errors": _append_error(state, result["error"]),
    }


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("research", node_research)
    graph.add_node("identify_opportunities", node_identify_opportunities)
    graph.add_node("map_solutions", node_map_solutions)
    graph.add_node("generate_report", node_generate_report)
    graph.add_node("send_email", node_send_email)

    graph.set_entry_point("research")
    graph.add_edge("research", "identify_opportunities")
    graph.add_edge("identify_opportunities", "map_solutions")
    graph.add_edge("map_solutions", "generate_report")
    graph.add_edge("generate_report", "send_email")
    graph.add_edge("send_email", END)

    return graph.compile()
