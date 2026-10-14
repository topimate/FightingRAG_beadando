
from pathlib import Path

import pandas as pd
import streamlit as st


DATA_DIR = Path("data/evaluation")

MODE_NAMES = {
    "llm_only": "LLM Only",
    "general_rag": "General RAG",
    "sport_aware_rag": "Sport-aware RAG",
}

MODE_ORDER = list(MODE_NAMES.values())


@st.cache_data
def load_evaluation():
    summary = pd.read_csv(DATA_DIR / "evaluation_summary.csv")
    categories = pd.read_csv(DATA_DIR / "evaluation_by_category.csv")

    summary["model"] = summary["mode"].map(MODE_NAMES)
    categories["model"] = categories["mode"].map(MODE_NAMES)

    return summary, categories


def render_insights():
    st.subheader("Model Insights")
    st.caption(
        "Evaluation of three answering strategies "
        "on 22 held-out questions (66 responses)."
    )

    try:
        summary, categories = load_evaluation()
    except FileNotFoundError:
        st.error(
            "Evaluation files not found. "
            "Run: python -m scripts.analyze_evaluation"
        )
        return

    # KPI cards
    scores = summary.set_index("mode")

    col1, col2, col3 = st.columns(3)

    for col, mode in zip(
        [col1, col2, col3],
        ["llm_only", "general_rag", "sport_aware_rag"],
    ):
        row = scores.loc[mode]

        col.metric(
            MODE_NAMES[mode],
            f"{row['normalized_score_pct']:.1f}%",
            help="Points earned as a percentage of the maximum possible score.",
        )

    st.divider()

    # Overall performance
    st.markdown("### Overall Performance")

    chart_data = summary.set_index("model").reindex(MODE_ORDER)

    st.bar_chart(
        chart_data["normalized_score_pct"],
        y_label="Normalized score (%)",
        x_label="Answering method",
    )

    st.caption(
        "Correctness is scored from 0 (incorrect) to 2 (correct). "
        "The percentage represents earned points / maximum points, "
        "not the percentage of fully correct answers."
    )

    st.divider()

    # Category comparison
    st.markdown("### Performance by Question Type")

    category_data = categories.pivot(
        index="category",
        columns="model",
        values="normalized_score_pct",
    )

    category_data = category_data.reindex(columns=MODE_ORDER)

    st.bar_chart(
        category_data,
        y_label="Normalized score (%)",
        x_label="Question category",
        stack=False,
    )

    st.caption(
        "Compare how the three methods handle single-sport, "
        "multi-sport, and unanswerable questions."
    )

    # Detailed results
    with st.expander("Detailed evaluation results"):
        st.dataframe(
            summary[
                [
                    "model",
                    "questions",
                    "total_score",
                    "fully_correct",
                    "normalized_score_pct",
                ]
            ].rename(
                columns={
                    "model": "Method",
                    "questions": "Questions",
                    "total_score": "Total score",
                    "fully_correct": "Fully correct",
                    "normalized_score_pct": "Normalized score (%)",
                }
            ),
            hide_index=True,
            use_container_width=True,
        )
