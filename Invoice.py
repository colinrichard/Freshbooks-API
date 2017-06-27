#class for invoices
class Invoice (object):
	#attributes 
	status = None
	create_date = None
	amount = None
	payment_status = None
	invoice_id = None
	v3_status = None
	fname = None
	lname = None


	#initalizer of invoice
	def __init__(self, status, create_date, amount, payment_status, invoice_id, v3_status, fname, lname):
		
		self.status = status
		self.fname = fname
		self.lname = lname
		self.create_date = create_date
		self. amount = amount
		self.payment_status = payment_status
		self.invoice_id = invoice_id
		self.v3_status = v3_status


	
