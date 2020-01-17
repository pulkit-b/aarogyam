from flask import Flask,render_template,request,flash,session,redirect,make_response,jsonify
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
import hashlib
import random
import requests
import datetime
import json

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'aarogyam'

mysql = MySQL(app)


app.config['MAIL_SERVER']='smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'pulkit.b@outlook.com'
app.config['MAIL_PASSWORD'] = '@0409Pulkit'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/hos_reg')
def hos_reg():
    return render_template('hos_reg.html')

@app.route('/staff_reg')
def staff_reg():
    return render_template('staff_reg.html')

@app.route('/reception')
def receptionist():
	if 'Relationship_Number' in session:
		userrelationshipnumber = session['Relationship_Number']
		cursor = mysql.connection.cursor()
		sql = "SELECT Hos_Relationship_Number,Staff_Relationship_Number,Staff_Name FROM aarogyam_staff_details_nptrun WHERE Staff_Relationship_Number=%s"
		sql_where = (userrelationshipnumber,)
		cursor.execute(sql, sql_where)
		row = cursor.fetchone()
		if row:
			sql = "SELECT Hos_Name FROM aarogyam_hos_reg_nptrun WHERE Hos_Relationship_Number=%s"
			sql_where = (row['Hos_Relationship_Number'],)
			cursor.execute(sql, sql_where)
			roww = cursor.fetchone()
			username = row['Staff_Name']
			hos_name = roww['Hos_Name']
			hrn = str(row['Hos_Relationship_Number'])
			n = username[0].upper() 
			return render_template('reception.html', n=n,hrn = hrn, userrelationshipnumber=userrelationshipnumber, username=username, hos_name=hos_name)
		else:
			return redirect('/')
	else:
		return redirect('/')

@app.route('/admin')
def admin():
	if 'Relationship_Number' in session:
		userrelationshipnumber = session['Relationship_Number']
		cursor = mysql.connection.cursor()
		sql = "SELECT * FROM aarogyam_user_auth_nptrun WHERE User_Relationship_Number=%s"
		sql_where = (userrelationshipnumber,)
		cursor.execute(sql, sql_where)
		row = cursor.fetchone()
		catogery = str(row['User_Category'])
		print(catogery)
		if catogery == '1':
			sql = "SELECT Hos_Name FROM aarogyam_hos_reg_nptrun WHERE Hos_Relationship_Number=%s"
			sql_where = (userrelationshipnumber,)
			cursor.execute(sql, sql_where)
			row = cursor.fetchone()
			username = row['Hos_Name']
			return render_template('admin.html', userrelationshipnumber=userrelationshipnumber, username=username)
		else:
			return redirect('/')
	else:
		return redirect('/')

@app.route('/staff-entry-submit', methods=['GET', 'POST'])
def staffentrysubmit():
	if 'Relationship_Number' in session:
		username = session['Relationship_Number']
	if request.method == "POST":
		userDetails = request.form
		Staff_Name = userDetails['Staff_Name']
		Staff_Designation = userDetails['Staff_Designation']
		Staff_Email = userDetails['Staff_email']
		Staff_Mobile = userDetails['Staff_mobile']
		Staff_Password = 'NPT' + str(random.randrange(5, 10**3))
		Staff_Profile_Updation = '0' 
		Hashed_Password =hashlib.md5(Staff_Password.encode()).hexdigest()
		Reg_Time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		Staff_Relationship_Number = 'NPT' + str(random.randrange(1, 10**4)) + Staff_Name[:3].upper()
		Designation = ''
		if (Staff_Designation == '2') or (Staff_Designation == '3') or (Staff_Designation == '4') or (Staff_Designation == '5') or (Staff_Designation == '6'):
			Designation = '2'
		elif (Staff_Designation == '7') or (Staff_Designation == '8') or (Staff_Designation == '9') or (Staff_Designation == '10') or (Staff_Designation == '11'):
			Designation = '3'
		elif (Staff_Designation == '12'):
			Designation = '4'
		elif (Staff_Designation == '13'):
			Designation = '5'
		elif (Staff_Designation == '15'):
			Designation = '6'
		elif (Staff_Designation == '16'):
			Designation = '7'
		else:
			Designation = '8'
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO aarogyam_staff_details_nptrun(Hos_Relationship_Number, Staff_Relationship_Number, Staff_Name, Staff_Designation, Staff_Email, Staff_Mobile, Staff_Profile_Updation) VALUES (%s,%s,%s,%s,%s,%s,%s)", (username, Staff_Relationship_Number, Staff_Name, Staff_Designation, Staff_Email, Staff_Mobile, Staff_Profile_Updation,))
		cur.execute("INSERT INTO aarogyam_user_auth_nptrun(User_Relationship_Number,User_Password,User_Category,User_Date_Reg) VALUES (%s,%s,%s,%s)", (Staff_Relationship_Number,Hashed_Password,Designation,Reg_Time,))
		mysql.connection.commit()
		msg = Message('Hello' + ' ' + Staff_Name, sender = 'pulkit.b@outlook.com', recipients = [Staff_Email])
		msg.html = render_template('sent_password.html', Hos_Password=Staff_Password, Hos_Relationship_Number=Staff_Relationship_Number)
		mail.send(msg)
		return jsonify({'success' : 'Mail Sent'})
	else:
		return jsonify({'error' : 'Error'})


@app.route('/opd_registration')
def opd_registration():
    return render_template('opd_reg.html')

@app.route('/room_reg')
def room_reg():
    return render_template('roomreg.html')

@app.route('/ipd_registration')
def ipd_registration():
    return render_template('ipd_reg.html')

@app.route('/beddetail')
def bedetail():
    return render_template('beddetail.html')

@app.route('/medis', methods=['POST'])
def medis():
	query = "%" + request.args['query'] +"%"
	cursor = mysql.connection.cursor()
	sql = "SELECT mname FROM aarogyam_medisearch_nptrun WHERE mname LIKE %s"
	sql_where = (query,)
	cursor.execute(sql, sql_where)
	row = cursor.fetchall()
	if row:
		resp = jsonify(row) 
		print(row)
		resp.status_code = 200
		return resp
	else:
		resp = jsonify({'error' : 'Mail Error'})
		resp.status_code = 200
		return resp

# @app.route('/waysms')
# def waysms():
# 	q=way2sms.sms('9713054321','Pulkit0409')
# 	q.send( '7230000797', 'hello' )
# 	return 'done'

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/doctor')
def doctor():
	if 'Relationship_Number' in session:
		userrelationshipnumber = session['Relationship_Number']
		cursor = mysql.connection.cursor()
		sql = "SELECT Hos_Relationship_Number,Staff_Relationship_Number,Staff_Name FROM aarogyam_staff_details_nptrun WHERE Staff_Relationship_Number=%s"
		sql_where = (userrelationshipnumber,)
		cursor.execute(sql, sql_where)
		row = cursor.fetchone()
		if row:
			sql = "SELECT Hos_Name FROM aarogyam_hos_reg_nptrun WHERE Hos_Relationship_Number=%s"
			sql_where = (row['Hos_Relationship_Number'],)
			cursor.execute(sql, sql_where)
			roww = cursor.fetchone()
			username = row['Staff_Name']
			hos_name = roww['Hos_Name']
			n = username[0].upper() 
			return render_template('doctor.html', n=n, userrelationshipnumber=userrelationshipnumber, username=username, hos_name=hos_name)
		else:
			return redirect('/')
	else:
		return redirect('/')
@app.route('/patientdetails')
def patientdetails():
    return render_template('patient_info.html')

@app.route('/ipdform')
def ipdform():
    return render_template('ipdform.html')


@app.route('/loginsubmit', methods=['POST'])
def login_submit():
	cursor = None
	
	_relationshipnumber = request.form['urn_no'].upper()
	_password = request.form['pwd']
	if _relationshipnumber and _password:
		#check user exists			
		cursor = mysql.connection.cursor()
		sql = "SELECT * FROM aarogyam_user_auth_nptrun WHERE User_Relationship_Number=%s"
		sql_where = (_relationshipnumber,)
		cursor.execute(sql, sql_where)
		row = cursor.fetchone()
		if row:
			fetched_password = row['User_Password']
			if hashlib.md5(_password.encode()).hexdigest()==fetched_password:
				session['Relationship_Number'] = row['User_Relationship_Number']
				category = str(row['User_Category'])
				if category == '1':
					return jsonify({'success' : '1'})
				elif (category == '2'):
					return jsonify({'success' : '2'})
				elif (category == '8'):
					return jsonify({'success' : '3'})
				else:
					return jsonify({'error' : 'Mail Sent'})
			else:
				return jsonify({'error' : 'Mail Sent'})
		else:
			return jsonify({'error' : 'Mail Sent'})
	else:
		return jsonify({'error' : 'Mail Sent'})

					

@app.route('/hospital_registration', methods=['GET', 'POST'])
def reg():
	if request.method == "POST":
		userDetails = request.form
		Hos_Name = userDetails['hos_name']
		Hos_Licence_No = userDetails['hos_licence']
		Hos_Admin_Mobile_No = userDetails['hos_mobile']
		Hos_Admin_Email_Id = userDetails['hos_email']
		Hos_Admin_Name = userDetails['hos_admin']
		Hos_Address = userDetails['hos_address']
		Hos_Address_State = userDetails['hos_state']
		Hos_Address_City = userDetails['hos_city']
		Hos_Address_Pincode = userDetails['hos_pincode']
		Hos_Password = 'NPT' + str(random.randrange(5, 10**3))
		Reg_Time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		Category = '1'
		Hos_Relationship_Number = 'NPT' + str(random.randrange(1, 10**4)) + Hos_Name[:3].upper() 
		Hashed_Password =hashlib.md5(Hos_Password.encode()).hexdigest() 
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO aarogyam_hos_reg_nptrun(Hos_Name,Hos_Licence_No,Hos_Admin_Mobile_No,Hos_Admin_Email_Id,Hos_Admin_Name,Hos_Address,Hos_Address_State,Hos_Address_City,Hos_Address_Pincode,Hos_Relationship_Number) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (Hos_Name,Hos_Licence_No,Hos_Admin_Mobile_No,Hos_Admin_Email_Id,Hos_Admin_Name,Hos_Address,Hos_Address_State,Hos_Address_City,Hos_Address_Pincode,Hos_Relationship_Number,))
		cur.execute("INSERT INTO aarogyam_user_auth_nptrun(User_Relationship_Number,User_Password,User_Category,User_Date_Reg) VALUES (%s,%s,%s,%s)", (Hos_Relationship_Number,Hashed_Password,Category,Reg_Time,))
		msg = Message('Hello' + ' ' + Hos_Name + ' ' + Hashed_Password, sender = 'pulkit.b@outlook.com', recipients = [Hos_Admin_Email_Id])
		msg.html = render_template('sent_password.html', Hos_Password=Hos_Password, Hos_Relationship_Number=Hos_Relationship_Number)
		mail.send(msg)
		mysql.connection.commit()
		return jsonify({'success' : 'Mail Sent'})
	else:
		return jsonify({'error' : 'Mail Error'})


@app.route('/ipd_reg', methods=['GET', 'POST'])
def ipd_reg():
	rrn = session['Relationship_Number']
	if request.method == "POST":
		userDetails = request.form
		prn = userDetails['prnn']
		bedvalue = userDetails['bedvalue']
		cad = userDetails['completeaddress'] + ',' + userDetails['state'] + ',' + userDetails['city']+ ',' + str(userDetails['pincode'])+ ',' + userDetails['nationality']
		marital_status = userDetails['maritalstatus']
		occupation  = userDetails['occupation']
		photoid = userDetails['photoid']
		otherid = userDetails['otherid']
		idn = userDetails['idn']
		rname = userDetails['rname']
		rgen = userDetails['rgen']
		rmob = userDetails['rmob']
		rrel = userDetails['rrel']
		radd = userDetails['radd']
		blood_group = ''
		date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		ipd_no = str(random.randrange(1, 10**7))  
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO aarogyam_ipd_registration_nptrun(ipd_no,Patient_Relationship_Number,Receptionist_Relationship_Number,address,marital_status,blood_group,occupation,photo_id,other_id,id_number,Guardian_name,guardian_gender,Guardian_contact_no,Guardian_Address,Guardian_Relation_Patient,datetime) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (ipd_no,prn,rrn,cad,marital_status,blood_group,occupation,photoid,otherid,idn,rname,rgen,rmob,radd,rrel,date,))
		cur.execute("INSERT INTO aarogyam_ipd_stay_nptrun(ipd_stay_id,Patient_Relationship_Number,hos_room_id) VALUES (%s,%s,%s)", (ipd_no,prn,bedvalue,))
		mysql.connection.commit()
		return jsonify({'success' : 'Mail Sent'})
	else:
		return jsonify({'error' : 'Mail Error'})


@app.route('/room_registration', methods=['GET', 'POST'])
def roomreg():
	hrn = session['Relationship_Number']
	if request.method == "POST":
		userDetails = request.form
		Room_Number = userDetails.getlist('roomnumber')
		Room_Type = userDetails.getlist('roomtype')
		Room_Floor = userDetails.getlist('roomfloor')
		Room_Block = userDetails.getlist('roomblock')
		Bed_Number = userDetails.getlist('bednumber')
		time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
		cur = mysql.connection.cursor()
		for i in range(0,len(Room_Number)):
			cur.execute("INSERT INTO aarogyam_hos_room_nptrun(hos_relationship_number,roomnumber,roomtype,roomfloor,roomblock,bednumber,dateandtime) VALUES (%s,%s,%s,%s,%s,%s,%s)", (hrn,Room_Number[i],Room_Type[i],Room_Floor[i],Room_Block[i],Bed_Number[i],time,))
		mysql.connection.commit()
		return jsonify({'success' : 'Mail Sent'})
	else:
		return jsonify({'error' : 'Mail Error'})


@app.route('/opd_reg', methods=['GET', 'POST'])
def opdreg():
	rrn = session['Relationship_Number']
	if request.method == "POST":
		Patient_rn = '0'
		userDetails = request.form
		Patient_rn = userDetails['patient_rn']
		Patient_Name = userDetails['patient_name']
		Patient_Mobile_No = userDetails['patient_mobile']
		Patient_Address = userDetails['patient_address']
		Patient_Age = userDetails['patient_age']
		Patient_Gender = userDetails['patient_gender']
		Patient_Reason = userDetails['patient_reason']
		Doctor_Name = userDetails['doctor_name']
		Patient_Relationship_Number = 'NPT' + str(random.randrange(1, 10**4)) + Patient_Name[:3].upper()
		Reg_Date = datetime.datetime.now().strftime("%Y-%m-%d")
		Reg_Time = datetime.datetime.now().strftime("%H:%M:%S")
		Prescription_id = str(random.randrange(1, 10**7))
		cursor = mysql.connection.cursor()
		sql = "SELECT patient_relationship_number FROM aarogyam_patient_registration_nptrun WHERE patient_relationship_number=%s"
		sql_where = (Patient_rn,)
		cursor.execute(sql, sql_where)
		row = cursor.fetchall()
		if row:
			cursor.execute("INSERT INTO aarogyam_opd_registration_nptrun(prescription_no,patient_relationship_number,receptionist_relationship_number,patient_reason,patient_assigned_doctor,date,time) VALUES (%s,%s,%s,%s,%s,%s,%s)", (Prescription_id,Patient_rn,rrn,Patient_Reason,Doctor_Name,Reg_Date,Reg_Time,))
			cursor.execute("INSERT INTO aarogyam_patient_prescription_nptrun(prescription_no,Patient_Relationship_Number) VALUES (%s,%s)", (Prescription_id,Patient_rn,))
		else:
			cursor.execute("INSERT INTO aarogyam_opd_registration_nptrun(prescription_no,patient_relationship_number,receptionist_relationship_number,patient_age,patient_reason,patient_assigned_doctor,date,time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (Prescription_id,Patient_Relationship_Number,rrn,Patient_Age,Patient_Reason,Doctor_Name,Reg_Date,Reg_Time,))
			cursor.execute("INSERT INTO aarogyam_patient_prescription_nptrun(prescription_no,Patient_Relationship_Number) VALUES (%s,%s)", (Prescription_id,Patient_Relationship_Number,))
			cursor.execute("INSERT INTO aarogyam_patient_registration_nptrun(receptionist_relationship_number,patient_relationship_number,patient_name,patient_mobile,patient_address,patient_gender,date,time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (rrn,Patient_Relationship_Number,Patient_Name,Patient_Mobile_No,Patient_Address,Patient_Gender,Reg_Date,Reg_Time,))
		mysql.connection.commit()
		return jsonify({'success' : 'Mail Sent'})
	else:
		return jsonify({'error' : 'Mail Error'})




@app.route('/patient_exist_check', methods=['POST'])
def patient_exist_check():
	try:
		prn = str(request.args['prn'])
		# validate the received values
		if request.method == 'POST':
			cursor = mysql.connection.cursor()
			
			sql = "SELECT patient_relationship_number,patient_name,patient_mobile,patient_address,patient_gender FROM aarogyam_patient_registration_nptrun WHERE patient_relationship_number=%s"
			sql_where = (prn,)
			cursor.execute(sql, sql_where)
			row = cursor.fetchall()
			
			if row:
				resp = jsonify(row) 
				resp.status_code = 200
				return resp
			else:
				resp = jsonify({'error' : 'Mail Error'})
				resp.status_code = 200
				return resp
		else:
			resp = jsonify({'error' : 'Mail Error'})
			resp.status_code = 200
			return resp
	except Exception as e:
		print(e)

@app.route('/ipdrefer', methods=['POST'])
def ipdrefer():
	ppid = str(request.args['ppid'])
	reason = str(request.form['data'])
	
	if request.method == 'POST':
		cursor = mysql.connection.cursor()
		sql = "UPDATE aarogyam_patient_prescription_nptrun SET ipd_refer = %s, reason = %s WHERE prescription_no = %s"
		data = ('1',reason,ppid,)
		cursor.execute(sql, data)
		mysql.connection.commit()
		return jsonify({'success' : 'Success'})
	else:
		return jsonify({'error' : 'Error'})

@app.route('/patientalert', methods=['POST'])
def patientalert():
	try:
		
		# validate the received values
		if request.method == 'POST':
			cursor = mysql.connection.cursor()
			Date = str(datetime.datetime.now().strftime("%Y-%m-%d"))
			sql = "SELECT pr.patient_relationship_number, pr.patient_name, pr.date,pr.time, opr.patient_reason,opr.prescription_no FROM aarogyam_patient_registration_nptrun pr INNER JOIN aarogyam_opd_registration_nptrun opr on pr.patient_relationship_number = opr.patient_relationship_number WHERE opr.date=%s"
			sql_where = (Date,)
			cursor.execute(sql, sql_where)
			row = cursor.fetchall()
			if row:
				resp = jsonify(row) 
				resp.status_code = 200
				return resp
			else:
				resp = jsonify('<span style=\'color:green;\'>Error</span>')
				resp.status_code = 200
				return resp
		else:
			resp = jsonify('<span style=\'color:red;\'>Username is required field.</span>')
			resp.status_code = 200
			return resp
	except Exception as e:
		print(e)

@app.route('/ipdalert', methods=['POST'])
def ipdalert():
	try:
		rrn = session['Relationship_Number']
		if request.method == 'POST':
			cursor = mysql.connection.cursor()
			sql = "SELECT * FROM aarogyam_staff_details_nptrun hos inner join aarogyam_opd_registration_nptrun opd on opd.receptionist_relationship_number = hos.Staff_Relationship_Number inner join aarogyam_patient_prescription_nptrun pre on opd.prescription_no = pre.prescription_no WHERE pre.ipd_refer = %s and hos.Staff_Relationship_Number = %s" 
			sql_where = ('1',rrn)
			cursor.execute(sql, sql_where)
			row = cursor.fetchall()
			if row:
				resp = jsonify(row) 
				resp.status_code = 200
				return resp
			else:
				resp = jsonify('<span style=\'color:green;\'>Error</span>')
				resp.status_code = 200
				return resp
		else:
			resp = jsonify('<span style=\'color:red;\'>Username is required field.</span>')
			resp.status_code = 200
			return resp
	except Exception as e:
		print(e)


@app.route('/patientinfo', methods=['POST'])
def patientinfo():
	try:
		prn = str(request.args['prn'])
		if prn and request.method == 'POST':
			cursor = mysql.connection.cursor()
			sql = "SELECT pr.patient_relationship_number, pr.patient_name, pr.patient_gender,opr.patient_age,pr.patient_address, opr.patient_reason,opr.prescription_no FROM aarogyam_patient_registration_nptrun pr INNER JOIN aarogyam_opd_registration_nptrun opr on pr.patient_relationship_number = opr.patient_relationship_number WHERE pr.patient_relationship_number=%s"
			sql_where = (prn,)
			cursor.execute(sql, sql_where)
			row = cursor.fetchall()
			
			if row:
				resp = jsonify(row) 
				resp.status_code = 200
				return resp
			else:
				resp = jsonify('<span style=\'color:green;\'>Error</span>')
				resp.status_code = 200
				return resp
		else:
			resp = jsonify('<span style=\'color:red;\'>Username is required field.</span>')
			resp.status_code = 200
			return resp
	except Exception as e:
		print(e)

@app.route('/ipdpatientinfo', methods=['POST'])
def ipdpatientinfo():
	try:
		prn = str(request.args['prn'])
		ppid = request.args['ppid']
		if prn and request.method == 'POST':
			cursor = mysql.connection.cursor()
			sql = "SELECT pr.patient_relationship_number, pr.patient_name, pr.patient_gender,opr.patient_age,pr.patient_address,opr.patient_assigned_doctor,pre.prescription_no,pre.reason FROM aarogyam_patient_registration_nptrun pr INNER JOIN aarogyam_opd_registration_nptrun opr on pr.patient_relationship_number = opr.patient_relationship_number INNER JOIN aarogyam_patient_prescription_nptrun pre on opr.prescription_no = pre.prescription_no WHERE pr.patient_relationship_number=%s and pre.prescription_no = %s"
			sql_where = (prn,ppid)
			cursor.execute(sql, sql_where)
			row = cursor.fetchall()
			
			if row:
				resp = jsonify(row) 
				resp.status_code = 200
				return resp
			else:
				resp = jsonify('<span style=\'color:green;\'>Error</span>')
				resp.status_code = 200
				return resp
		else:
			resp = jsonify('<span style=\'color:red;\'>Username is required field.</span>')
			resp.status_code = 200
			return resp
	except Exception as e:
		print(e)

@app.route('/fetchbed', methods=['POST'])
def fetchbed():
	try:
		hrn = str(request.args['hrn'])
		if hrn and request.method == 'POST':
			cursor = mysql.connection.cursor()
			sql = "SELECT * FROM aarogyam_hos_room_nptrun WHERE hos_relationship_number=%s"
			sql_where = (hrn,)
			cursor.execute(sql, sql_where)
			row = cursor.fetchall()
			rowarr = []
			for i in range (0,len(row)):
				rowarr.append(row[i])
			if row:
				resp = jsonify(rowarr) 
				resp.status_code = 200
				return resp
			else:
				resp = jsonify('<span style=\'color:green;\'>Error</span>')
				resp.status_code = 200
				return resp
		else:
			resp = jsonify('<span style=\'color:red;\'>Username is required field.</span>')
			resp.status_code = 200
			return resp
	except Exception as e:
		print(e)

@app.route('/fetchdoc', methods=['POST'])
def fetchdoc():
	rrn = session['Relationship_Number']
	try:
		if request.method == 'POST':
			cursor = mysql.connection.cursor()
			sql = "SELECT Hos_Relationship_Number FROM aarogyam_staff_details_nptrun WHERE Staff_Relationship_Number=%s"
			sql_where = (rrn,)
			cursor.execute(sql, sql_where)
			row = cursor.fetchone()
			hrn = row['Hos_Relationship_Number']
			sql = "SELECT Staff_Name FROM aarogyam_staff_details_nptrun WHERE Hos_Relationship_Number=%s and Staff_Designation=%s"
			sql_where = (hrn,'2',)
			cursor.execute(sql, sql_where)
			row = cursor.fetchall()
			print(row)
			if row:
				resp = jsonify(row) 
				resp.status_code = 200
				return resp
			else:
				resp = jsonify('<span style=\'color:green;\'>Error</span>')
				resp.status_code = 200
				return resp
		else:
			resp = jsonify('<span style=\'color:red;\'>Username is required field.</span>')
			resp.status_code = 200
			return resp
	except Exception as e:
		print(e)


@app.route('/prescription-submit', methods=['GET', 'POST'])
def prescriptionsubmit():
	if request.method == "POST":
		userDetails = request.form
		ppid = str(request.args['ppid'])
		Patient_Weight = userDetails['patient_weight']
		Patient_Problem = userDetails['patient_problem']
		Medicine_Name = userDetails.getlist('medicinename')
		Medicine_Strength = userDetails.getlist('medicinestrength')
		Medicine_Dosage = userDetails.getlist('medicinedosage')
		Medicine_Others = userDetails.getlist('medicineothers')
		Test_Name = userDetails.getlist('testname')
		Test_Detail = userDetails.getlist('testothers')
		Reg_Time = datetime.datetime.now().strftime("%Y-%m-%d")
		mncsv =''
		mscsv = ''
		mdcsv = ''
		mocsv = ''
		tncsv = ''
		tdcsv = ''
		for i in range(0,len(Medicine_Name)):
			if(i==0):
				mncsv = mncsv + Medicine_Name[i]
				mscsv = mscsv + Medicine_Strength[i]
				mdcsv = mdcsv + Medicine_Dosage[i]
				mocsv = mocsv + Medicine_Others[i]
			else:
				mncsv = mncsv + ',' + Medicine_Name[i]
				mscsv = mscsv + ',' + Medicine_Strength[i]
				mdcsv = mdcsv + ',' + Medicine_Dosage[i]
				mocsv = mocsv + ',' + Medicine_Others[i]
		for i in range(0,len(Test_Name)):
			if(i==0):
				tncsv = tncsv + Test_Name[i]
				tdcsv = tdcsv + Test_Detail[i]
			else:
				tncsv = tncsv + ',' + Test_Name[i]
				tdcsv = tdcsv + ',' + Test_Detail[i]
		cursor = mysql.connection.cursor()
		sql = "UPDATE aarogyam_patient_prescription_nptrun SET patient_weight = %s, patient_problem = %s, medicine_name = %s,medicine_strength = %s,dosage = %s,other_detail = %s, test_name = %s, other_test_detail = %s, date = %s WHERE prescription_no = %s"
		data = (Patient_Weight,Patient_Problem,mncsv,mscsv,mdcsv,mocsv,tncsv,tdcsv,Reg_Time,ppid,)
		cursor.execute(sql, data)
		mysql.connection.commit()
		return jsonify({'success' : 'Success'})
	else:
		return jsonify({'error' : 'Error'})


@app.route('/logout')
def logout():
	if 'Relationship_Number' in session:
		session.pop('Relationship_Number', None)
	return redirect('/')
	
if __name__ == '__main__':
    app.run(debug=True) 