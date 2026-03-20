import streamlit as st
import pandas as pd
import requests

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

# ================== WEATHER FUNCTION ==================
def get_weather(city):
    api_key = "67c4117ca275c8948ddbc80f84554e42"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        response = requests.get(url)
        data = response.json()

        if data["cod"] == 200:
            temp = data["main"]["temp"]
            weather = data["weather"][0]["description"]
            return f"{weather}, {temp}°C"
        else:
            return "Weather not found"
    except:
        return "Error fetching weather"

# ================== AI AGENT ==================
def ai_agent(student_name, df):
    student = df[df["name"].str.lower() == student_name.lower()]

    if student.empty:
        return "Student not found ❌"

    city = student.iloc[0]["city"]
    marks = student.iloc[0]["marks"]

    weather = get_weather(city)

    return f"""
    📊 Student: {student_name}  
    🎯 Marks: {marks}  
    🌍 City: {city}  
    ☁️ Weather: {weather}  

    💡 Insight: Good time to study!
    """

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

# ================== LOGOUT ==================
def logout():
    st.session_state.logged_in = False
    st.rerun()

# ================== DASHBOARD ==================
def dashboard():

    st.sidebar.write(f"👤 {st.session_state.username}")
    st.sidebar.button("Logout", on_click=logout)

    # LOAD DATA
    df = pd.read_csv("students.csv")
    df["marks"] = pd.to_numeric(df["marks"], errors="coerce")
    df["age"] = pd.to_numeric(df["age"], errors="coerce")

    # FILTERS
    st.sidebar.title("🔎 Filters")

    city = st.sidebar.selectbox(
        "Select City",
        ["All"] + list(df["city"].unique())
    )

    min_marks = st.sidebar.slider("Minimum Marks", 0, 100, 50)

    filtered_df = df.copy()

    if city != "All":
        filtered_df = filtered_df[filtered_df["city"] == city]

    filtered_df = filtered_df[filtered_df["marks"] >= min_marks]

    # TITLE
    st.title("🤖 AI Data Query Dashboard")

    # KPI
    st.markdown("## 📊 Key Insights")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Students", len(filtered_df))
    col2.metric("Average Marks", round(filtered_df["marks"].mean(), 2))
    col3.metric("Highest Marks", filtered_df["marks"].max())
    col4.metric("Lowest Marks", filtered_df["marks"].min())

    # ================== EXISTING AI QUERY ==================
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

    # ================== NEW AI AGENT (TRACK 2) ==================
    st.markdown("## 🤖 Smart AI Assistant")

    student_query = st.text_input("Ask about a student (e.g. Priya)")

    if student_query:
        response = ai_agent(student_query, filtered_df)
        st.success(response)

    # TABLE
    st.markdown("## 📋 Student Data")
    st.dataframe(filtered_df, use_container_width=True)

    # VISUALS
    st.markdown("## 📈 Visual Dashboard")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 Marks Distribution")
        st.bar_chart(filtered_df["marks"])

    with col2:
        st.subheader("🏙️ Students by City")
        st.bar_chart(filtered_df["city"].value_counts())

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("📊 Average Marks per City")
        st.bar_chart(filtered_df.groupby("city")["marks"].mean())

    with col4:
        st.subheader("🔥 Top 5 Performers")
        st.dataframe(filtered_df.sort_values(by="marks", ascending=False).head(5))

    # QUICK SEARCH
    st.markdown("## 🔍 Quick Search")

    name_search = st.text_input("Search student by name")

    if name_search:
        result = filtered_df[
            filtered_df["name"].str.contains(name_search, case=False)
        ]
        st.dataframe(result, use_container_width=True)

    # EXTRA
    st.markdown("## 🧠 Extra Insights")

    col11, col12 = st.columns(2)

    col11.subheader("Median Marks")
    col11.write(filtered_df["marks"].median())

    col12.subheader("Standard Deviation")
    col12.write(filtered_df["marks"].std())

    # DOWNLOAD
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