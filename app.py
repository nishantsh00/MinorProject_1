import streamlit as st
import sqlite3
import pandas as pd

# Database connection helper
def get_data(query, params=None):
    conn = sqlite3.connect(r"C:\Users\ASUS\student_data.db")  # Make sure your DB file is named correctly
    if params:
        df = pd.read_sql_query(query, conn, params=params)
    else:
        df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Set Streamlit config
st.set_page_config(page_title="Placement Eligibility App", layout="wide")

# Sidebar Navigation
st.sidebar.title("Home Page")
page = st.sidebar.radio("Go to", ["Eligibility Criteria", "Students Analytical Insights"])

# -------------------------------- PAGE 1: Eligibility Criteria --------------------------------
if page == "Eligibility Criteria":
    st.title(" Placement Eligibility Checker")
    st.subheader("Filter Students Based on Eligibility Criteria")

    # Sidebar filters
    placement_status = st.selectbox("Placement Status", ["All", "Ready", "Not Ready"])
    problems_solved = st.slider("Total Problems Solved", 25, 10, 60)
    communication_score = st.slider("Communication Score", 50, 100, 75)
    mock_interview_score = st.slider("Mock Interview Score", 40, 100, 60)
    internships_completed = st.slider("Internship Completed",1 , 3, 1)
    # SQL Query with dynamic filters
    query = """
    SELECT s.student_id, s.name, s.course_batch, s.city, p.problems_solved,
           ss.communication, pl.placement_status, pl.mock_interview_score, pl.internships_completed
    FROM Student_Table s
    JOIN programming_table p ON s.student_id = p.student_id
    JOIN softskills_table ss ON s.student_id = ss.student_id
    JOIN placements_table pl ON s.student_id = pl.student_id
    WHERE p.problems_solved >= ?
      AND ss.communication >= ?
    """
    params = [problems_solved, communication_score]

    if placement_status != "All":
        query += " AND pl.placement_status = ?"
        params.append(placement_status)

    df = get_data(query, params=params)

    st.write("### Eligible Students")
    st.write(f"Filtered for: Problems Solved ≥ {problems_solved}, Communication Score ≥ {communication_score}, Placement Status = {placement_status}")
    st.dataframe(df)

# -------------------------------- PAGE 2: Students Analytical Insights --------------------------------
elif page == "Students Analytical Insights":
    st.title(" Student Performance & Placement Insights")

    queries = {
        "1. Top 50 Students by Mock Interview Score": """
            SELECT s.student_id, s.name,s.course_batch, pl.mock_interview_score
            FROM Student_Table s
            JOIN placements_table pl ON s.student_id = pl.student_id
            ORDER BY pl.mock_interview_score DESC LIMIT 50
        """,
        "2. Students Who Completed Certificates More Than 2": """
            SELECT s.student_id, s.name, s.course_batch, p.certifications_earned
            FROM Student_Table s
            JOIN programming_table p ON s.student_id = p.student_id
            WHERE p.certifications_earned > 2
        """,
        "3. Progamming Language Used By Students": """
            SELECT s.student_id, s.name AS student_name, p.language
            FROM programming_table p 
            JOIN Student_Table s ON p.student_id = s.student_id
            WHERE p.language IS NOT NULL
            ORDER BY s.name
            """,
        
        "4. Top 50 Soft Skill Performers": """
            SELECT s.student_id, s.name, s.course_batch,
                   (ss.communication + ss.teamwork + ss.presentation + ss.leadership + ss.critical_thinking + ss.interpersonal_skills) AS total_soft_skills
            FROM Student_Table s
            JOIN softskills_table ss ON s.student_id = ss.student_id
            ORDER BY total_soft_skills DESC LIMIT 50
            """,
        "5. Average Placement Package by Batch": """
            SELECT s.course_batch, AVG(pl.placement_package) AS avg_package
            FROM Student_Table s
            JOIN placements_table pl ON s.student_id = pl.student_id
            WHERE pl.placement_status = 'Ready'
            GROUP BY s.course_batch
            """,
         "6. Placement Status Count": """
             SELECT placement_status, COUNT(*) AS total_students
             FROM placements_table 
             GROUP BY placement_status;
             """,
        "7. Students Who Completed More Than 1 Internship": """
            SELECT s.student_id, s.name, s.course_batch, pl.internships_completed
            FROM Student_Table s
            JOIN placements_table pl ON s.student_id = pl.student_id
            WHERE pl.internships_completed > 1
            """,
        "8. Companies That Have Placed Students": """
            SELECT DISTINCT company_name
            FROM placements_table
            WHERE placement_status = 'Ready' AND company_name IS NOT NULL;
            """,
        "9. Students with Strong Leadership Skills (>75)": """
            SELECT s.student_id, s.name, s.course_batch, ss.leadership
            FROM Student_Table s
            JOIN softskills_table ss ON s.student_id = ss.student_id
            WHERE ss.leadership > 75
            """,
        "10. Students Eligible for Placement (User Eligibility Criteria)": """
             SELECT s.student_id, s.name,s.course_batch, p.problems_solved, ss.communication, pl.mock_interview_score
             FROM Student_Table s
             JOIN programming_table p ON s.student_id = p.student_id
             JOIN softskills_table ss ON s.student_id = ss.student_id
             JOIN placements_table pl ON s.student_id = pl.student_id
             WHERE 
             p.problems_solved >= 50 AND
             ss.communication >= 75 AND
             pl.mock_interview_score >= 70 
             """,

    }

    selected_query = st.selectbox("Select an Insight", list(queries.keys()))
    result_df = get_data(queries[selected_query])

    st.write("### Result")
    st.dataframe(result_df)
