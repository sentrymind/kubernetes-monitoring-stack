"""
Streamlit Frontend for HealthTrack Research
"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.graph_objects as go
import plotly.express as px

# API Configuration
API_BASE = "http://localhost:8000"

# Page config
st.set_page_config(
    page_title="HealthTrack Research",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.big-font {font-size:20px !important; font-weight: bold;}
.metric-card {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# Helper functions
def api_get(endpoint):
    """GET request to API"""
    try:
        response = requests.get(f"{API_BASE}{endpoint}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

def api_post(endpoint, data):
    """POST request to API"""
    try:
        response = requests.post(f"{API_BASE}{endpoint}", json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

# Sidebar navigation
with st.sidebar:
    st.title("💊 HealthTrack")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["Dashboard", "Add Supplement", "Track Intake", "Research", "Analysis", "Reports"]
    )
    st.markdown("---")
    st.info("Evidence-based supplement tracking with PubMed integration")

# PAGE: Dashboard
if page == "Dashboard":
    st.title("📊 Dashboard")

    # Fetch supplements
    supplements = api_get("/api/supplements")

    if not supplements:
        st.warning("No supplements added yet. Add your first supplement!")
    else:
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Supplements", len(supplements))
        with col2:
            total_research = sum(s.get('research_count', 0) for s in supplements)
            st.metric("Research Articles", total_research)
        with col3:
            st.metric("Active Days", "-")  # TODO: Calculate from logs

        st.markdown("---")

        # Supplements table
        st.subheader("Your Supplements")
        df = pd.DataFrame(supplements)
        st.dataframe(
            df[['name', 'dosage', 'dosage_unit', 'frequency', 'research_count']],
            use_container_width=True
        )

        # Quick actions
        st.markdown("---")
        st.subheader("Quick Actions")
        selected_supp = st.selectbox(
            "Select supplement for quick log:",
            options=[s['name'] for s in supplements]
        )

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("✅ Log Taken Today"):
                supp = next(s for s in supplements if s['name'] == selected_supp)
                result = api_post("/api/intake", {
                    "supplement_id": supp['id'],
                    "date": str(date.today()),
                    "taken": True
                })
                if result:
                    st.success("Logged successfully!")

# PAGE: Add Supplement
elif page == "Add Supplement":
    st.title("➕ Add New Supplement")

    with st.form("add_supplement_form"):
        name = st.text_input("Supplement Name *", placeholder="e.g., Vitamin D3, Omega-3")

        col1, col2 = st.columns(2)
        with col1:
            dosage = st.number_input("Dosage *", min_value=0.0, step=0.1)
            frequency = st.selectbox(
                "Frequency *",
                ["Daily", "Twice daily", "Every other day", "Weekly"]
            )
        with col2:
            dosage_unit = st.selectbox(
                "Unit *",
                ["mg", "g", "mcg", "IU", "ml"]
            )
            auto_search = st.checkbox("Auto-search research (PubMed)", value=True)

        user_notes = st.text_area("Notes (optional)")

        submitted = st.form_submit_button("Add Supplement")

        if submitted:
            if not name or dosage <= 0:
                st.error("Please fill in all required fields")
            else:
                with st.spinner("Adding supplement and searching research..."):
                    result = api_post("/api/supplements", {
                        "name": name,
                        "dosage": dosage,
                        "dosage_unit": dosage_unit,
                        "frequency": frequency,
                        "user_notes": user_notes,
                        "auto_search": auto_search
                    })

                    if result:
                        st.success(f"✅ Supplement added successfully!")
                        if auto_search:
                            st.info(f"🔍 Found {result.get('research_found', 0)} research articles")
                        st.balloons()

# PAGE: Track Intake
elif page == "Track Intake":
    st.title("📅 Track Daily Intake")

    supplements = api_get("/api/supplements")

    if not supplements:
        st.warning("No supplements to track. Add some first!")
    else:
        selected_date = st.date_input("Date", value=date.today())

        st.markdown("---")

        # Create intake form for each supplement
        for supp in supplements:
            with st.expander(f"💊 {supp['name']} ({supp['dosage']} {supp['dosage_unit']})"):
                col1, col2, col3 = st.columns([2, 2, 2])

                with col1:
                    taken = st.checkbox(
                        "Taken",
                        key=f"taken_{supp['id']}"
                    )

                with col2:
                    energy = st.slider(
                        "Energy Level",
                        1, 10, 5,
                        key=f"energy_{supp['id']}"
                    )

                with col3:
                    sleep = st.slider(
                        "Sleep Quality",
                        1, 10, 5,
                        key=f"sleep_{supp['id']}"
                    )

                notes = st.text_input(
                    "Notes",
                    key=f"notes_{supp['id']}"
                )

                if st.button(f"Save Log", key=f"save_{supp['id']}"):
                    result = api_post("/api/intake", {
                        "supplement_id": supp['id'],
                        "date": str(selected_date),
                        "taken": taken,
                        "energy_level": energy,
                        "sleep_quality": sleep,
                        "notes": notes
                    })
                    if result:
                        st.success("Logged successfully!")

# PAGE: Research
elif page == "Research":
    st.title("🔬 Research Evidence")

    supplements = api_get("/api/supplements")

    if not supplements:
        st.warning("No supplements added yet")
    else:
        selected_supp_name = st.selectbox(
            "Select Supplement:",
            options=[s['name'] for s in supplements]
        )

        supp = next(s for s in supplements if s['name'] == selected_supp_name)

        # Refresh button
        if st.button("🔄 Refresh Research from PubMed"):
            with st.spinner("Searching PubMed..."):
                result = api_post(f"/api/research/refresh/{supp['id']}", {})
                if result:
                    st.success(f"✅ Found {result.get('articles_found', 0)} articles")
                    st.rerun()

        st.markdown("---")

        # Fetch research
        research = api_get(f"/api/research/{supp['id']}")

        if not research:
            st.info("No research articles found. Click 'Refresh Research' to search PubMed.")
        else:
            st.success(f"📚 Found {len(research)} research articles")

            # Evidence level distribution
            evidence_counts = {}
            for r in research:
                level = r.get('evidence_level', 'unknown')
                evidence_counts[level] = evidence_counts.get(level, 0) + 1

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("High Quality", evidence_counts.get('high', 0))
            with col2:
                st.metric("Medium Quality", evidence_counts.get('medium', 0))
            with col3:
                st.metric("Low Quality", evidence_counts.get('low', 0))

            st.markdown("---")

            # Display articles
            for r in research[:10]:  # Show first 10
                with st.expander(f"[{r['year']}] {r['title']}"):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"**Authors:** {r.get('authors', 'N/A')}")
                        st.markdown(f"**Journal:** {r.get('journal', 'N/A')}")
                        st.markdown(f"**Type:** {r.get('publication_type', 'N/A')}")

                    with col2:
                        st.markdown(f"**Evidence Level:**")
                        level = r.get('evidence_level', 'unknown')
                        color = {'high': '🟢', 'medium': '🟡', 'low': '🔴'}.get(level, '⚪')
                        st.markdown(f"{color} {level.upper()}")

                    if r.get('key_findings'):
                        st.markdown("**Key Findings:**")
                        st.info(r['key_findings'])

                    if r.get('recommended_dosage'):
                        st.markdown(f"**Recommended Dosage:** {r['recommended_dosage']} {r.get('dosage_unit', '')}")

                    st.markdown(f"[View on PubMed]({r['url']}) | PMID: {r['pmid']}")

# PAGE: Analysis
elif page == "Analysis":
    st.title("🧮 Dosage Analysis")

    supplements = api_get("/api/supplements")

    if not supplements:
        st.warning("No supplements to analyze")
    else:
        selected_supp_name = st.selectbox(
            "Select Supplement:",
            options=[s['name'] for s in supplements]
        )

        supp = next(s for s in supplements if s['name'] == selected_supp_name)

        # Dosage analysis
        st.subheader("Dosage Recommendations")
        analysis = api_get(f"/api/analyze/dosage/{supp['id']}")

        if analysis and 'error' not in analysis:
            status = analysis.get('status', 'unknown')
            status_colors = {
                'optimal': '🟢',
                'above': '🔴',
                'below': '🟡',
                'no_data': '⚪'
            }

            st.markdown(f"### {status_colors.get(status, '⚪')} Status: {status.upper()}")
            st.info(analysis.get('message', ''))

            if 'recommended_range' in analysis:
                rec = analysis['recommended_range']

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Your Dosage", f"{analysis['current_dosage']} {analysis['current_unit']}")
                with col2:
                    st.metric("Recommended Min", f"{rec['min']} {rec['unit']}")
                with col3:
                    st.metric("Recommended Max", f"{rec['max']} {rec['unit']}")

                # Visualization
                fig = go.Figure()

                # Recommended range
                fig.add_trace(go.Scatter(
                    x=[rec['min'], rec['max']],
                    y=[1, 1],
                    mode='lines',
                    name='Recommended Range',
                    line=dict(color='green', width=10),
                    showlegend=True
                ))

                # Your dosage
                fig.add_trace(go.Scatter(
                    x=[analysis['current_dosage']],
                    y=[1],
                    mode='markers',
                    name='Your Dosage',
                    marker=dict(size=15, color='red', symbol='diamond'),
                    showlegend=True
                ))

                fig.update_layout(
                    title="Dosage Comparison",
                    xaxis_title=f"Dosage ({analysis['current_unit']})",
                    yaxis=dict(visible=False),
                    height=200
                )

                st.plotly_chart(fig, use_container_width=True)

                # Top sources
                if 'top_sources' in analysis:
                    st.markdown("### Top Research Sources")
                    for source in analysis['top_sources']:
                        st.markdown(f"- **{source['dosage']} {rec['unit']}** - PMID: {source['pmid']} ({source['year']}) - Evidence: {source['evidence_level']}")

        # Evidence summary
        st.markdown("---")
        st.subheader("Evidence Summary")
        evidence = api_get(f"/api/analyze/evidence/{supp['id']}")

        if evidence and 'error' not in evidence:
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Total Studies", evidence.get('total_studies', 0))

                # Evidence levels pie chart
                if 'evidence_levels' in evidence:
                    fig = px.pie(
                        values=list(evidence['evidence_levels'].values()),
                        names=list(evidence['evidence_levels'].keys()),
                        title="Evidence Quality Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Year distribution
                if 'year_distribution' in evidence:
                    years = list(evidence['year_distribution'].keys())
                    counts = list(evidence['year_distribution'].values())

                    fig = go.Figure(data=[
                        go.Bar(x=years, y=counts)
                    ])
                    fig.update_layout(
                        title="Publications by Year",
                        xaxis_title="Year",
                        yaxis_title="Count"
                    )
                    st.plotly_chart(fig, use_container_width=True)

# PAGE: Reports
elif page == "Reports":
    st.title("📄 Generate Reports")

    st.info("PDF report generation coming soon!")

    # Show text report for now
    supplements = api_get("/api/supplements")

    if supplements:
        report = f"""
# HealthTrack Research Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Your Supplements ({len(supplements)})

"""
        for supp in supplements:
            report += f"\n### {supp['name']}\n"
            report += f"- **Dosage:** {supp['dosage']} {supp['dosage_unit']}\n"
            report += f"- **Frequency:** {supp['frequency']}\n"
            report += f"- **Research Articles:** {supp.get('research_count', 0)}\n"

        st.markdown(report)

        st.download_button(
            label="📥 Download as Markdown",
            data=report,
            file_name=f"healthtrack_report_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown"
        )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "<small>HealthTrack Research v1.0 | Evidence-based supplement tracking</small>"
    "</div>",
    unsafe_allow_html=True
)
