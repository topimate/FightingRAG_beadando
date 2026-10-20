
from pathlib import Path

import pandas as pd
import streamlit as st
import altair as alt

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "evaluation"

MODE_NAMES = {
    "llm_only": "LLM Only",
    "general_rag": "General RAG",
    "sport_aware_rag": "Sport-aware RAG",
}

MODE_ORDER = list(MODE_NAMES.values())

MODEL_COLORS = {
    "LLM Only": "#92949D",
    "General RAG": "#F87171",
    "Sport-aware RAG": "#E11D35",
}

MODEL_COLOR_SCALE = alt.Scale(
    domain=list(MODEL_COLORS.keys()),
    range=list(MODEL_COLORS.values()),
)


CATEGORY_NAMES = {
    "single": "Single sport",
    "comparison": "Two-sport comparison",
    "triple_comparison": "Three-sport comparison",
    "unanswerable": "Unanswerable",
}

SCORE_NAMES = {
    0: "Incorrect",
    1: "Partially correct",
    2: "Correct",
}


@st.cache_data
def load_data():
    summary = pd.read_csv(
        DATA_DIR / "evaluation_summary.csv"
    )
    categories = pd.read_csv(
        DATA_DIR / "evaluation_by_category.csv"
    )
    reviews = pd.read_csv(
        DATA_DIR / "answer_review_scored.csv"
    )

    for df in (summary, categories, reviews):
        df["model"] = df["mode"].map(MODE_NAMES)

    reviews["correctness"] = pd.to_numeric(
        reviews["correctness"],
        errors="coerce",
    )

    return summary, categories, reviews


def clean_text(value):
    """Convert missing values to empty strings."""
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return str(value)
    if pd.isna(value):
        return ""
    return str(value)


def render_overview(summary):
    st.markdown("### Performance Overview")
    st.caption(
        "22 held-out questions · 66 model responses · "
        "Three answering strategies"
    )

    indexed = summary.set_index("mode")
    columns = st.columns(3, gap="medium")

    for col, mode in zip(columns, MODE_NAMES):
        row = indexed.loc[mode]

        with col:
            with st.container(border=True):
                st.caption(MODE_NAMES[mode])

                st.metric(
                    "Normalized score",
                    f"{row['normalized_score_pct']:.1f}%",
                    label_visibility="collapsed",
                )

                st.caption(
                    f"{int(row['fully_correct'])} / "
                    f"{int(row['questions'])} fully correct"
                )

    with st.container(border=True):
        st.markdown("#### Overall Model Comparison")


        chart = (
            summary.set_index("model")
            .reindex(MODE_ORDER)
            .reset_index()
        )


        chart_data = summary.copy()

        chart = (
            alt.Chart(chart_data)
            .mark_bar(cornerRadiusEnd=6)
            .encode(
                y=alt.Y("model:N", title=None),
                x=alt.X(
                    "normalized_score_pct:Q",
                    title="Normalized score (%)",
                    scale=alt.Scale(domain=[0, 100]),
                ),
                color=alt.Color(
                    "model:N",
                    scale=MODEL_COLOR_SCALE,
                    legend=None,
                ),
                tooltip=[
                    alt.Tooltip("model:N", title="Model"),
                    alt.Tooltip(
                        "normalized_score_pct:Q",
                        title="Score (%)",
                        format=".1f",
                    ),
                ],
            )
            .properties(height=190)
        )

        st.altair_chart(chart, width="stretch")



        st.caption(
            "Normalized score = earned correctness points / "
            "maximum available points. "
            "This is not the percentage of fully correct answers."
        )

    with st.container(border=True):
        st.markdown("#### Key Finding")

        st.markdown(
            "On the held-out test set, **Sport-aware RAG** "
            "achieved the highest normalized correctness score."
        )

        sport_score = float(
            indexed.loc["sport_aware_rag", "normalized_score_pct"]
        )
        general_score = float(
            indexed.loc["general_rag", "normalized_score_pct"]
        )

        difference = sport_score - general_score

        st.metric(
            "Improvement over General RAG",
            f"+{difference:.1f} percentage points",
        )

        st.caption(
            "Results are based on a small, manually scored "
            "evaluation dataset. They are not a statistical "
            "guarantee of performance on new questions."
        )


def render_categories(categories):
    st.markdown("### Performance by Question Type")
    st.caption(
        "Discover how each approach performs on "
        "different types of combat-sport questions."
    )

    data = categories.copy()

    data["category_label"] = (
        data["category"]
        .map(CATEGORY_NAMES)
        .fillna(data["category"])
    )

    pivot = data.pivot(
        index="category_label",
        columns="model",
        values="normalized_score_pct",
    )

    category_order = [
        CATEGORY_NAMES[key]
        for key in CATEGORY_NAMES
        if CATEGORY_NAMES[key] in pivot.index
    ]

    pivot = pivot.reindex(
        index=category_order,
        columns=MODE_ORDER,
    )

    with st.container(border=True):
        st.markdown("#### Category Comparison")



        chart = (
            alt.Chart(data)
            .mark_bar(cornerRadiusEnd=4)
            .encode(
                x=alt.X("category_label:N", title=None),
                xOffset=alt.XOffset("model:N"),
                y=alt.Y(
                    "normalized_score_pct:Q",
                    title="Normalized score (%)",
                    scale=alt.Scale(domain=[0, 100]),
                ),
                color=alt.Color(
                    "model:N",
                    scale=MODEL_COLOR_SCALE,
                    legend=alt.Legend(
                        title=None,
                        orient="bottom",
                    ),
                ),
                tooltip=[
                    alt.Tooltip("model:N", title="Model"),
                    alt.Tooltip("category_label:N", title="Category"),
                    alt.Tooltip(
                        "normalized_score_pct:Q",
                        title="Score (%)",
                        format=".1f",
                    ),
                ],
            )
            .properties(height=350)
        )

        st.altair_chart(chart, width="stretch")



        st.caption(
            "Each score represents the normalized correctness "
            "of a model for a particular question category."
        )

    with st.container(border=True):
        st.markdown("#### Category Breakdown")

        category_list = list(CATEGORY_NAMES.keys())

        selected_category = st.selectbox(
            "Explore a question category",
            category_list,
            format_func=lambda x: CATEGORY_NAMES[x],
            key="insights_category_select",
        )

        selected = data[
            data["category"] == selected_category
        ].copy()

        selected = selected.set_index("model").reindex(
            MODE_ORDER
        )

        columns = st.columns(3)

        for col, model in zip(columns, MODE_ORDER):
            with col:
                row = selected.loc[model]

                with st.container(border=True):
                    st.caption(model)

                    st.metric(
                        "Score",
                        f"{float(row['normalized_score_pct']):.1f}%",
                        label_visibility="collapsed",
                    )

                    st.caption(
                        f"{int(row['questions'])} questions"
                    )

    with st.expander("View complete category data"):
        display = data[
            [
                "category_label",
                "model",
                "questions",
                "normalized_score_pct",
            ]
        ].rename(
            columns={
                "category_label": "Question type",
                "model": "Model",
                "questions": "Questions",
                "normalized_score_pct": "Score (%)",
            }
        )

        st.dataframe(
            display,
            hide_index=True,
            use_container_width=True,
        )


def render_review_card(row):
    """Display one model answer at full width."""
    score = row["correctness"]

    if pd.notna(score):
        score_text = SCORE_NAMES.get(
            int(score),
            "Not scored",
        )
        score_value = f"{int(score)} / 2"
    else:
        score_text = "Not scored"
        score_value = "N/A"

    with st.container(border=True):
        header_left, header_right = st.columns([3, 1])

        with header_left:
            st.markdown(f"#### {row['model']}")
            st.caption(f"Evaluation: {score_text}")

        with header_right:
            st.metric("Correctness", score_value)

        st.divider()

        st.markdown("**Model Answer**")

        answer = clean_text(row.get("answer"))

        st.markdown(
            answer if answer else "*No answer recorded.*"
        )

    notes = clean_text(row.get("error_notes"))

    if notes:
        with st.container(border=True):
            st.markdown("#### Evaluation Notes")
            st.write(notes)

    sources = clean_text(
        row.get("retrieved_sources")
    )

    if sources and sources.lower() not in ("nan", "[]"):
        with st.expander("Retrieved Sources"):
            st.code(sources, language=None)


def render_error_explorer(reviews):
    st.markdown("### Error Explorer")
    st.caption(
        "Inspect questions, compare answers, "
        "and understand where models succeed or fail."
    )

    test = reviews[
        reviews["split"] == "evaluation"
    ].copy()

    if test.empty:
        st.warning("No evaluation questions found.")
        return

    question_table = (
        test[["id", "category", "question"]]
        .drop_duplicates(subset=["id"])
        .sort_values("id")
    )

    scores = test.pivot_table(
        index="id",
        columns="mode",
        values="correctness",
        aggfunc="first",
    )

    if {
        "general_rag",
        "sport_aware_rag",
    }.issubset(scores.columns):
        scores["improvement"] = (
            scores["sport_aware_rag"]
            - scores["general_rag"]
        )

        question_table = question_table.merge(
            scores[["improvement"]],
            left_on="id",
            right_index=True,
            how="left",
        )

    with st.container(border=True):
        st.markdown("#### Find a Question")

        filter_col, focus_col = st.columns([2, 3])

        with filter_col:
            category_options = ["All"] + sorted(
                question_table["category"]
                .dropna()
                .unique()
                .tolist()
            )

            selected_category = st.selectbox(
                "Question type",
                category_options,
                format_func=lambda x: (
                    "All categories"
                    if x == "All"
                    else CATEGORY_NAMES.get(x, x)
                ),
            )

        with focus_col:
            st.write("")
            focus = st.checkbox(
                "Show only Sport-aware improvements"
            )

        filtered = question_table.copy()

        if selected_category != "All":
            filtered = filtered[
                filtered["category"] == selected_category
            ]

        if focus and "improvement" in filtered.columns:
            filtered = filtered[
                filtered["improvement"] > 0
            ]

        if filtered.empty:
            st.info("No questions match these filters.")
            return

        question_lookup = dict(
            zip(filtered["id"], filtered["question"])
        )

        selected_id = st.selectbox(
            "Select a question",
            filtered["id"].tolist(),
            format_func=lambda qid: (
                f"{qid} — {question_lookup[qid][:85]}"
            ),
        )

    selected = test[
        test["id"] == selected_id
    ].copy()

    if selected.empty:
        return

    first = selected.iloc[0]

    with st.container(border=True):
        st.caption(
            CATEGORY_NAMES.get(
                first["category"],
                first["category"],
            )
        )

        st.markdown(f"### {first['question']}")

        with st.expander(
            "Reference Answer",
            expanded=True,
        ):
            st.write(
                clean_text(
                    first.get("expected_answer")
                )
            )

            reference_sources = clean_text(
                first.get("reference_sources")
            )

            if reference_sources:
                st.caption(
                    f"Reference: {reference_sources}"
                )

    st.markdown("#### Model Comparison")

    selected["sort_order"] = selected["model"].map(
        {
            name: index
            for index, name in enumerate(MODE_ORDER)
        }
    )

    selected = selected.sort_values("sort_order")

    # Compact score cards
    score_cols = st.columns(3, gap="medium")

    for col, model_name in zip(score_cols, MODE_ORDER):
        model_rows = selected[
            selected["model"] == model_name
        ]

        with col:
            with st.container(border=True):
                st.caption(model_name)

                if model_rows.empty:
                    st.metric(
                        "Correctness",
                        "N/A",
                        label_visibility="collapsed",
                    )
                else:
                    score = model_rows.iloc[0]["correctness"]

                    value = (
                        f"{int(score)} / 2"
                        if pd.notna(score)
                        else "N/A"
                    )

                    st.metric(
                        "Correctness",
                        value,
                        label_visibility="collapsed",
                    )

    # Full-width answers: prevent Markdown table overlap
    model_tabs = st.tabs(MODE_ORDER)

    for tab, model_name in zip(
        model_tabs,
        MODE_ORDER,
    ):
        with tab:
            model_rows = selected[
                selected["model"] == model_name
            ]

            if model_rows.empty:
                st.info(
                    "No response recorded for this model."
                )
                continue

            row = model_rows.iloc[0]

            render_review_card(row)


def render_details(reviews):
    st.markdown("### Detailed Results")
    st.caption(
        "Explore all scored responses and export "
        "a filtered evaluation dataset."
    )

    test = reviews[
        reviews["split"] == "evaluation"
    ].copy()

    with st.container(border=True):
        st.markdown("#### Evaluation Records")

        selected_models = st.multiselect(
            "Filter answering methods",
            MODE_ORDER,
            default=MODE_ORDER,
        )

        if not selected_models:
            st.info("Select at least one model.")
            return

        test = test[
            test["model"].isin(selected_models)
        ].copy()

        test["score_label"] = (
            test["correctness"]
            .map(SCORE_NAMES)
            .fillna("Not scored")
        )

        display = test[
            [
                "id",
                "category",
                "model",
                "correctness",
                "score_label",
                "question",
                "error_notes",
            ]
        ].rename(
            columns={
                "id": "Question ID",
                "category": "Category",
                "model": "Model",
                "correctness": "Score",
                "score_label": "Result",
                "question": "Question",
                "error_notes": "Evaluation notes",
            }
        )

        st.dataframe(
            display,
            hide_index=True,
            use_container_width=True,
        )

    with st.container(border=True):
        st.markdown("#### Export Results")
        st.caption(
            f"{len(test)} evaluation records selected."
        )

        st.download_button(
            "Download filtered evaluation",
            data=test.to_csv(
                index=False
            ).encode("utf-8-sig"),
            file_name="fightrag_evaluation_filtered.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary",
        )


def render_insights():
    st.subheader("Model Insights")

    st.caption(
        "A transparent comparison of LLM-only, "
        "General RAG and Sport-aware RAG."
    )

    try:
        summary, categories, reviews = load_data()

    except FileNotFoundError:
        st.error(
            "Evaluation files not found. "
            "Run: python -m scripts.analyze_evaluation"
        )
        return

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Overview",
            "Question Types",
            "Error Explorer",
            "Results",
        ]
    )

    with tab1:
        render_overview(summary)

    with tab2:
        render_categories(categories)

    with tab3:
        render_error_explorer(reviews)

    with tab4:
        render_details(reviews)
