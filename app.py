import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from openai import OpenAI

# ================== CONFIG ==================
st.set_page_config(page_title="AI Dashboard", layout="wide")

# ================== OPENAI ==================
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    client = None

# ================== SESSION ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ================== USERS ==================
users = {
    "admin": "1234",
    "anjala": "pass123",
    "demo": "demo123"
}

# ================== DATA ==================
def load_data():
    data = {
        "name": ["Anjala", "Rahul", "Priya", "Amit", "Sneha", "Rohan", "Kiran", "Neha"],
        "age": [22, 23, 21, 24, 22, 23, 21, 22],
        "city": ["Pune", "Mumbai", "Pune", "Delhi", "Mumbai", "Pune", "Delhi", "Pune"],
        "marks": [85, 78, 92, 67, 88, 74, 81, 90]
    }
    df = pd.DataFrame(data)
    df["marks"] = pd.to_numeric(df["marks"], errors="coerce")
    return df

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
        return "❌ Student not found"

    city = student.iloc[0]["city"]
    marks = student.iloc[0]["marks"]
    weather = get_weather(city)

    if marks >= 85:
        insight = "🚀 Excellent performance"
    elif marks >= 70:
        insight = "👍 Good performance"
    elif marks >= 50:
        insight = "⚡ Average performance"
    else:
        insight = "📉 Needs improvement"

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

    st.markdown("""
    ### 🔑 Demo Credentials
    - admin / 1234  
    - anjala / pass123  
    - demo / demo123  
    """)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login Successful 🚀")
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
    st.sidebar.write("👤 " + st.session_state.username)
    st.sidebar.button("Logout", on_click=logout)

    df = load_data()

    # ================= FILTER =================
    st.sidebar.title("🔎 Filters")
    city = st.sidebar.selectbox("Select City", ["All"] + list(df["city"].unique()))
    min_marks = st.sidebar.slider("Minimum Marks", 0, 100, 50)

    filtered_df = df.copy()

    if city != "All":
        filtered_df = filtered_df[filtered_df["city"] == city]

    filtered_df = filtered_df[filtered_df["marks"] >= min_marks]

    # ================= TITLE =================
    st.title("🤖 AI Data Query Dashboard")
    st.caption("AI-powered analytics dashboard 🚀")
    st.info("Scroll down to explore all features 👇")

    # ================= KPI =================
    st.subheader("📊 Key Insights")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Students", len(filtered_df))
    col2.metric("Average Marks", round(filtered_df["marks"].mean(), 2))
    col3.metric("Highest Marks", filtered_df["marks"].max())
    col4.metric("Lowest Marks", filtered_df["marks"].min())

    st.markdown("---")

    # ================= AI CHAT =================
    st.subheader("🤖 AI Chat")

    user_input = st.text_input("Ask anything about your data")

    if st.button("Ask AI"):
        if user_input:
            try:
                if client:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": user_input}]
                    )
                    answer = response.choices[0].message.content
                else:
                    answer = "AI not configured"

            except:
                answer = "⚠️ AI quota exceeded"

            st.session_state.chat_history.append((user_input, answer))

    for q, a in st.session_state.chat_history[::-1]:
        st.write("🧑", q)
        st.write("🤖", a)

    st.markdown("---")

    # ================= SMART AI =================
    st.subheader("🤖 Smart Assistant")

    query = st.text_input("Ask about a student")

    if query:
        st.success(ai_agent(query, filtered_df))

    st.markdown("---")

    # ================= TABLE =================
    st.subheader("📋 Student Data")
    st.dataframe(filtered_df, use_container_width=True)

    st.markdown("---")

    # ================= VISUALS =================
    st.subheader("📊 Visual Dashboard")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Marks Distribution")
        st.bar_chart(filtered_df["marks"])

    with col2:
        st.subheader("City Distribution")
        st.bar_chart(filtered_df["city"].value_counts())

    # PIE CHART
    st.subheader("City Pie Chart")

    fig, ax = plt.subplots()
    ax.pie(filtered_df["city"].value_counts(),
           labels=filtered_df["city"].value_counts().index,
           autopct="%1.1f%%")
    st.pyplot(fig)

    st.markdown("---")

    # ================= TOP =================
    st.subheader("🏆 Top Performers")
    st.dataframe(filtered_df.sort_values(by="marks", ascending=False).head(5))

    st.markdown("---")

    # ================= SEARCH =================
    st.subheader("🔍 Search Student")

    search = st.text_input("Enter name")

    if search:
        result = filtered_df[filtered_df["name"].str.contains(search, case=False)]
        st.dataframe(result)

    st.markdown("---")

    # ================= EXTRA =================
    st.subheader("📈 Extra Insights")

    col1, col2 = st.columns(2)

    col1.write(f"Median: {filtered_df['marks'].median()}")
    col2.write(f"Std Dev: {filtered_df['marks'].std()}")
    st.markdown("---")

    # ================= FOOTER =================
    st.success("Project Ready for Submission ✅")

# ================== MAIN ==================
if not st.session_state.logged_in:
    login()
else:
    dashboard()