from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

report_data = {
    'project_name': 'Face Recognition-Based Employee Access Monitoring and Admin Dashboard System',
    'intern_name': 'Aryan Raj',
    'reporting_period': '04/05/2026 to 05/07/2026',
    'organization': 'Grasim Chemicals, Rehla Division – Aditya Birla Group',
    'objective': 'The project was intended to design and develop a smart face recognition-based access monitoring system for a company environment. The main objective was to automate employee identification, detect unauthorized persons, and provide an admin dashboard for real-time monitoring and alerting. The system aimed to improve workplace security, reduce manual verification, and provide a modern digital solution for access control.',
    'work_completed': 'During the internship, I worked on developing a complete prototype of the system with both backend and frontend components. The major tasks completed included: designing the overall architecture for employee registration, face image storage, and access monitoring; implementing employee registration with employee ID, name, and allowed area details; developing a training pipeline to generate facial embeddings from uploaded employee images; building live camera-based recognition for identifying employees in real time; creating an admin web interface for monitoring the camera feed and viewing alerts; implementing unauthorized access alerting and access logging; testing the system locally with multiple employee profiles and camera-based recognition.',
    'key_outcomes': 'The project successfully delivered a working prototype of an AI-based security monitoring system. Key outcomes included: a functional employee registration system with stored employee data; a trained recognition model capable of identifying registered employees from live camera input; an admin dashboard for live monitoring and alert visibility; a working alert mechanism for unauthorized or unknown persons; the system was tested successfully with multiple employee records and live recognition scenarios.',
    'challenges': 'Several challenges were encountered during development: face recognition accuracy was affected by image quality and lighting conditions; compatibility issues arose while integrating the face recognition libraries with the Python environment; the live camera monitoring required careful handling of video processing and real-time updates. These challenges were addressed by improving image preprocessing and face detection logic, using a more stable and compatible implementation approach for facial embedding generation, and structuring the web dashboard to support live feed display and alert updates efficiently.',
    'learnings': 'The internship provided valuable learning in several areas: Python programming and software development for AI-based applications; computer vision and face recognition concepts; web development using Flask and HTML/CSS for the admin dashboard; database handling with SQLite and employee data management; debugging real-world technical issues and improving system reliability; understanding how technology can be applied to industrial and security-related environments.',
    'recommendations': 'Cedur should continue the development of this system by focusing on the following next steps: improve recognition accuracy by using better-quality camera input and more diverse employee datasets; integrate the system with real access control hardware such as door locks or turnstiles; add email/SMS notifications for administrators in real time; enhance the dashboard with more analytics, employee activity history, and role-based access; deploy the solution on a more robust server environment for real-world use.',
    'executive_summary': 'This internship project focused on developing a face recognition-based employee access monitoring system aimed at improving workplace security. The solution included employee registration, facial embedding generation, live camera recognition, access logging, and an admin dashboard for real-time monitoring. The prototype was successfully implemented and tested locally, demonstrating its ability to identify registered employees and flag unauthorized access attempts. The project provided practical experience in AI, computer vision, web development, and security system design. It holds strong potential for further development into a scalable and industrial-grade access control solution.'
}

doc = Document()
doc.add_heading('Internship Project Report – Summary', level=1)
doc.add_paragraph(f"Project Name: {report_data['project_name']}")
doc.add_paragraph(f"Intern Name: {report_data['intern_name']}")
doc.add_paragraph(f"Reporting Period: {report_data['reporting_period']}")
doc.add_paragraph(f"Organization: {report_data['organization']}")

def add_section(title, content):
    doc.add_heading(title, level=2)
    doc.add_paragraph(content)

add_section('1. Project Objective', report_data['objective'])
add_section('2. Work Completed', report_data['work_completed'])
add_section('3. Key Outcomes', report_data['key_outcomes'])
add_section('4. Challenges & Solutions', report_data['challenges'])
add_section('5. Learnings', report_data['learnings'])
add_section('6. Recommendations / Next Steps', report_data['recommendations'])
add_section('7. Executive Summary (3–5 sentences)', report_data['executive_summary'])

docx_path = 'Internship_Project_Report_Aryan_Raj.docx'
doc.save(docx_path)

pdf_path = 'Internship_Project_Report_Aryan_Raj.pdf'
canvas_obj = canvas.Canvas(pdf_path, pagesize=letter)
width, height = letter
line_height = 14
x = 40
y = height - 40
canvas_obj.setFont('Helvetica-Bold', 16)
canvas_obj.drawString(x, y, 'Internship Project Report – Summary')
y -= 30
canvas_obj.setFont('Helvetica', 12)
for key in ['project_name', 'intern_name', 'reporting_period', 'organization']:
    canvas_obj.drawString(x, y, f"{key.replace('_', ' ').title()}: {report_data[key]}")
    y -= line_height

y -= 10
for title, field in [
    ('1. Project Objective', 'objective'),
    ('2. Work Completed', 'work_completed'),
    ('3. Key Outcomes', 'key_outcomes'),
    ('4. Challenges & Solutions', 'challenges'),
    ('5. Learnings', 'learnings'),
    ('6. Recommendations / Next Steps', 'recommendations'),
    ('7. Executive Summary (3–5 sentences)', 'executive_summary')
]:
    canvas_obj.setFont('Helvetica-Bold', 12)
    canvas_obj.drawString(x, y, title)
    y -= line_height
    canvas_obj.setFont('Helvetica', 11)
    text = report_data[field]
    for paragraph in text.split('. '):
        if not paragraph.strip():
            continue
        line = paragraph.strip()
        canvas_obj.drawString(x + 10, y, line)
        y -= line_height
        if y < 80:
            canvas_obj.showPage()
            y = height - 40
            canvas_obj.setFont('Helvetica', 11)
    y -= 10
canvas_obj.save()
print('Generated files:', docx_path, pdf_path)
