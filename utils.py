import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if 'students' not in st.session_state:
        st.session_state.students = pd.DataFrame({
            'student_id': [],
            'name': [],
            'class': []
        })

    if 'attendance' not in st.session_state:
        st.session_state.attendance = pd.DataFrame({
            'date': [],
            'student_id': [],
            'status': []
        })

def calculate_attendance_percentage(student_id):
    """Calculate attendance percentage for a specific student"""
    if len(st.session_state.attendance) == 0:
        return 0.0

    student_attendance = st.session_state.attendance[
        st.session_state.attendance['student_id'] == student_id
    ]

    if len(student_attendance) == 0:
        return 0.0

    present_count = len(student_attendance[student_attendance['status'] == 'Present'])
    total_count = len(student_attendance)

    return (present_count / total_count) * 100

def create_attendance_chart(student_id):
    """Create attendance visualization for a student"""
    student_attendance = st.session_state.attendance[
        st.session_state.attendance['student_id'] == student_id
    ].copy()

    if len(student_attendance) == 0:
        return None

    student_attendance['date'] = pd.to_datetime(student_attendance['date'])
    student_attendance = student_attendance.sort_values('date')

    fig = px.line(
        student_attendance,
        x='date',
        y='status',
        title='Attendance History',
        color_discrete_map={'Present': '#4CAF50', 'Absent': '#FFC107'}
    )

    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Status',
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    return fig

def validate_student_data(name, class_name):
    """Validate student input data"""
    if not name.strip():
        return False, "Student name cannot be empty"
    if not class_name.strip():
        return False, "Class name cannot be empty"
    return True, ""