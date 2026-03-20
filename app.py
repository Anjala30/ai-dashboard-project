import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
from openai import OpenAI

# ================== CONFIG ==================
st.set_page_config(page_title="AI Dashboard", layout="wide")

# ================== OPENAI ==================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ================== UI STYLE ==================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right,#0f2027,#203a43,#2c5364);
    color: white;
}
.chat-user {
    background:#2563eb;
    padding:10px;
    border-radius:10px;
    margin-bottom:5px;
}
.chat-ai {
    background:#16a34a;
    padding:10px;
    border-radius:10px;
    margin-bottom:10px;
}
</style>
""", unsafe_allow_html=True)

# ================== LOGIN STATE ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ================== USERS ==================
users = {
    "admin": "1234",
    "anjala": "pass123",
    "demo": "demo123"
}

# ================== WEATHER ==================
def get_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid=67c4117ca275c8948ddbc80f84554e42&units=metric"
        data = requests.get(url).json()
        return f"{data['weather'][0]['description']}, {data['main']['temp']}°C"
    except:
        return "N/A"

# ================== AI AGENT ==================
def ai_agent(student_name, df):
    student = df[df["name"].str.lower() == student_name.lower()]

    if student.empty:
        return "Student not found ❌"

    city = student.iloc[0]["city"]
    marks = student.iloc[0]["marks"]

    weather = get_weather(city)

    if marks >= 85:
        insight = "Excellent performance 🚀"
    elif marks >= 70:
        insight = "Good performance 👍"
    elif marks >= 50:
        insight = "Average performance ⚡"
    else:
        insight = "Needs improvement 📉"

    return f"""
📌 Student: {student_name}
📊 Marks: {marks}
🌍 City: {city}
🌤 Weather: {weather}

💡 Insight: {insight}
"""

# ================== LOGIN ==================
def login():
    st.title("🔐 Login Page")

    st.info("admin / 1234\nanjala / pass123\ndemo / demo123")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Invalid credentials ❌")

# ================== LOGOUT ==================
def logout():
    st.session_state.logged_in = False
    st.rerun()

# ================== DASHBOARD ==================
def dashboard():

    # SIDEBAR
    st.sidebar.success("AI Dashboard Live 🚀")
    st.sidebar.write(f"👤 {st.session_state.username}")
    st.sidebar.button("Logout", on_click=logout)

    # LOAD DATA
    df = pd.read_csv("students.csv")
    df["marks"] = pd.to_numeric(df["marks"], errors="coerce")

    # ================= FILTERS =================
    st.sidebar.title("🔎 Filters")

    city = st.sidebar.selectbox("Select City", ["All"] + list(df["city"].unique()))
    min_marks = st.sidebar.slider("Minimum Marks", 0, 100, 50)

    filtered_df = df.copy()

    if city != "All":
        filtered_df = filtered_df[filtered_df["city"] == city]

    filtered_df = filtered_df[filtered_df["marks"] >= min_marks]

    # ================= TITLE =================
    st.title("🤖 AI Data Query Dashboard")
    st.caption("AI-powered analytics with real-time insights 🚀")

    # ================= KPI =================
    st.markdown("## 📊 Key Insights")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Students", len(filtered_df))
    col2.metric("Average Marks", round(filtered_df["marks"].mean(), 2))
    col3.metric("Highest Marks", filtered_df["marks"].max())
    col4.metric("Lowest Marks", filtered_df["marks"].min())

    # ================= AI CHAT =================
    st.markdown("## 🤖 AI Chat (Powered by GPT)")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Ask anything about your data")

    if st.button("Ask AI"):
        if user_input:

            data_context = filtered_df.to_string()

            prompt = f"""
You are a smart data analyst.

Dataset:
{data_context}

Question:
{user_input}

Give clear and short answer.
"""

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )

                answer = response.choices[0].message.content

            except Exception:
                answer = "⚠️ AI quota exceeded (API limit). Dashboard still works."

            st.session_state.chat_history.append((user_input, answer))

    for q, a in st.session_state.chat_history[::-1]:
        st.markdown(f'<div class="chat-user">🧑 {q}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-ai">🤖 {a}</div>', unsafe_allow_html=True)

    # ================= SMART AI =================
    st.markdown("## 🤖 Smart AI Assistant")

    student_query = st.text_input("Ask about a student (e.g. Priya)")

    if student_query:
        response = ai_agent(student_query, filtered_df)
        st.success(response)

    # ================= TABLE =================
    st.markdown("## 📋 Student Data")
    st.dataframe(filtered_df, use_container_width=True)

    # ================= VISUALS =================
    st.markdown("## 📊 Visual Dashboard")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Marks Distribution")
        st.bar_chart(filtered_df["marks"])

    with col2:
        st.subheader("Students by City")
        st.bar_chart(filtered_df["city"].value_counts())

    # PIE CHART
    st.subheader("City Distribution (Pie Chart)")

    city_counts = filtered_df["city"].value_counts()

    fig, ax = plt.subplots()
    ax.pie(city_counts, labels=city_counts.index, autopct="%1.1f%%")
    st.pyplot(fig)

    # ================= TOP STUDENTS =================
    st.markdown("## 🏆 Top 5 Performers")
    st.dataframe(filtered_df.sort_values(by="marks", ascending=False).head(5))

    # ================= SEARCH =================
    st.markdown("## 🔍 Quick Search")

    name_search = st.text_input("Search student by name")

    if name_search:
        result = filtered_df[
            filtered_df["name"].str.contains(name_search, case=False)
        ]
        st.dataframe(result)

    # ================= EXTRA =================
    st.markdown("## 🧠 Extra Insights")

    col11, col12 = st.columns(2)

    col11.subheader("Median Marks")
    col11.write(filtered_df["marks"].median())

    col12.subheader("Standard Deviation")
    col12.write(filtered_df["marks"].std())

    # ================= DOWNLOAD =================
    st.markdown("## ⬇ Download Data")

    csv = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="students.csv",
        mime="text/csv"
    )

    # ================= FOOTER =================
    st.markdown("---")
    st.markdown("Made with ❤️ by Anjala | AI Dashboard Project")

# ================== MAIN ==================
if not st.session_state.logged_in:
    login()
else:
    dashboard()