from flask import Flask, render_template, request, redirect, url_for
import csv, mysql.connector
import os
import random
from twilio.rest import Client
from twilio.http.http_client import TwilioHttpClient
#from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
app = Flask(__name__)

#proxy_client = TwilioHttpClient(proxy={'http': os.environ['http_proxy']}, 'https': os.environ['https_proxy']})


engine = create_engine(
	"mysql+mysqlconnector://xaniku:password123@xaniku.mysql.pythonanywhere-services.com/xaniku$stores",
	pool_pre_ping=True
	)

## DATABASE ##



#mydb = mysql.connector.connect(
#		host="xaniku.mysql.pythonanywhere-services.com",
#		user="xaniku",
#		password="password123",
#		database='xaniku$stores'
#	)

#mycursor = mydb.cursor(buffered=True)


#sql_insert_formula = "INSERT INTO Stores (store_name, store_description, store_status, box, sold_boxes) VALUES (%s, %s, %s, %s, %s)"
#sql_select_formula = "SELECT * FROM Stores"
#sql_delete_formula = "DELETE FROM Stores WHERE store_name='Lanchonete Lebron'"


#store1 = ("Lanchonete Lebron", "grande loja", "activa", 1, 0)
#store2 = ("Mercearia", "péssimo", "activa", 1, 0)

#mycursor.execute(sql_select_formula)
#result = mycursor.fetchone()

# for x in result:
# 	if x == 22:
# 		store_id = result[2]
# 		print(store_id)

#mydb.commit()







 ## DATABASE ##

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/works.html')
def works():
    result = engine.execute("SELECT *, DATE_FORMAT(start_time, '%h:%i') AS start_time, DATE_FORMAT(end_time, '%h:%i') AS end_time FROM theStores")
    data = result.fetchall()
    return render_template("works.html", data = data)



#@app.route('/work.html')
#def fds(result):
#    return render_template("work.html", render_template("work.html", store_name = result[1], store_description = result[2], store_status = result[3], number_of_boxes = result[4]))

@app.route('/<string:page_name>')
def components(page_name):
    return render_template(page_name, title=page_name)

@app.route('/reservation_form', methods=["POST"])
def reservation():
	if request.method == "POST":
	    code = random.randint(99,1000)
	    account_sid = 'AC1a12907b714663c20b1fc6ba2155e8f9'
	    auth_token = 'b610d4b8a6b588097f02608b59d15d5b'
	    user_phone = request.form["user_phone"]

	    store_name = request.form["store_name"]
	    store_phone = request.form["store_phone"]
	    store_email = request.form["store_email"]
	    start_time = request.form["start_time"]
	    end_time = request.form["end_time"]
	    store_id = request.form["store_id"]
	    user_name = request.form["user_name"]
	    user_email = request.form["user_email"]
	    available_boxes = request.form["available_boxes"]
	    client = Client(account_sid, auth_token)#, http_client=proxy_client)
	    message = client.messages.create(
							  from_='+12513188064',
                              body=('Parabéns %s! Alguém salvou a Caixa Surpresa. O código é %s. Peça ao cliente para confirmar o código.' % (store_name, code)),
                              to=store_phone
                          )

	    client = Client(account_sid, auth_token)#, http_client=proxy_client)
	    message = client.messages.create(
							  from_='+12513188064',
                              body=('Parabéns pela compra da Caixa Surpresa. O seu código é o %s ' % code),
                              to=user_phone
                          )
	    print(message.sid)
	    new_count = int(available_boxes) - 1
	    engine.execute("UPDATE theStores SET available_boxes = %s WHERE store_id = %s" % (new_count, store_id))
	    insert_statement = ("INSERT INTO users (user_name, user_email) values (%s, %s)")
	    params = (user_name, user_email)
	    engine.execute(insert_statement, params)
	    return render_template("reservado.html", start_time = start_time, end_time = end_time, store_name = store_name)


@app.route('/<int:store_id>')
def stores(store_id):
        #mycursor.execute("SELECT *, DATE_FORMAT(start_time, '%h:%i') AS start_time, DATE_FORMAT(end_time, '%h:%i') AS end_time FROM theStores WHERE store_id = %s" % store_id)
        #result = mycursor.fetchone()
        result = engine.execute("SELECT *, DATE_FORMAT(start_time, '%%h:%%i') AS start_time, DATE_FORMAT(end_time, '%%h:%%i') AS end_time FROM theStores WHERE store_id = %s" % store_id)
        result = result.fetchone()
        return render_template("work.html", store_name = result[1], store_description = result[2], store_phone = result[3], store_status = result[5], available_boxes = result[6], start_time = result["start_time"], end_time = result["end_time"], store_id = store_id)



@app.route('/ninja.html')
def ninja():
    result = engine.execute("SELECT * FROM theStores")
    #mycursor.execute("SELECT * FROM theStores")
    data = result.fetchall()
    return render_template("ninja.html", data = data)

@app.route('/add_store', methods=["POST"])
def add_store():
	if request.method == "POST":

		store_name = request.form["store_name"]
		store_description = request.form["store_description"]
		store_phone = request.form["store_phone"]
		available_boxes = request.form["available_boxes"]
		store_email = request.form["store_email"]
		start_time = request.form["start_time"]
		end_time = request.form["end_time"]
		insert_statement = ("INSERT INTO theStores (store_name, store_description, store_phone, store_email, store_status, available_boxes, start_time, end_time, sold_boxes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
		parameters = (store_name, store_description, store_phone, store_email, "active", available_boxes, start_time, end_time, 0)
		result = engine.execute(insert_statement, parameters)
		#mycursor.execute(insert_statement, parameters)
		#mydb.commit()
		return redirect(url_for("ninja"))

@app.route('/delete/<string:store_id>')
def delete(store_id):

		#mycursor.execute("DELETE FROM theStores WHERE store_id = %s" % store_id)
		#mydb.commit()
		result = engine.execute("DELETE FROM theStores WHERE store_id = %s" % store_id)
		return redirect(url_for('ninja'))

@app.route('/edit/<string:store_id>')
def edit(store_id):

	#mycursor.execute("SELECT * FROM theStores WHERE store_id = %s" % store_id)
	#data = mycursor.fetchall()
	result = engine.execute("SELECT * FROM theStores WHERE store_id = %s" % store_id)
	result = result.fetchall()
	return render_template("edit_contact.html", contact = result[0])
	#mycursor.execute("UPDATE stores SET store_name = %s, store_description = %s, store_phone = %s, stores_status = %s, available_boxes = %s, sold_boxes = %s" )

@app.route('/update/<string:store_id>', methods=["POST"])
def update(store_id):

	if request.method == "POST":
		store_name = request.form["store_name"]
		store_description = request.form["store_description"]
		store_phone = request.form["store_phone"]
		available_boxes = request.form["available_boxes"]
		store_email = request.form["store_email"]
		start_time = request.form["start_time"]
		end_time = request.form["end_time"]
		update_statement = ("UPDATE theStores SET store_name = %s, store_description = %s, store_phone = %s, store_email = %s, start_time = %s, end_time = %s, available_boxes = %s WHERE store_id = %s")
		parameters = (store_name, store_description, store_phone, store_email, start_time, end_time, available_boxes, store_id)
		result = engine.execute(update_statement, parameters)
		#mycursor.execute(update_statement, parameters)
		return redirect(url_for('ninja'))


#ISTO é o route que usei com <form> em vez de href
# @app.route('/<int:store_id>', methods=["POST"])
# def stores1(store_id):
#     if request.method == "POST":
#         #select_query = "SELECT * FROM stores"
#         mycursor.execute("SELECT * FROM stores WHERE store_id = %s" % store_id)
#         result = mycursor.fetchone()
#         print(result)
#         return render_template("work.html", store_name = result[1], store_description = result[2], store_status = result[3], number_of_boxes = result[4])







# @app.route('/submit_form', methods=["POST", "GET"])
# def submit_form():
#     if request.method == "POST":
#     	data = request.form.to_dict()
#     	write_to_csv(data)
#     	return redirect("thankyou.html")
#     else:
#     	return "failed"

# def write_to_file_json(data): #JSON Format
# 	with open("database.txt", "a") as database:
# 		database.write(json.dumps(data))

# def write_to_file(data): #Desfazendo o dict e append os valores em separado
# 	with open("database.txt", "a") as database:
# 		email = data["email"]
# 		subject = data["subject"]
# 		message = data["message"]
# 		database.write(f"\n{email}, {subject}, {message}")

# def write_to_csv(data): #Desfazendo o dict e append os valores em separado
# 	with open("database.csv", "a", newline='') as database_csv:
# 		email = data["email"]
# 		subject = data["subject"]
# 		message = data["message"]
# 		csv_writer = csv.writer(database_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
# 		csv_writer.writerow([email, subject, message])













# if __name__ == "__main__":
#     app.run()
