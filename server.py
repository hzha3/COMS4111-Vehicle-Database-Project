
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, flash, redirect, url_for,session
#from werkzeug.security import generate_password_hash, check_password_hash
#from flask_login import login_user, login_required, logout_user, current_user
from datetime import date
import random


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.config['SECRET_KEY'] = 'Group106'



#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.73.36.248/project1
#
# For example, if you had username zy2431 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://zy2431:123123@34.73.36.248/project1"
#
# Modify these with your own credentials you received from TA!
DATABASE_USERNAME = "hz2816"
DATABASE_PASSWRD = "8168"
DATABASE_HOST = "34.148.107.47" # change to 34.28.53.86 if you used database 2 for part 2
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/project1"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
'''
with engine.connect() as conn:
	create_table_command = """
	CREATE TABLE IF NOT EXISTS test (
		id serial,
		name text
	)
	"""
	res = conn.execute(text(create_table_command))
	insert_table_command = """INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace')"""
	res = conn.execute(text(insert_table_command))
	# you need to commit for create, insert, update queries to reflect
	conn.commit()
'''



@app.before_request
def before_request():
	"""
	This function is run at the beginning of every web request 
	(every time you enter an address in the web browser).
	We use it to setup a database connection that can be used throughout the request.

	The variable g is globally accessible.
	"""
	try:
		g.conn = engine.connect()
	except:
		print("uh oh, problem connecting to database")
		import traceback; traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):
	"""
	At the end of the web request, this makes sure to close the database connection.
	If you don't, the database could run out of memory!
	"""
	try:
		g.conn.close()
	except Exception as e:
		pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
	"""
	request is a special object that Flask provides to access web request information:

	request.method:   "GET" or "POST"
	request.form:     if the browser submitted a form, this contains the data in the form
	request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

	See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
	"""

	# DEBUG: this is debugging code to see what request looks like
	print(request.args)


	return render_template("index.html")


@app.route('/data', methods =['GET','POST'])
def data():
	"""
	request is a special object that Flask provides to access web request information:

	request.method:   "GET" or "POST"
	request.form:     if the browser submitted a form, this contains the data in the form
	request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

	See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
	"""

	#table name
	select_query='''
SELECT C.TABLE_NAME
FROM INFORMATION_SCHEMA.COLUMNS C
WHERE EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES T 
              WHERE T.TABLE_TYPE='BASE TABLE' AND C.TABLE_NAME=T.TABLE_NAME)
GROUP BY c.TABLE_NAME

	'''
	cursor = g.conn.execute(text(select_query))
	table_name=[]
	for result in cursor:
		if "pg" in result[0] or "sql" in result[0] or "test" in result[0]:
			continue
		table_name.append(result[0])
	cursor.close()

	select = "vehicle"

	if request.method == 'POST':
		select = request.form.get('table')
	#select = request.form.get('table')
	#select = str(select)


	select_query=f'''
	select *
	from INFORMATION_SCHEMA.COLUMNS
	where TABLE_NAME='{select}'
	'''
	cursor = g.conn.execute(text(select_query))
	col_name=[]
	for result in cursor:
		col_name.append(result[3])
	cursor.close()


	output=[]
	select_query = f"SELECT * from {select}"

	cursor = g.conn.execute(text(select_query))

	for result in cursor:
		output.append(result)
	cursor.close()

	context = {'table_name': table_name,'data': output, 'col_name': col_name,'select': select}



	return render_template("data.html",**context)




@app.route('/sql', methods =['GET','POST'])
def sql():
	#table name
	sql_note=None
	output=[]

	if request.method == 'POST':
		sql_note = request.form.get('note')
		cursor = g.conn.execute(text(sql_note))
		for result in cursor:
			output.append(result)
		cursor.close()

	context = {'data': output,"sql":sql_note}

	return render_template("sql.html",**context)











#------------------------------------------------------------
  
@app.route('/vehicle', methods =['GET','POST'])
def vehicle():
	#table name
	select_query1='''
SELECT distinct(manufacturer)
FROM vehicle
Order by manufacturer

	'''
	cursor = g.conn.execute(text(select_query1))
	table_name=[]
	for result in cursor:
		table_name.append(result[0])
	cursor.close()

	select = "ALL"
	price_range_low=0
	price_range_high=10000

	if request.method == 'POST':
		select = request.form.get('table')
		if price_range_low:
			price_range_low=request.form.get('price_range_low')
			if price_range_low=="":
				price_range_low=0
		if price_range_high:
			price_range_high=request.form.get('price_range_high')
			if price_range_high=="":
				price_range_high=10000



	select_query=f'''
	select *
	from INFORMATION_SCHEMA.COLUMNS
	where TABLE_NAME='vehicle'
	'''
	cursor = g.conn.execute(text(select_query))
	col_name=[]
	for result in cursor:
		col_name.append(result[3])
	cursor.close()


	output=[]
	select_query = f"SELECT * from vehicle Where manufacturer='{select}' AND price_in_thousands > {price_range_low} AND price_in_thousands < {price_range_high}"
	if select == "ALL":
		select_query = f"SELECT * from vehicle Where price_in_thousands > {price_range_low} AND price_in_thousands < {price_range_high}"



	cursor = g.conn.execute(text(select_query))

	for result in cursor:
		output.append(result)
	cursor.close()

	context = {'table_name': table_name,'data': output, 'col_name': col_name,'select': select, "price_range_low":price_range_low,"price_range_high":price_range_high}






	return render_template("vehicle.html",**context)



@app.route('/dealership', methods =['GET','POST'])
def dealership():
	#table name
	select_query1='''
SELECT (SUBSTRING(d_id,1,2)) as a
FROM dealership
Group by a
order by a

	'''
	cursor = g.conn.execute(text(select_query1))
	table_name=[]
	for result in cursor:
		table_name.append(result[0])
	cursor.close()

	select = "ALL"
	price_range_low=0
	price_range_high=10000

	if request.method == 'POST':
		select = request.form.get('table')
		if price_range_low:
			price_range_low=request.form.get('d_sale_low')
			if price_range_low=="":
				price_range_low=0
		if price_range_high:
			price_range_high=request.form.get('d_sale_high')
			if price_range_high=="":
				price_range_high=10000



	select_query=f'''
	select *
	from INFORMATION_SCHEMA.COLUMNS
	where TABLE_NAME='dealership'
	'''
	cursor = g.conn.execute(text(select_query))
	col_name=[]
	for result in cursor:
		col_name.append(result[3])
	cursor.close()


	output=[]
	select_query = f"SELECT * from dealership Where d_id like'{select}%' AND d_sale > {price_range_low} AND d_sale < {price_range_high} order by d_id"
	if select == "ALL":
		select_query = f"SELECT * from dealership Where d_sale > {price_range_low} AND d_sale < {price_range_high} order by d_id"



	cursor = g.conn.execute(text(select_query))

	for result in cursor:
		output.append(result)
	cursor.close()

	context = {'table_name': table_name,'data': output, 'col_name': col_name,'select': select, "price_range_low":price_range_low,"price_range_high":price_range_high}



	return render_template("dealership.html",**context)




@app.route('/insurance', methods =['GET','POST'])
def insurance():
	#table name
	select_query1='''
SELECT distinct(state)
FROM insurance
Order by state

	'''
	cursor = g.conn.execute(text(select_query1))
	table_name=[]
	for result in cursor:
		table_name.append(result[0])
	cursor.close()

	select = "ALL"
	price_range_low=0
	price_range_high=0

	if request.method == 'POST':
		select = request.form.get('table')
		price_range_low=request.form.get('minimum_coverage')
		price_range_high=request.form.get('full_coverage')




	select_query=f'''
	select *
	from INFORMATION_SCHEMA.COLUMNS
	where TABLE_NAME='insurance'
	'''
	cursor = g.conn.execute(text(select_query))
	col_name=[]
	for result in cursor:
		col_name.append(result[3])
	cursor.close()


	output=[]
	select_query = f"SELECT * from insurance Where state='{select}' AND minimum_coverage > {price_range_low} AND full_coverage > {price_range_high}"
	if select == "ALL":
		select_query = f"SELECT * from insurance Where minimum_coverage > {price_range_low} AND full_coverage > {price_range_high}"



	cursor = g.conn.execute(text(select_query))

	for result in cursor:
		output.append(result)
	cursor.close()

	context = {'table_name': table_name,'data': output, 'col_name': col_name,'select': select, "price_range_low":price_range_low,"price_range_high":price_range_high}






	return render_template("insurance.html",**context)



@app.route('/rec', methods =['GET','POST'])
def rec():
	#table name
	select_query1='''
SELECT distinct(v_id)
FROM vehicle
Order by v_id

	'''
	cursor = g.conn.execute(text(select_query1))
	table_name=[]
	for result in cursor:
		table_name.append(result[0])
	cursor.close()

	select = "V_1"


	if request.method == 'POST':

		select = str(request.form.get('table'))


	select_query=f'''
	select *
	from INFORMATION_SCHEMA.COLUMNS
	where TABLE_NAME='vehicle'
	'''
	cursor = g.conn.execute(text(select_query))
	col_name=[]
	for result in cursor:
		col_name.append(result[3])
	cursor.close()


	output=[]
	select_query = f"SELECT * from vehicle Where v_id='{select}' "
	if select == "ALL":
		select_query = f"SELECT * from vehicle Where v_id='{select}' "

	cursor = g.conn.execute(text(select_query))

	for result in cursor:
		output.append(result)
	cursor.close()


	context = {'data':output}

		

	output1=[]
	select_query = f"SELECT * from vehicle Where v_id !='{select}' AND manufacturer = '{output[0][1]}' "
	if select == "ALL":
		select_query = f"SELECT * from vehicle Where v_id= !='{select}' AND manufacturer = '{output[0][1]}' "

	cursor = g.conn.execute(text(select_query))

	for result in cursor:
		output1.append(result)
	cursor.close()



	output2=[]
	price_range_low = output[0][3]-1
	price_range_high = output[0][3]+1
	select_query = f"SELECT * from vehicle Where v_id!='{select}' AND price_in_thousands > {price_range_low} AND price_in_thousands < {price_range_high} order by price_in_thousands"
	if select == "ALL":
		select_query = f"SELECT * from vehicle Where v_id='{select}' "

	cursor = g.conn.execute(text(select_query))

	for result in cursor:
		output2.append(result)
	cursor.close()

	context = {'table_name': table_name,'data': output,'data1': output1,'data2': output2, 'col_name': col_name,'select': select, "price_range_low":price_range_low,"price_range_high":price_range_high}






	return render_template("rec.html",**context)




@app.route('/signup',methods = ['GET','POST'])
def signup():
	"""
	request is a special object that Flask provides to access web request information:

	request.method:   "GET" or "POST"
	request.form:     if the browser submitted a form, this contains the data in the form
	request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

	See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
	"""

	select_query = f"""
SELECT MAX(CAST(substring(c_id FROM 3) AS INTEGER)) FROM customer;
"""
	cursor = g.conn.execute(text(select_query))
	num = []

	for result in cursor:
		num.append(result)
	cursor.close()

	#num = int(num[0].split("_")[-1])+1
	num = int(num[0][0])+1

	cid = "C_"+str(num)
	name = None
	address = None
	phone = None
	gender = None
	annualincome = None
	texts = ""
	context = {"cid":cid,"texts":texts}

	if request.method == 'POST':
		name = request.form.get('name')
		address = request.form.get('address')
		phone = request.form.get('phone')
		gender = request.form.get('gender')
		annualincome = request.form.get('annualincome')
		texts = "The following account is created:"

		select_query = f"""
INSERT INTO customer (c_id , customer_name,customer_address , phone , gender , annual_income)
VALUES ('{cid}', '{name}', '{address}',{phone},'{gender}',{annualincome});
		"""

		cursor = g.conn.execute(text(select_query))
		cursor.close()
		g.conn.commit()

		select_query = f"""
SELECT MAX(CAST(substring(c_id FROM 3) AS INTEGER)) FROM customer;
"""
		cursor = g.conn.execute(text(select_query))
		num = []

		for result in cursor:
			num.append(result)
		cursor.close()
		g.conn.commit()


		#num = int(num[0].split("_")[-1])+1
		num = int(num[0][0])+1

		cid = "C_"+str(num)
		context = {"cid":cid,"name":name,"address":address,"phone":phone, "gender":gender,"annualincome":annualincome,"texts":texts}
	

	return render_template("signup.html", **context)



@app.route('/order', methods =['GET','POST'])
def order():
	
	cid = None
	phone = None
	transaction ="Order "
	vehicle = "Vehicle Info"
	customer = "Customer Info"
	saleman = "Saleman Info"
	dealer = "Dealer Info"
	insurance="Insurance Info"
	manufacturer="Manufacturer Info"
	context = {'cid':cid, 'phone':phone}

	if request.method == 'POST':
		cid = request.form.get('cid')
		phone = request.form.get('phone')
		transaction ="Order "
		vehicle = "Vehicle Info"
		customer = "Customer Info"
		saleman = "Saleman Info"
		dealer = "Dealer Info"
		insurance="Insurance Info"
		manufacturer="Manufacturer Info"

		select_query = f"SELECT * from car_sale_transaction Where c_id = '{cid}'"
		cursor = g.conn.execute(text(select_query))
		output=[]
		for result in cursor:
			output.append(result)
		cursor.close()


		select_query = f"SELECT * from vehicle Where v_id = '{output[0][2]}'"
		cursor = g.conn.execute(text(select_query))
		output1=[]
		for result in cursor:
			output1.append(result)
		cursor.close()
		

		select_query = f"SELECT * from customer Where c_id = '{output[0][3]}'"
		cursor = g.conn.execute(text(select_query))
		output2=[]
		for result in cursor:
			output2.append(result)
		cursor.close()
		

		

		select_query = f"SELECT * from dealership Where d_id = '{output[0][5]}'"
		cursor = g.conn.execute(text(select_query))
		output4=[]
		for result in cursor:
			output4.append(result)
		cursor.close()
		

		select_query = f"SELECT * from insurance Where insurance_id  = '{output[0][6]}'"
		cursor = g.conn.execute(text(select_query))
		output5=[]
		for result in cursor:
			output5.append(result)
		cursor.close()
		

		select_query = f"SELECT * from manufacturer Where manufacturer_name = '{output[0][7]}'"
		cursor = g.conn.execute(text(select_query))
		output6=[]
		for result in cursor:
			output6.append(result)
		cursor.close()
		context = {'cid':cid, 'phone':phone,'output':output,"transaction" :transaction, "vehicle" : vehicle ,"customer" : customer,"saleman" : saleman ,"dealer":dealer,"insurance": insurance,"manufacturer":manufacturer, 'output1':output1, 'output2':output2, 'output4':output4, 'output5':output5, 'output6':output6}
		
	

	#context = {'cid':cid, 'phone':phone,'output':output,transaction :"transaction ", vehicle : "vehicle ",customer : "customer",saleman : "saleman ",dealer:"dealer ",insurance: "insurance:",manufacturer:"manufacturer"}
	


	return render_template("order.html",**context)




@app.route('/cart', methods =['GET','POST'])
def cart():
	
	select_query = f"""
SELECT MAX(CAST(substring(t_id FROM 3) AS INTEGER)) FROM car_sale_transaction;
"""
	cursor = g.conn.execute(text(select_query))
	num = []

	for result in cursor:
		num.append(result)
	cursor.close()

	#num = int(num[0].split("_")[-1])+1
	num = int(num[0][0])+1

	tid = "T_"+str(num)

	today_date = date.today().strftime('%m/%d/%Y')
	transaction ="Order "
	vehicle = "Vehicle Info"
	customer = "Customer Info"
	saleman = "Saleman Info"
	dealer = "Dealer Info"
	insurance="Insurance Info"
	manufacturer="Manufacturer Info"
	context = {'tid':tid, 'date':today_date}

	if request.method == 'POST':
		vid = request.form.get('vid')
		cid = request.form.get('cid')
		did = request.form.get('did')
		iid = request.form.get('iid')

		sid = "S_"+str(random.randint(0,999))
		
		select_query = f"SELECT manufacturer from vehicle Where v_id = '{vid}'"
		cursor = g.conn.execute(text(select_query))
		m=[]
		for result in cursor:
			m.append(result)
		cursor.close()
		m_name=m[0][0]
		

		select_query = f"""
INSERT INTO car_sale_transaction (t_id , transaction_date ,v_id , c_id , s_id , d_id,i_id,manufacturer_name)
VALUES ('{tid}', '{today_date}', '{vid}','{cid}','{sid}','{did}','{iid}','{m_name}');
		"""

		cursor = g.conn.execute(text(select_query))
		cursor.close()
		g.conn.commit()

	
		select_query = f"SELECT * from car_sale_transaction Where t_id = '{tid}'"
		cursor = g.conn.execute(text(select_query))
		output=[]
		for result in cursor:
			output.append(result)
		cursor.close()


		select_query = f"SELECT * from vehicle Where v_id = '{output[0][2]}'"
		cursor = g.conn.execute(text(select_query))
		output1=[]
		for result in cursor:
			output1.append(result)
		cursor.close()
		

		select_query = f"SELECT * from customer Where c_id = '{output[0][3]}'"
		cursor = g.conn.execute(text(select_query))
		output2=[]
		for result in cursor:
			output2.append(result)
		cursor.close()
		

		

		select_query = f"SELECT * from dealership Where d_id = '{output[0][5]}'"
		cursor = g.conn.execute(text(select_query))
		output4=[]
		for result in cursor:
			output4.append(result)
		cursor.close()
		

		select_query = f"SELECT * from insurance Where insurance_id  = '{output[0][6]}'"
		cursor = g.conn.execute(text(select_query))
		output5=[]
		for result in cursor:
			output5.append(result)
		cursor.close()
		

		select_query = f"SELECT * from manufacturer Where manufacturer_name = '{output[0][7]}'"
		cursor = g.conn.execute(text(select_query))
		output6=[]
		for result in cursor:
			output6.append(result)
		cursor.close()
		context = {'tid':tid, 'date':today_date,'output':output,"transaction" :transaction, "vehicle" : vehicle ,"customer" : customer,"saleman" : saleman ,"dealer":dealer,"insurance": insurance,"manufacturer":manufacturer, 'output1':output1, 'output2':output2, 'output4':output4, 'output5':output5, 'output6':output6}
		
		

	#context = {'cid':cid, 'phone':phone,'output':output,transaction :"transaction ", vehicle : "vehicle ",customer : "customer",saleman : "saleman ",dealer:"dealer ",insurance: "insurance:",manufacturer:"manufacturer"}
	


	return render_template("cart.html",**context)









if __name__ == "__main__":
	import click

	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8111, type=int)
	
	def run(debug, threaded, host, port):
		"""
		This function handles command line parameters.
		Run the server using:

			python server.py

		Show the help text using:

			python server.py --help

		"""


		HOST, PORT = host, port
		print("running on %s:%d" % (HOST, PORT))
		app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

		

run()
