import streamlit as st
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
import io
from datetime import datetime

from sql_engine.sql_generator import generate_sql
from sql_engine.query_executor import execute_query


st.set_page_config(
    page_title="AI SQL Assistant",
    page_icon="🤖",
    layout="wide"
)

sidebar = st.sidebar
sidebar.title("AI SQL Assistant")
sidebar.markdown("### Theme")
theme_choice = sidebar.radio(
    "Mode",
    ["Dark", "Light"],
    index=0,
    horizontal=True,
)
# to run write streamlit run app.py 

is_dark = theme_choice == "Dark"
if is_dark:
    body_bg = "linear-gradient(135deg, #0f172a 0%, #111827 45%, #1f2937 100%)"
    base_text = "#f4f7ff"
    sidebar_bg = "rgba(15, 23, 42, 0.95)"
    card_bg = "rgba(15, 23, 42, 0.95)"
    card_border = "rgba(148, 163, 184, 0.15)"
    accent = "rgba(59, 130, 246, 0.18)"
    shadow = "rgba(15, 23, 42, 0.35)"
    button_text = "#0f172a"
    button_bg = "linear-gradient(135deg, #2563eb, #7dd3fc)"
    button_hover = "linear-gradient(135deg, #1d4ed8, #38bdf8)"
    muted = "#cbd5e1"
else:
    body_bg = "linear-gradient(135deg, #f8fafc 0%, #e2e8f0 45%, #f8fafc 100%)"
    base_text = "#0f172a"
    sidebar_bg = "rgba(255, 255, 255, 0.95)"
    card_bg = "rgba(255, 255, 255, 0.96)"
    card_border = "rgba(148, 163, 184, 0.45)"
    accent = "rgba(59, 130, 246, 0.12)"
    shadow = "rgba(15, 23, 42, 0.12)"
    button_text = "#ffffff"
    button_bg = "linear-gradient(135deg, #2563eb, #38bdf8)"
    button_hover = "linear-gradient(135deg, #1d4ed8, #60a5fa)"
    muted = "#475569"

page_style = f"""
<style>
body {{
    color: {base_text};
    background: {body_bg};
}}
section.main {{
    padding: 1rem 1.5rem 2rem;
}}
.stApp {{
    background: transparent;
}}
.stSidebar {{
    background: {sidebar_bg};
    color: {base_text};
    border-right: 1px solid rgba(148, 163, 184, 0.2);
}}
.hero-card,
.section-card {{
    background: {card_bg};
    border: 1px solid {card_border};
    border-radius: 24px;
    padding: 2rem;
    box-shadow: 0 24px 80px {shadow};
}}
.hero-card {{
    position: relative;
    overflow: hidden;
}}
.hero-card::before {{
    content: "";
    position: absolute;
    top: -60px;
    right: -80px;
    width: 220px;
    height: 220px;
    background: {accent};
    border-radius: 50%;
    filter: blur(50px);
    animation: float 8s ease-in-out infinite;
}}
.expand-text {{
    font-size: 1rem;
    line-height: 1.8;
    color: {muted};
}}
.animate-header {{
    animation: fadeIn 1.2s ease-out;
}}
.animate-section {{
    animation: slideUp 0.9s ease-out;
}}
@keyframes float {{
    0%, 100% {{ transform: translateY(0) translateX(0); }}
    50% {{ transform: translateY(-18px) translateX(10px); }}
}}
@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes slideUp {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
.stButton button {{
    background: {button_bg};
    color: {button_text};
    font-weight: 700;
}}
.stButton button:hover {{
    background: {button_hover};
}}
</style>
"""
st.markdown(page_style, unsafe_allow_html=True)

# ============================================
# Helper Functions for Phase 1 Features
# ============================================

def initialize_session_state():
    """Initialize session state for query history"""
    if "query_history" not in st.session_state:
        st.session_state.query_history = []
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "last_query" not in st.session_state:
        st.session_state.last_query = None


def add_to_history(question, sql_query):
    """Add question and query to history"""
    history_item = {
        "question": question,
        "sql": sql_query,
        "timestamp": datetime.now().strftime("%H:%M")
    }
    st.session_state.query_history.insert(0, history_item)
    # Keep only last 10 queries
    if len(st.session_state.query_history) > 10:
        st.session_state.query_history = st.session_state.query_history[:10]


def get_smart_chart_type(df):
    """
    Intelligently determine which chart to display based on data structure.
    
    Rules:
    - 2 columns (1 text + 1 numeric) → Bar Chart
    - Category + Count pattern → Pie Chart
    - Date + Value pattern → Line Chart
    - Multi-column → Table only
    """
    if len(df.columns) == 2:
        col1_type = df.iloc[:, 0].dtype
        col2_type = df.iloc[:, 1].dtype
        col1_name = df.columns[0].lower()
        col2_name = df.columns[1].lower()

        text_numeric = (
            (pd.api.types.is_string_dtype(col1_type) and pd.api.types.is_numeric_dtype(col2_type)) or
            (pd.api.types.is_string_dtype(col2_type) and pd.api.types.is_numeric_dtype(col1_type))
        )
        date_numeric = (
            (pd.api.types.is_datetime64_any_dtype(col1_type) and pd.api.types.is_numeric_dtype(col2_type)) or
            (pd.api.types.is_datetime64_any_dtype(col2_type) and pd.api.types.is_numeric_dtype(col1_type))
        )

        if text_numeric:
            if 'count' in col1_name or 'total' in col1_name or 'sum' in col1_name or \
               'count' in col2_name or 'total' in col2_name or 'sum' in col2_name:
                return "pie"
            return "bar"

        if date_numeric:
            return "line"

    return "table"


def _pivot_chart_df(df):
    """Normalize 2-column data for chart display."""
    if len(df.columns) != 2:
        return df

    first_numeric = pd.api.types.is_numeric_dtype(df.iloc[:, 0].dtype)
    second_numeric = pd.api.types.is_numeric_dtype(df.iloc[:, 1].dtype)
    first_date = pd.api.types.is_datetime64_any_dtype(df.iloc[:, 0].dtype)
    second_date = pd.api.types.is_datetime64_any_dtype(df.iloc[:, 1].dtype)

    if first_numeric and not second_numeric:
        return df.iloc[:, [1, 0]]
    if first_date and second_numeric:
        return df
    if second_date and first_numeric:
        return df.iloc[:, [1, 0]]

    return df


def display_smart_chart(df, chart_type):
    """Display chart based on determined type"""
    chart_df = _pivot_chart_df(df)

    if chart_type == "bar":
        st.bar_chart(
            chart_df.set_index(chart_df.columns[0]) if len(chart_df.columns) >= 2 else chart_df,
            use_container_width=True
        )
    elif chart_type == "pie":
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.pie(
            chart_df.iloc[:, 1],
            labels=chart_df.iloc[:, 0],
            autopct='%1.1f%%',
            startangle=90,
            colors=plt.cm.Set3.colors
        )
        ax.set_title(f"{chart_df.columns[1]} by {chart_df.columns[0]}", fontsize=14, fontweight='bold')
        st.pyplot(fig, use_container_width=True)
    elif chart_type == "line":
        st.line_chart(
            chart_df.set_index(chart_df.columns[0]) if len(chart_df.columns) >= 2 else chart_df,
            use_container_width=True
        )
    else:  # table
        st.dataframe(df, use_container_width=True)


def create_download_buttons(result_df):
    """Create download buttons for CSV and Excel"""
    col1, col2 = st.columns(2)
    
    # CSV Download
    with col1:
        csv_data = result_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Excel Download
    with col2:
        excel_buffer = io.BytesIO()
        try:
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                result_df.to_excel(writer, sheet_name='Results', index=False)
            excel_buffer.seek(0)
            st.download_button(
                label="📊 Download Excel",
                data=excel_buffer.getvalue(),
                file_name=f"query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.ms-excel",
                use_container_width=True
            )
        except ImportError:
            st.info("💡 Install openpyxl for Excel export: pip install openpyxl")


def display_query_metrics(result_df):
    """Display query execution metrics"""
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        st.metric(
            label="Rows Returned",
            value=len(result_df),
            delta=None
        )
    
    with metric_col2:
        st.metric(
            label="Columns",
            value=len(result_df.columns),
            delta=None
        )
    
    with metric_col3:
        st.metric(
            label="Execution Status",
            value="✅ Success",
            delta=None
        )


# Initialize session state
initialize_session_state()

section = sidebar.radio(
    "Navigation",
    ["🏠 Home", "💬 Ask Question", "📊 Data Overview", "ℹ️ About"],
    index=0
)
sidebar.divider()

# ============================================
# Query History Section in Sidebar
# ============================================
sidebar.markdown("### 📜 Recent Questions")
if st.session_state.query_history:
    for i, item in enumerate(st.session_state.query_history):
        with sidebar.expander(f"{item['question'][:40]}... ({item['timestamp']})", expanded=False):
            st.caption("**Question:**")
            st.write(item['question'])
            st.caption("**SQL Query:**")
            st.code(item['sql'], language='sql')
            if st.button("Re-run this query", key=f"rerun_{i}"):
                st.session_state.last_query = item['sql']
                st.rerun()
else:
    sidebar.info("No recent queries yet. Ask a question to get started!")

sidebar.divider()

# ============================================
# Example Prompts Section
# ============================================
sidebar.markdown("### Example prompts")
sidebar.markdown(
    "• Show top 5 brands with most products  \n    • Which brand has the most expensive product?  \n    • Show products above 50000 rupees  \n    • What are the most common colors?  \n    • Show average original price by brand"
)
sidebar.divider()
sidebar.markdown("Built with Streamlit + SQLite")

# Load dataset
base_path = Path(__file__).resolve().parent
db_path = base_path / "Database" / "sales.db"
engine = create_engine(f"sqlite:///{db_path.as_posix()}")
try:
    df = pd.read_sql("SELECT * FROM products", engine)
except Exception as exc:
    st.error("Unable to load the dataset. Please verify Database/sales.db exists.")
    st.stop()

brand_counts = df["Brand"].value_counts().nlargest(15)
color_counts = df["Color"].value_counts().nlargest(15)

if section == "🏠 Home":
    st.markdown("<div class='hero-card animate-section'>", unsafe_allow_html=True)
    st.markdown("<div class='animate-header'>", unsafe_allow_html=True)
    st.title("🤖 AJIO AI SQL Assistant")
    st.subheader("Modern data exploration with natural language SQL generation")
    st.markdown(
        "<p class='expand-text'>Use the side menu to navigate sections, ask questions in plain English, and inspect results with a polished, readable interface.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.metric("Total products", len(df), delta=None)
        st.metric("Unique brands", df["Brand"].nunique(), delta=None)
        st.metric("Distinct colors", df["Color"].nunique(), delta=None)
    with col2:
        st.markdown("### Top brands")
        st.bar_chart(brand_counts)
    st.markdown("</div>", unsafe_allow_html=True)

elif section == "💬 Ask Question":
    st.markdown("<div class='section-card animate-section'>", unsafe_allow_html=True)
    st.header("Ask a question")
    st.write("Type a natural language question and let the AI generate the corresponding SQL query.")
    question = st.text_input(
        "Ask a question about the dataset",
        placeholder="Example: Show top 5 brands with most products",
        key="question_input"
    )
    if st.button("Generate Answer", use_container_width=True):
        if not question:
            st.warning("Please enter a question before generating SQL.")
        else:
            with st.spinner("Generating SQL..."):
                sql_query = generate_sql(question)
            
            # ============================================
            # Display Generated SQL
            # ============================================
            st.subheader("Generated SQL")
            st.code(sql_query, language="sql")
            
            # ============================================
            # Execute Query and Display Results
            # ============================================
            st.subheader("Results")
            try:
                result = execute_query(sql_query)
                
                # Add to query history
                add_to_history(question, sql_query)
                
                # Display Query Metrics (Phase 1: Feature 3)
                st.markdown("**Query Metrics:**")
                display_query_metrics(result)
                
                st.divider()
                
                # Determine and display chart type (Phase 1: Feature 4)
                chart_type = get_smart_chart_type(result)
                
                if chart_type != "table":
                    st.markdown(f"**Visualization ({chart_type.capitalize()} Chart):**")
                    display_smart_chart(result, chart_type)
                    st.divider()
                
                st.markdown("**Raw Data:**")
                st.dataframe(result, use_container_width=True)
                
                # Download buttons (Phase 1: Feature 2)
                st.markdown("**Export Results:**")
                create_download_buttons(result)
                
                st.success("✅ Query executed successfully.")
            except Exception as exc:
                st.error(f"❌ Query execution failed: {exc}")
    st.markdown("</div>", unsafe_allow_html=True)

elif section == "📊 Data Overview":
    st.markdown("<div class='section-card animate-section'>", unsafe_allow_html=True)
    st.header("Dataset overview")
    st.write("Inspect the dataset and see quick summary statistics for the AJIO product dataset.")
    stats_col1, stats_col2, stats_col3 = st.columns(3)
    with stats_col1:
        st.metric("Total products", len(df))
    with stats_col2:
        st.metric("Unique brands", df["Brand"].nunique())
    with stats_col3:
        st.metric("Distinct colors", df["Color"].nunique())
    st.divider()
    st.subheader("Popular brands")
    st.bar_chart(brand_counts)
    st.subheader("Popular colors")
    st.bar_chart(color_counts)
    st.divider()
    st.subheader("Sample rows")
    st.dataframe(df.head(12), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown("<div class='section-card animate-section'>", unsafe_allow_html=True)
    st.header("About this assistant")
    st.write(
        "This app converts plain-English questions into SQL, executes them against the AJIO sales dataset, and shows results in a polished dashboard."
    )
    st.write("**Features:**")
    st.write(
        "- Modern sidebar navigation\n- Animated UI enhancements\n- SQL generation from natural language\n- Interactive dataset summary and charts"
    )
    st.write("**Built with:** Streamlit, SQLAlchemy, SQLite")
    st.markdown("</div>", unsafe_allow_html=True)
