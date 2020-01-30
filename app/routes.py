import os
import json
from flask import flash, render_template, request, redirect, url_for
from app import app, categorize, db, parser
from app.models import Payment
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"

def allowed_file(filename):
	return '.' in filename and (filename.rsplit('.', 1)[1].lower() == 'pdf')

@app.route('/', methods = ['GET', 'POST'])
def upload():
	if request.method == 'POST':
	# check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		# if user does not select file, browser also
		# submit an empty part without filename
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			filepath = os.path.join(UPLOAD_FOLDER, filename)
			file.save(filepath)
			# if not process_bank_statement(filepath):
			# 	return "Are you sure you uploaded a bank statement? SpendAnalyzer was not able to parse it."
			messages = filepath
			df = parser.parse_bank_statement(filepath)
			categorize.categorize(df)
			for index, row in df.iterrows():
				p = Payment(date=row.Date, desc=row.Desc, amount=row.Amount, balance=row.Balance, category=row.Category)
				db.session.add(p)
			db.session.commit()
			return redirect(url_for('.dashboard'))
			# return redirect(request.url)
	return render_template("start.html")

@app.route('/dashboard')
def dashboard():
	data = db.session.query(db.func.strftime('%Y/%m',Payment.date), db.func.sum(Payment.amount)).filter(Payment.category.isnot('Others')).group_by(db.func.strftime('%Y/%m', Payment.date)).all()
	month_data = {'data': [], 'labels': []}
	for month in data:
		month_data['labels'].append(month[0][2:])
		month_data['data'].append(abs(month[1]))

	data = db.session.query(Payment.category, db.func.sum(Payment.amount)).group_by(Payment.category).all()
	categorical_data = {'data': [], 'labels':[]}
	for category in data:
		if category[0] != 'Others':
			categorical_data['labels'].append(category[0])
			categorical_data['data'].append(-category[1])

	X_Months = 8
	X_Rest = 10
	latest_month_query = db.session.query(db.func.max(Payment.date))
	filter_latest_month_query = (db.func.julianday(Payment.date, "start of month")
		- db.func.julianday(latest_month_query,"start of month"))
	strip_desc = db.func.replace(db.func.replace(Payment.desc," Card 7186",""),"Sq *","")
	format_desc = db.func.ltrim(strip_desc, db.func.substr(Payment.desc,0,7))
	data = (db.session.query(format_desc, db.func.count(format_desc).label("Count"))
		.filter(Payment.category.is_("Restaurants"))
		.filter(filter_latest_month_query >= -31*X_Months)
		.group_by(format_desc).order_by(db.desc("Count")).all())
	unique_rest_visited = len(data)
	# data = db.session.query(Payment.desc).filter(db.func.strftime('%Y/%m',Payment.date))

	payments = Payment.query.order_by(Payment.date).all()
	return render_template("dashboard.html", payments=[payment.serialize() for payment in payments],
		categorical_data=categorical_data, month_data=month_data, restaurants=data[:X_Rest],
		unique_rest_visited=unique_rest_visited)