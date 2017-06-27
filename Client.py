#client class to hold client data
class Client(object):
	
	__fname = None
	__lname = None
	__org = None
#client initializing constructor 
	def __init__(self, fname, lname, org):
		self.__fname = fname
		self.__lname = lname
		self.__org = org
#getters and setters
	
	def get_fname(self):
		return self.__fname

	def get_lname(self):
		return self.__lname

	def get_org(self):
		return self.__org

	def set_lname(self, name):
		self.__lname = name

	def set_fname(self, name):
		self.__fname = name

	def set_org(self, org):
		self.__org = org