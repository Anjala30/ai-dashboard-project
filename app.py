import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from openai import OpenAI

# ================= CONFIG =================
st.set_page_config(page_title="AI Dashboard", layout="wide")

# ================= OPENAI =================
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    client = None

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ================= USERS =================
users = {
    "admin": "1234",
    "anjala": "pass123",
    "demo": "demo123"
}

# ================= DATA =================
def load_data():
    data = {
        "name": ["Anjala", "Rahul", "Priya", "Amit", "Sneha", "Rohan", "Kiran"],
        "age": [22, 23, 21, 24, 22, 23, 21],
        "city": ["Pune", "Mumbai", "Pune", "Delhi", "Mumbai", "Pune", "Delhi"],
        "marks": [85, 78, 92, 67, 88, 74, 81]
    }
    return pd.DataFrame(data)

# ================= WEATHER =================
def get_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid=67c4117ca275c8948ddbc80f84554e42&units=metric"
        data = requests.get(url).json()
        return f"{data['weather'][0]['description']}, {data['main']['temp']}°C"
    except:
        return "N/A"

# ================= AI AGENT =================
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

# ================= LOGIN =================
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
            st.success("Login successful 🚀")
            st.rerun()
        else:
            st.error("Invalid credentials ❌")

# ================= LOGOUT =================
def logout():
    st.session_state.logged_in = False
    st.rerun()

# ================= DASHBOARD =================
def dashboard():

    # Sidebar
    st.sidebar.success("AI Dashboard Live 🚀")
    st.sidebar.write(f"👤 {st.session_state.username}")
    st.sidebar.button("Logout", on_click=logout)

    df = load_data()

    # Filters
    st.sidebar.title("🔎 Filters")
    city = st.sidebar.selectbox("Select City", ["All"] + list(df["city"].unique()))
    min_marks = st.sidebar.slider("Minimum Marks", 0, 100, 50)

    filtered_df = df.copy()

    if city != "All":
        filtered_df = filtered_df[filtered_df["city"] == city]

    filtered_df = filtered_df[filtered_df["marks"] >= min_marks]

    # Title
    st.title("🤖 AI Data Dashboard")
    st.caption("Real-time analytics + AI insights 🚀")

    # KPI
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Students", len(filtered_df))
    col2.metric("Avg Marks", round(filtered_df["marks"].mean(), 2))
    col3.metric("Max Marks", filtered_df["marks"].max())
    col4.metric("Min Marks", filtered_df["marks"].min())

    st.markdown("---")

    # ================= AI CHAT =================
    st.subheader("🤖 AI Chat")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Ask something")

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
                answer = "⚠️ AI limit reached"

            st.session_state.chat_history.append((user_input, answer))

    for q, a in st.session_state.chat_history[::-1]:
        st.write("🧑", q)
        st.write("🤖", a)

    st.markdown("---")

    # ================= SMART AI =================
    st.subheader("🤖 Smart Assistant")

    query = st.text_input("Enter student name")

    if query:
        st.success(ai_agent(query, filtered_df))

    st.markdown("---")

    # ================= TABLE =================
    st.subheader("📋 Data Table")
    st.dataframe(filtered_df)

    st.markdown("---")

    # ================= CHARTS =================
    st.subheader("📊 Charts")

    col1, col2 = st.columns(2)

    with col1:
        st.bar_chart(filtered_df["marks"])

    with col2:
        st.bar_chart(filtered_df["city"].value_counts())

    # Pie
    fig, ax = plt.subplots()
    ax.pie(filtered_df["city"].value_counts(), labels=filtered_df["city"].value_counts().index, autopct="%1.1f%%")
    st.pyplot(fig)

    st.markdown("---")

    # Top Students
    st.subheader("🏆 Top Students")
    st.dataframe(filtered_df.sort_values(by="marks", ascending=False).head(5))

    st.markdown("---")

    # Search
    st.subheader("🔍 Search")

    search = st.text_input("Search name")

    if search:
        result = filtered_df[filtered_df["name"].str.contains(search, case=False)]
        st.dataframe(result)

    st.markdown("---")

    # Stats
    st.subheader("📈 Extra Stats")

    col1, col2 = st.columns(2)

    col1.write(f"Median: {filtered_df['marks'].median()}")
    col2.write(f"Std Dev: {filtered_df['marks'].std()}")

    st.markdown("---")
    st.success("Project Ready ✅")

# ================= MAIN =================
if not st.session_state.logged_in:
    login()
else:
    dashboard()