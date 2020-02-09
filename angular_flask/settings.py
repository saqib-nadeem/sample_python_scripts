#--------Flask Config------------
DEBUG = True
SECRET_KEY = '' # read it from env variables

#--------DB Config------------
MONGODB_SETTINGS = {
	'DB':  'meraq',
	'USERNAME': 'saqib',
	'PASSWORD': '', # read it from env variables
	'HOST': 'localhost',
	'PORT': 45011
}
