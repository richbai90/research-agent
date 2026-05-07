import streamlit as st
import asyncio
from agent import graph

st.set_page_config(page_title="Fail-Fast Research Agent", layout="wide")

# --- Helper Functions ---


def dict_to_markdown(idea_cards: list, summary: str) -> str:
    """Converts the agent's output into a cleanly formatted Markdown document."""
    md = f"# Research Generation Summary\n\n{summary}\n\n---\n\n"

    for i, card in enumerate(idea_cards, 1):
        md += f"## Idea {i}: {card.get('title', 'Untitled')}\n\n"
        md += f"**Hypothesis:** {card.get('hypothesis', '')}\n\n"
        md += f"**Novelty Claim:** {card.get('novelty_claim', '')}\n\n"
        md += f"**Why It Matters:** {card.get('why_it_matters', '')}\n\n"
        md += f"**Differentiator:** {card.get('differentiator', '')}\n\n"

        md += "### Key Assumptions\n"
        for assumption in card.get("key_assumptions", []):
            md += f"- {assumption}\n"

        md += "\n### Failure Modes\n"
        for failure in card.get("failure_modes", []):
            md += f"- {failure}\n"

        md += f"\n### Experimental Details\n{card.get('experimental_details', '')}\n\n"
        md += f"### Refinement Process\n- {card.get('refinement_process', '')}\n\n"
        md += f"### Stop / Pivot Rules\n{card.get('stop_pivot_rules', '')}\n\n"

        md += "### Week One Plan\n"
        for step in card.get("week_one_plan", []):
            md += f"- {step}\n"

        md += "\n### Relevant Sources\n"
        for source in card.get("relevant_sources", []):
            md += f"- {source}\n"
        md += f"\n### Risk Assessment\n{card.get('risk_assessment', '')}\n\n"
        md += "---\n\n"

    return md


async def run_agent_async(initial_state: dict, status_container):
    """Executes the async LangGraph and updates the UI with progress."""
    # Keep a running dictionary of the complete state so we don't drop the idea_cards
    full_state = initial_state.copy()

    async for chunk in graph.astream(initial_state):
        for node, values in chunk.items():
            # Accumulate the state deltas
            full_state.update(values)

            status_container.info(f"✅ Completed step: **{node.capitalize()}**")

            if node == "orchestrate":
                decision = values.get("status")
                feedback = values.get("feedback", "")

                if decision == "loop":
                    status_container.warning(
                        f"🔄 Orchestrator triggered a loop. Refining ideas..."
                    )
                    # Tie the expander to the status container so it stays in visual sequence
                    with status_container.expander(
                        "Orchestrator Feedback", expanded=False
                    ):
                        st.write(feedback)
                elif decision == "final":
                    if "STATUS: FAIL" in feedback:
                        status_container.error(
                            "⚠️ Max iterations reached. Orchestrator forced an exit with the best available attempt."
                        )
                    else:
                        status_container.success("🎯 Orchestrator approved the ideas.")

    return full_state


# --- UI Layout ---

st.title("🔬 Fail-Fast Research Agent")
st.markdown(
    "Generate novel, rapidly-testable research ideas backed by Scite.ai literature analysis."
)

with st.sidebar:
    st.header("Experiment Settings")
    domain = st.text_area(
        "Domain / Area",
        value="Neuromorphic sensor data processing for orbital debris tracking",
    )
    target_count = st.number_input(
        "Target Output Count", min_value=1, max_value=10, value=3
    )
    time_horizon = st.selectbox(
        "Time Horizon for Killer Test", ["2 hours", "1 day", "1 week", "1 month"]
    )

    st.subheader("Resource Boundaries")
    hardware = st.text_input(
        "Hardware Access", value="Single local GPU (RTX 4090), No cluster access"
    )
    simulation = st.text_input("Simulation/EDA Access", value="Python/PyTorch, OpenEB")

    run_button = st.button("Generate Ideas", type="primary", use_container_width=True)

if run_button:
    if not domain:
        st.error("Please enter a research domain.")
        st.stop()

    initial_state = {
        "domain": domain,
        "settings": {
            "TARGET OUTPUT COUNT": target_count,
            "TIME HORIZON FOR KILLER TEST": time_horizon,
            "RESOURCE BOUNDARY": f"Hardware: {hardware} | Simulation: {simulation}",
        },
        "iteration": 0,
        "status": "continue",
    }

    st.divider()
    status_container = st.container()

    with st.spinner("Initializing Research Agent..."):
        final_state = asyncio.run(run_agent_async(initial_state, status_container))

    if final_state and "idea_cards" in final_state:
        st.subheader("Generated Idea Cards")

        st.info(final_state.get("feedback", "No orchestrator summary provided."))

        # Display Cards in Accordions
        for i, card in enumerate(final_state["idea_cards"], 1):
            with st.expander(
                f"Idea {i}: {card.get('title', 'Untitled')}", expanded=True
            ):
                st.write(f"**Hypothesis:** {card.get('hypothesis')}")
                st.write(f"**Test:** {card.get('experimental_details')}")
                st.write(f"**Refinement:** {card.get('refinement_process')}")
                if card.get("relevant_sources"):
                    st.write("**Sources:**")
                    for source in card["relevant_sources"]:
                        st.markdown(f"- {source}")

        md_text = dict_to_markdown(
            final_state["idea_cards"], final_state.get("feedback", "")
        )

        st.divider()
        st.download_button(
            label="📥 Export to Markdown",
            data=md_text,
            file_name=f"research_ideas_{domain[:15].replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    else:
        st.error(
            "Failed to extract Idea Cards from the graph execution. Please check the terminal logs."
        )
