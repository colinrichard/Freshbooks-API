from flask import Flask, request, redirect, session, url_for
from flask import render_template
from flask.json import jsonify
from datetime import datetime
import os
import requests, json
#import urllib2
import company
import Client
import Invoice
import time

#data object to communicate with freshbooks' API to retrieve user data

#   **For API Documentation look at Freshbooks' developer site**
#   ** https://www.freshbooks.com/api/start ** 

class FbData(object):
	#attributes of the data object
	client_id = None
	client_secret = None
	authorization_base_url = None
	bearer = None
	company_list = []
	invoice_list = []
	current_company = None
	client_list = []
	
	#initializes data object with the client ID, client secret and authorization URL of your application
	def __init__(self):

		self.client_id = 'aa086d0ba43285f8ba45603132abe38cbf450090d510a5b23230dd1ab843c74d'
		self.client_secret = '815ce57d07e2808e52006ccd3c6fb352bc0f224eefe0314326b4fb70676e1c3a'
		self.authorization_base_url = 'https://my.freshbooks.com/service/auth/oauth/authorize?client_id=aa086d0ba43285f8ba45603132abe38cbf450090d510a5b23230dd1ab843c74d&response_type=code&redirect_uri=https://localhost:5000/placeholder'
	

	#function that sends Freshbooks the authorization code and retrives the bearer used for API calls. 
	def setToken(self, code):
		#API URL for Authentication
		url = "https://api.freshbooks.com/auth/oauth/token"
		#data needed for the post call
		payload = {'grant_type': 'authorization_code', 'client_secret': str(self.client_secret),'code': code, 'client_id': str(self.client_id), 'redirect_uri': 'https://localhost:5000/placeholder'}
		#needed header information
		headers = {'Api-Version': 'alpha', 'Content-Type': 'application/json'}
		#Sending/Retrieving from freshbooks
		res = requests.post(url, data=json.dumps(payload), headers=headers)
		#loading the returned response into json
		jsonData = res.json()
		#saving bearer to the data object
		self.bearer = jsonData["access_token"]

	#function that loads the user's companies
	def get_company_info(self):
		#deletes the old list to update to a new list
		del self.company_list[:]
		del self.client_list[:]

		#API URL for user information
		url = "https://api.freshbooks.com/auth/api/v1/users/me"
		#API headers
		headers = {'Authorization': 'Bearer ' + str(self.bearer), 'Api-Version': 'alpha', 'Content-Type': 'application/json'}
		# Storing response
		res = requests.get(url, data=None, headers=headers)
		#Converting response to JSON
		jsonData = res.json()
		#getting number of companies and making variable for name and id of companies
		company_length = len(jsonData['response']['business_memberships'])
		company_name = None
		company_id = None
		#for loop to add all companies to company list in data object
		for index in range(company_length):

			company_name = str(jsonData['response']['business_memberships'][index]['business']['name'])
			company_id = str(jsonData['response']['business_memberships'][index]['business']['account_id'])

			self.company_list.append(company.Company(company_name, company_id))	

	# retrives company ID
	def find_id(self, name):

		company_length = len(self.company_list)

		for x in range(company_length):
		
			if self.company_list[x].get_name() == name:
				#sets current company to the company user logs into 
				self.current_company = self.company_list[x].get_id()
				return self.company_list[x].get_id()


		return "Could not find id"

	#lists all the clients under the company user selected
	def list_clients(self, id):
		#delete old list
		del self.client_list[:]
		#API URL for list of clients
		url = "https://api.freshbooks.com/accounting/account/" + str(id) + "/users/clients"
		#API header
		headers = {'Authorization': 'Bearer ' + str(self.bearer), 'Api-Version': 'alpha', 'Content-Type': 'application/json'}
		#getting client(s) data and converting to JSON
		res = requests.get(url, data=None, headers=headers)
		jsonData = res.json()
		#initializing client data
		client_length = len(jsonData['response']['result']['clients'])
		client_fname = None
		client_lname = None
		client_org = None
		#looping through client json file to make and add client objects to the data object
		for x in range(client_length):

			client_fname = str(jsonData['response']['result']['clients'][x]['fname'])	
			client_lname = str(jsonData['response']['result']['clients'][x]['lname'])
			client_org = str(jsonData['response']['result']['clients'][x]['organization'])
			self.client_list.append(Client.Client(client_fname, client_lname, client_org))

	#lists invoices under the company the user has selected
	def list_invoices(self, id):
		#deletes old invoice list
		del self.invoice_list[:]
		#API URL for listing invoices
		url = "https://api.freshbooks.com/accounting/account/" + str(id) + "/invoices/invoices"
		#API header
		headers = {'Authorization': 'Bearer ' + str(self.bearer), 'Api-Version': 'alpha', 'Content-Type': 'application/json'}
		#retrieving data and converting to JSON
		res = requests.get(url, data=None, headers=headers)
		jsonData = res.json()
		#invoice data 
		invoice_length = len(jsonData['response']['result']['invoices'])
		invoice_fname = None
		invoice_lname = None
		invoice_status = None
		invoice_pay_status = None
		v3_status = None 
		invoice_create_date = None
		invoice_amount = None 
		invoice_id = None
		#initializing invoice objects and adding to invoice_list
		for x in range(invoice_length):
			invoice_fname = str(jsonData['response']['result']['invoices'][x]['fname'])
			invoice_pay_status = str(jsonData['response']['result']['invoices'][x]['payment_status'])
			invoice_lname = str(jsonData['response']['result']['invoices'][x]['lname'])
			invoice_status = str(jsonData['response']['result']['invoices'][x]['status'])
			v3_status = str(jsonData['response']['result']['invoices'][x]['v3_status'])
			invoice_create_date = str(jsonData['response']['result']['invoices'][x]['create_date'])
			invoice_amount = str(jsonData['response']['result']['invoices'][x]['outstanding']['amount'])
			invoice_id = str(jsonData['response']['result']['invoices'][x]['id'])

			self.invoice_list.append(Invoice.Invoice(invoice_status, invoice_create_date, invoice_amount, invoice_pay_status, invoice_id, v3_status, invoice_fname, invoice_lname))

	# pays invocie with a given amount		
	def pay_invoice(self, invoice_id, amount):

		#Used to check for negative amounts
		a = int(amount)
		if a < 0:
			a = 0	
		#API URL for making a payment		
		url = "https://api.freshbooks.com/accounting/account/" + str(self.current_company) + "/payments/payments"
		#API header
		headers = {'Authorization': 'Bearer ' + str(self.bearer), 'Api-Version': 'alpha', 'Content-Type': 'application/json'}
		#data needed for API (invoice number & payment amount)
		payload = { 'payment': {'invoiceid': invoice_id, 'amount': {'amount': str(a)}, 'date': time.strftime('%Y-%m-%d'), 'type': "credit"} }
		#posting data
		print(time.strftime('%Y-%m-%d'))
		res = requests.post(url, data=json.dumps(payload), headers=headers)
	
	# creating a client			
	def create_client(self, fname, lname, org):
		#API URL for client creation		

		url = "https://api.freshbooks.com/accounting/account/" + str(self.current_company) + "/users/clients"
		#API header
		headers = {'Authorization': 'Bearer ' + str(self.bearer), 'Api-Version': 'alpha', 'Content-Type': 'application/json'}
		#API data (you can choose fields you want, this example is first name, last name and organization)
		payload = {'client': { 'fname': str(fname), 'lname': str(lname), 'organization': str(org) } }
		#posting data
		res = requests.post(url, data=json.dumps(payload), headers=headers)

	

