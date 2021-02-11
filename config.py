import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class BaseConfig(object):
	DEBUG = False
	TEMPLATES_AUTO_RELOAD = True
	SESSION_COOKIE_HTTPONLY = True
	SESSION_COOKIE_SECURE = True
	#used to generate client side security. The key value should stay the same, otherwise sessions (cookies) would be invalid after a server crash/restart
	SECRET_KEY = "bb8NfvRFyHRewqtF_UkOaA"
	MYSQL_HOST = 'localhost'
	MYSQL_USER = os.environ.get('MYSQL_USER')
	MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
	MYSQL_DB = 'findo'
	MYSQL_CURSORCLASS = 'DictCursor'

class DevelopmentConfig(object):
	DEBUG = True
	# NEED THIS to update templates with a hard refresh in browser
	TEMPLATES_AUTO_RELOAD = True
	SESSION_COOKIE_HTTPONLY = True
	ESSION_COOKIE_SECURE = True
	SECRET_KEY = "bb8NfvRFyHRewqtF_UkOaA"
	MYSQL_HOST = 'localhost'
	MYSQL_USER = os.environ.get('MYSQL_USER')
	MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
	MYSQL_DB = 'findo'
	MYSQL_CURSORCLASS = 'DictCursor'
