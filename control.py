from flask import Flask, request, redirect, session, url_for
from flask import render_template
from flask.json import jsonify
import requests, json
import company
import fbdata
import Client 

#flask application
app = Flask(__name__)

#data object to make calls to Freshbook Data
d = fbdata.FbData()
#index page
@app.route("/")
def index():
	return render_template('index.html')

#Authentication Page
@app.route("/auth/")
def hello():
	return redirect(d.authorization_base_url, code=302)
#Authorization redirects back to here
@app.route("/placeholder/")

def placeholder():
	
	# retreives authentication code that freshbook sends back through URL
	code = request.args.get('code')
	#sends authentication code back to Freshbooks and gets bearer in return and then save in data variable
	d.setToken(code)
	#Retrieves all the company info of user logged in
	d.get_company_info()
	#returns new page displaying user with the choice to pick which company to proceed with (User probably has only one)
	return render_template('company.html', companies = d.company_list, cLength = len(d.company_list))

#Routes here after user selects their company
@app.route("/options/")

def options():
	#Retrieves their company name and ID used for later API calls for their data
	compName = request.args.get('cName')

	d.find_id(compName)

	return render_template('options.html')

#If user selects Clients redirects here
@app.route("/clients/")

def clientList():
	#populates client_list in data varaible with the clients of their company they selected
	d.list_clients(d.current_company)
	#sends data to HTML page to be displayed
	return render_template('clients.html', clients = d.client_list, lengthC = len(d.client_list))
#user wants to create a new client
@app.route("/clients/create")

def createClient():
#loads new html page to allow for data entry from user
	return render_template('createclient.html')
#User submits new client
@app.route("/clients/confirm")

def confirmClient():
	#retrives new client info from URL
	fname = request.args.get('first')
	lname = request.args.get('last')
	org = request.args.get('company')
	eligibility = False

	if ((fname == "" or lname == "") and org == ""):
		eligibility = False
	else:
		#creates new client
		d.create_client(fname, lname, org)
		#updates client list of their company
		d.list_clients(d.current_company)
		#confirmation HTML page
		eligibility = True

	return render_template('confirmclient.html', makeClient = eligibility)

# user selects Invoices
@app.route("/invoices/")

def invoices():

	#lists the invoices
	d.list_invoices(d.current_company)

	#HTML page to display invocies
	return render_template('invoices.html', invoices = d.invoice_list, lengthI = len(d.invoice_list))

#user wants to pay an invoice
@app.route("/invoices/pay/")

def payInvoice():
	#retrives invoice id through URL
	invoice_id = request.args.get('id')
	#redirects to payment HTML page with the invoice ID
	return render_template('payInvoice.html', d = invoice_id)
#Once payment is submitted 
@app.route("/invoices/pay/<path:code>")

def recieveAmount(code):
	#gets the amount the user would like to pay
	amountPaid = request.args.get('payamount')

	#Calculates new invoice amount
	d.pay_invoice(code, amountPaid)
	#updates list on invoices
	d.list_invoices(d.current_company)
	#confirmation HTML page
	return render_template('payconfirm.html')

#self assigned certificate
if __name__ == "__main__":
	app.run(ssl_context='adhoc')





