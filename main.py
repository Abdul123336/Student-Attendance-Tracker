import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from utils import (
    initialize_session_state,
    calculate_attendance_percentage,
    create_attendance_chart,
    validate_student_data
)

# Page configuration
st.set_page_config(
    page_title="Student Attendance Tracker",
    page_icon="📚",
    layout="wide"
)

# Load custom CSS
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state
initialize_session_state()

# Main header
st.markdown("""
    <div class='header-container'>
        <h1>Student Attendance Tracker</h1>
    </div>
""", unsafe_allow_html=True)

# Navigation bar
st.markdown("<div class='navbar'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    manage_students = st.button("Student's List", key="nav_manage", use_container_width=True)
with col2:
    take_attendance = st.button("Mark Attendance", key="nav_attendance", use_container_width=True)
with col3:
    view_statistics = st.button("View Statistics", key="nav_stats", use_container_width=True)

# Initialize page state if not exists
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Student's List"

# Update current page based on navigation
if manage_students:
    st.session_state.current_page = "Student's List"
elif take_attendance:
    st.session_state.current_page = "Mark Attendance"
elif view_statistics:
    st.session_state.current_page = "View Statistics"

st.markdown("</div>", unsafe_allow_html=True)

# Page content
if st.session_state.current_page == "Student's List":
    st.header("Student's List")

    # Add new student form
    with st.form("add_student_form"):
        st.subheader("Add New Student")
        student_name = st.text_input("Student Name")
        class_name = st.text_input("Class")
        submit_button = st.form_submit_button("Add Student")

        if submit_button:
            is_valid, error_message = validate_student_data(student_name, class_name)
            if is_valid:
                new_student = pd.DataFrame({
                    'student_id': [len(st.session_state.students) + 1],
                    'name': [student_name],
                    'class': [class_name]
                })
                st.session_state.students = pd.concat([st.session_state.students, new_student], ignore_index=True)
                st.success("Student added successfully!")
            else:
                st.error(error_message)

    # Display student list
    if not st.session_state.students.empty:
        st.subheader("Student List")

        # Create a copy of students DataFrame with attendance percentage
        display_df = st.session_state.students.copy()
        display_df['attendance_percentage'] = display_df['student_id'].apply(
            lambda x: f"{calculate_attendance_percentage(x):.1f}%"
        )

        # Rename columns for display
        display_df.columns = ['ID', 'Name', 'Class', 'Attendance Rate']

        # Display the formatted DataFrame
        st.dataframe(
            display_df,
            column_config={
                "ID": st.column_config.NumberColumn(
                    "ID",
                    help="Student ID"
                ),
                "Attendance Rate": st.column_config.TextColumn(
                    "Attendance Rate",
                    help="Student's attendance percentage",
                    width="medium"
                )
            },
            use_container_width=True
        )
    else:
        st.info("No students registered yet.")

elif st.session_state.current_page == "Mark Attendance":
    st.header("Mark Attendance")

    if st.session_state.students.empty:
        st.warning("Please add students first.")
    else:
        date = st.date_input("Select Date", datetime.now())

        with st.form("attendance_form"):
            st.subheader(f"Mark Attendance for {date}")

            attendance_data = []
            for _, student in st.session_state.students.iterrows():
                status = st.selectbox(
                    f"{student['name']} ({student['class']})",
                    options=['Present', 'Absent'],
                    key=f"attendance_{student['student_id']}"
                )
                attendance_data.append({
                    'date': date,
                    'student_id': student['student_id'],
                    'status': status
                })

            submit_attendance = st.form_submit_button("Submit Attendance")

            if submit_attendance:
                new_attendance = pd.DataFrame(attendance_data)
                st.session_state.attendance = pd.concat(
                    [st.session_state.attendance, new_attendance],
                    ignore_index=True
                )
                st.success("Attendance recorded successfully!")

else:  # View Statistics
    st.header("Attendance Statistics")

    if st.session_state.students.empty:
        st.warning("No students registered yet.")
    else:
        # Overall statistics
        st.subheader("Overall Statistics")

        col1, col2 = st.columns(2)

        with col1:
            total_students = len(st.session_state.students)
            st.metric("Total Students", total_students)

        with col2:
            if not st.session_state.attendance.empty:
                overall_attendance = (
                    len(st.session_state.attendance[st.session_state.attendance['status'] == 'Present']) /
                    len(st.session_state.attendance) * 100
                )
                st.metric("Overall Attendance Rate", f"{overall_attendance:.1f}%")
            else:
                st.metric("Overall Attendance Rate", "0%")

        # Individual student statistics
        st.subheader("Individual Student Statistics")

        selected_student = st.selectbox(
            "Select Student",
            options=st.session_state.students['student_id'].tolist(),
            format_func=lambda x: st.session_state.students[
                st.session_state.students['student_id'] == x
            ]['name'].iloc[0]
        )

        if selected_student:
            student_data = st.session_state.students[
                st.session_state.students['student_id'] == selected_student
            ].iloc[0]

            attendance_percentage = calculate_attendance_percentage(selected_student)

            st.markdown(f"""
                <div class='student-card'>
                    <h3>{student_data['name']}</h3>
                    <p>Class: {student_data['class']}</p>
                    <p>Attendance Rate: {attendance_percentage:.1f}%</p>
                </div>
            """, unsafe_allow_html=True)

            # Attendance history chart
            attendance_chart = create_attendance_chart(selected_student)
            if attendance_chart:
                st.plotly_chart(attendance_chart, use_container_width=True)
            else:
                st.info("No attendance records available for this student.")