from flask import Flask, render_template, request, session, redirect, url_for, make_response
import qrcode
import os
import json
import pandas as pd
from fpdf import FPDF
from datetime import datetime, timedelta
import hashlib



app = Flask(__name__)
app.secret_key = 'your_secret_key'  # لتخزين الجلسات (sessions)

# مسار حفظ الصور المولدة
qr_directory = os.path.join(app.static_folder, 'qr_codes')
if not os.path.exists(qr_directory):
    os.makedirs(qr_directory)

def generate_token(subject, section, secret_key='your_secret_key'):
    current_time = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    token_string = f"{subject}_{section}_{current_time}_{secret_key}"
    return hashlib.sha256(token_string.encode()).hexdigest()


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    subject = request.form['subject']
    section = request.form['section']

    if subject and section:
        # إنشاء توقيع فريد للرابط
        token = generate_token(subject, section)
        creation_time = datetime.now()  # حفظ توقيت الإنشاء

        # تخزين التوقيت المرتبط بـ token في الجلسة
        session['tokens'] = session.get('tokens', {})
        session['tokens'][token] = creation_time.strftime('%Y-%m-%d %H-%M-%S')

        student_url = url_for('student_by_token', token=token, _external=True)

        # توليد QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(student_url)
        qr.make(fit=True)

        qr_image_path = os.path.join(qr_directory, f"qr_{token}.png")
        qr.make_image(fill='black', back_color='white').save(qr_image_path)

        return render_template('index.html', qr_image_path=f'static/qr_codes/qr_{token}.png', student_url=student_url)

    return "Please provide subject and section."

@app.route('/stop', methods=['POST'])
def stop():
    return render_template('index.html', show_download=True)

@app.route('/download_excel')
def download_excel():
    students = session.get('students', [])
    if not students:
        return "This service not available right now"

    # إنشاء ملف Excel
    df = pd.DataFrame()

    # إضافة بيانات الطلاب إلى DataFrame
    for student in students:
        df = df.append({
            'Name': student.get('name'),
            'ID': student.get('id'),
            'Subject': student.get('subject'),
            'Section': student.get('section')
        }, ignore_index=True)

    # تحضير اسم الملف
    subject = session.get('subject', 'Unknown_Subject')
    section = session.get('section', 'Unknown_Section')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_file_name = f"attendance_{subject}_{section}_{timestamp}.xlsx"

    # مسار حفظ الملف
    excel_file_path = os.path.join(qr_directory, excel_file_name)

    # حفظ البيانات في ملف Excel
    df.to_excel(excel_file_path, index=False)

    # مسح بيانات الطلاب من الجلسة بعد التنزيل
    session['students'] = []

    # إعادة توجيه المستخدم لتحميل الملف
    return redirect(url_for('static', filename=f'qr_codes/{excel_file_name}'))
    students = session.get('students', [])
    if not students:
        return "No attendance data available to download."

    # Convert students data to DataFrame with the correct structure
    data = []
    for student in students:
        data.append({
            'Name': student.get('name'),
            'ID': student.get('id'),
            'Subject': student.get('subject'),
            'Section': student.get('section')
        })

    df = pd.DataFrame(data)

    # Prepare filenames
    subject = session.get('subject', 'Unknown_Subject')
    section = session.get('section', 'Unknown_Section')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_file_name = f"attendance_{subject}_{section}_{timestamp}.xlsx"

    # Excel file path
    excel_file_path = os.path.join('path_to_save_excel', excel_file_name)

    # Save to Excel
    df.to_excel(excel_file_path, index=False)

    # Provide download link for the Excel file
    return f"""
    Excel file has been generated. 
    <a href="{url_for('static', filename=f'qr_codes/{excel_file_name}')}">Download Excel</a>
    """

@app.route('/download_pdf')
def download_pdf():

    # استرداد بيانات الطلاب من الجلسة
    students = session.get('students', [])
    if not students:
        return "No attendance data available to download."

    # إنشاء ملف PDF
    pdf = FPDF()
    pdf.set_left_margin(10)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # إضافة عنوان التقرير
    pdf.cell(200, 10, txt="Attendance Report", ln=True, align="C")
    pdf.ln(10)

    # إضافة بيانات الطلاب إلى التقرير
    for student in students:
        pdf.cell(200, 10, txt=f"Name: {student['name']}, ID: {student['id']}, Subject: {student['subject']}, Section: {student['section']}", ln=True)

    # إنشاء اسم فريد للملف باستخدام اسم المادة والرقم والتاريخ
    subject = session.get('subject', 'Unknown_Subject')
    section = session.get('section', 'Unknown_Section')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # تاريخ ووقت فريد
    pdf_file_name = f"attendance_{subject}_{section}_{timestamp}.pdf"
    pdf_file_path = os.path.join(qr_directory, pdf_file_name)

    # حفظ التقرير في ملف جديد
    pdf.output(pdf_file_path)

    # مسح بيانات الطلاب من الجلسة بعد التنزيل
    session['students'] = []  # مسح قائمة الطلاب في الجلسة

    # إعادة توجيه المستخدم لتحميل الملف الجديد
    return redirect(url_for('static', filename=f'qr_codes/{pdf_file_name}'))

    # استرداد بيانات الطلاب من الجلسة
    students = session.get('students', [])
    if not students:
        return "No attendance data available to download."

    # إنشاء ملف PDF
    pdf = FPDF()
    pdf.set_left_margin(10)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # عنوان التقرير
    pdf.cell(200, 10, txt="Attendance Report", ln=True, align="C")
    pdf.ln(10)

    # إضافة بيانات الطلاب إلى التقرير
    for student in students:
        pdf.cell(200, 10, txt=f"Name: {student['name']}, ID: {student['id']}, Subject: {student['subject']}, Section: {student['section']}", ln=True)

    # إنشاء اسم فريد للملف باستخدام اسم المادة والرقم والتاريخ
    subject = session.get('subject', 'Unknown_Subject')
    section = session.get('section', 'Unknown_Section')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_file_name = f"attendance_{subject}_{section}_{timestamp}.pdf"
    pdf_file_path = os.path.join(qr_directory, pdf_file_name)

    pdf.output(pdf_file_path)

    return redirect(url_for('static', filename=f'qr_codes/{pdf_file_name}'))
    students = session.get('students', [])

    pdf = FPDF()
    pdf.set_left_margin(10)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Attendance Report", ln=True, align="C")
    pdf.ln(10)

    for student in students:
        pdf.cell(200, 10, txt=f"Name: {student['name']}, ID: {student['id']}, Subject: {student['subject']}, Section: {student['section']}", ln=True)

    pdf_file_path = os.path.join(qr_directory, 'attendance.pdf')
    pdf.output(pdf_file_path)

    return redirect(url_for('static', filename=f'qr_codes/attendance.pdf'))

@app.route('/student/<subject>/<section>', methods=['GET'])
def student(subject, section):
    return render_template('student.html', subject=subject, section=section)

@app.route('/submit_attendance', methods=['POST'])
def submit_attendance():
    student_name = request.form['student_name']
    student_id = request.form['student_id']
    subject = request.form['subject']
    section = request.form['section']

    # التحقق من الكوكيز
    last_attendance_time = request.cookies.get(f'attendance_{student_id}')
    
    now = datetime.now()

    if last_attendance_time:
        # تحويل الوقت المخزن في الكوكيز إلى كائن datetime
        last_attendance_time = datetime.strptime(last_attendance_time, "%Y-%m-%d %H:%M:%S")
        # التحقق مما إذا مرت 30 دقيقة
        if now - last_attendance_time < timedelta(minutes=30):
            return "You have already submitted attendance recently. Please wait"

    # إذا لم يتم التسجيل مؤخرًا، أضف السجل
    students = session.get('students', [])
    students.append({'name': student_name, 'id': student_id, 'subject': subject, 'section': section})
    session['students'] = students

    # تخزين الكوكيز
    response = make_response("Attendance Submitted Successfully!")
    response.set_cookie(f'attendance_{student_id}', now.strftime("%Y-%m-%d %H:%M:%S"), max_age=900)  # الكوكيز صالح لمدة 15 دقيقة بس

    return response

@app.route('/student/<token>', methods=['GET'])
def student_by_token(token):
    tokens = session.get('tokens', {})
    creation_time_str = tokens.get(token)

    if not creation_time_str:
        return "Invalid or expired token."

    try:
        # تحويل التوقيت إلى كائن datetime
        creation_time = datetime.strptime(creation_time_str, '%Y-%m-%d %H-%M-%S')
        now = datetime.now()

        # التحقق من انتهاء صلاحية التوكن
        if now - creation_time > timedelta(seconds=45):
            return "This link has expired. Please refresh the QR Code."
    except ValueError:
        return "Invalid token format."

    return render_template('student.html', token=token)

@app.route('/refresh_qr', methods=['GET'])
def refresh_qr():
    subject = session.get('subject', 'default_subject')
    section = session.get('section', 'default_section')

    if subject and section:
        token = generate_token(subject, section)
        now = datetime.now()
        student_url = url_for('student_by_token', token=token, _external=True)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(student_url)
        qr.make(fit=True)

        qr_image_path = os.path.join(qr_directory, f"qr_{token}.png")
        qr.make_image(fill='black', back_color='white').save(qr_image_path)

        # تحديث الجلسة بالتوكن والتوقيت الجديد
        session['tokens'] = session.get('tokens', {})
        session['tokens'][token] = now.strftime('%Y-%m-%d %H-%M-%S')

        return {
            'qr_image': f'static/qr_codes/qr_{token}.png',
            'student_url': student_url
        }
    return {'error': 'Subject and section are required'}, 400


if __name__ == '__main__':
    app.run(debug=True)