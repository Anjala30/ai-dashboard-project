import streamlit as st
import pandas as pd

# ================== PAGE CONFIG ==================
st.set_page_config(page_title="AI Dashboard", layout="wide")

# ================== LOGIN STATE ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ================== USER DATABASE ==================
users = {
    "admin": "1234",
    "anjala": "pass123",
    "demo": "demo123"
}

# ================== LOGIN FUNCTION ==================
def login():
    st.title("🔐 Login Page")
    st.markdown("### 🔑 Demo Credentials")

    st.code("""
    admin / 1234
    anjala / pass123
    demo / demo123
    """)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login successful ✅")
            st.rerun()
        else:
            st.error("Invalid credentials ❌")

# ================== LOGOUT FUNCTION ==================
def logout():
    st.session_state.logged_in = False
    st.rerun()

# ================== DASHBOARD ==================
def dashboard():

    # Sidebar user + logout
    st.sidebar.write(f"👤 {st.session_state.username}")
    st.sidebar.button("Logout", on_click=logout)

    # ================== LOAD DATA ==================
    df = pd.read_csv("students.csv")

    # Fix data types properly
    df["marks"] = pd.to_numeric(df["marks"], errors="coerce")
    df["age"] = pd.to_numeric(df["age"], errors="coerce")

    # ================== SIDEBAR ==================
    st.sidebar.title("🔎 Filters")

    city = st.sidebar.selectbox(
        "Select City",
        ["All"] + list(df["city"].unique())
    )

    min_marks = st.sidebar.slider(
        "Minimum Marks",
        0, 100, 50
    )

    # Apply filters
    filtered_df = df.copy()

    if city != "All":
        filtered_df = filtered_df[filtered_df["city"] == city]

    filtered_df = filtered_df[filtered_df["marks"] >= min_marks]

    # ================== TITLE ==================
    st.title("🤖 AI Data Query Dashboard")

    # ================== KPI ==================
    st.markdown("## 📊 Key Insights")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Students", len(filtered_df))
    col2.metric("Average Marks", round(filtered_df["marks"].mean(), 2))
    col3.metric("Highest Marks", filtered_df["marks"].max())
    col4.metric("Lowest Marks", filtered_df["marks"].min())

    # ================== AI QUERY ==================
    st.markdown("## 🤖 Ask AI")

    query = st.text_input("Ask your question (e.g. students from Pune)")

    if st.button("Search"):
        if query:

            df_result = df.copy()

            if "pune" in query.lower():
                df_result = df_result[df_result["city"] == "Pune"]

            elif "mumbai" in query.lower():
                df_result = df_result[df_result["city"] == "Mumbai"]

            elif "delhi" in query.lower():
                df_result = df_result[df_result["city"] == "Delhi"]

            elif "top" in query.lower():
                df_result = df_result.sort_values(by="marks", ascending=False)

            elif "lowest" in query.lower():
                df_result = df_result.sort_values(by="marks", ascending=True)

            elif "average" in query.lower():
                st.success(f"Average Marks: {round(df['marks'].mean(), 2)}")

            st.success("AI Response")
            st.dataframe(df_result, use_container_width=True)

    # ================== TABLE ==================
    st.markdown("## 📋 Student Data")
    st.dataframe(filtered_df, use_container_width=True)

    # ================== VISUAL DASHBOARD ==================
    st.markdown("## 📈 Visual Dashboard")

    # ROW 1
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 Marks Distribution")
        st.bar_chart(filtered_df["marks"])

    with col2:
        st.subheader("🏙️ Students by City")
        st.bar_chart(filtered_df["city"].value_counts())

    # ROW 2
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("📊 Average Marks per City")
        avg_marks = filtered_df.groupby("city")["marks"].mean()
        st.bar_chart(avg_marks)

    with col4:
        st.subheader("🔥 Top 5 Performers")
        top_students = filtered_df.sort_values(by="marks", ascending=False).head(5)
        st.dataframe(top_students, use_container_width=True)

    # ROW 3
    col5, col6 = st.columns(2)

    with col5:
        st.subheader("📉 Bottom 5 Performers")
        low_students = filtered_df.sort_values(by="marks", ascending=True).head(5)
        st.dataframe(low_students, use_container_width=True)

    with col6:
        st.subheader("📌 City-wise Count")
        city_count = filtered_df["city"].value_counts().reset_index()
        city_count.columns = ["City", "Count"]
        st.dataframe(city_count, use_container_width=True)

    # ROW 4
    col7, col8 = st.columns(2)

    with col7:
        st.subheader("📊 Marks Statistics")
        st.write(filtered_df["marks"].describe())

    with col8:
        st.subheader("🏆 Highest Scorer Details")
        top = filtered_df.loc[filtered_df["marks"].idxmax()]
        st.write(top)

    # ROW 5
    col9, col10 = st.columns(2)

    with col9:
        st.subheader("📍 City Comparison Chart")
        st.bar_chart(filtered_df.groupby("city")["marks"].sum())

    with col10:
        st.subheader("📈 Marks Trend")
        st.line_chart(filtered_df["marks"])

    # ================== QUICK SEARCH ==================
    st.markdown("## 🔍 Quick Search")

    name_search = st.text_input("Search student by name")

    if name_search:
        result = filtered_df[
            filtered_df["name"].str.contains(name_search, case=False)
        ]
        st.dataframe(result, use_container_width=True)

    # ================== EXTRA ==================
    st.markdown("## 🧠 Extra Insights")

    col11, col12 = st.columns(2)

    with col11:
        st.subheader("Median Marks")
        st.write(filtered_df["marks"].median())

    with col12:
        st.subheader("Standard Deviation")
        st.write(filtered_df["marks"].std())

    # ================== DOWNLOAD ==================
    st.markdown("## ⬇️ Download Data")

    csv = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="students.csv",
        mime="text/csv"
    )

# ================== MAIN ==================
if not st.session_state.logged_in:
    login()
else:
    dashboard()