#Company class to hold information about the company
class Company:
	__name = None
	__account_id = None
#company initalizing constructor 
	def __init__(self,name, account_id):
		self.__name = name
		self.__account_id = account_id
#getters and setters
	def get_name(self):
		return self.__name

	def get_id(self):
		return self.__account_id

	def set_name(self,name):
		self.__name = name


	def set_id(self,id):
		self.__account_id = id

	
		
			
