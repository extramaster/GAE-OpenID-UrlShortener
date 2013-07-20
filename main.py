import logging
import cgi
import wsgiref.handlers
import random
import urllib
import os
import sys


from urlparse import urlparse

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


# OpenID providers listed here:
providers = {
'Google (preferred)'   : 'https://www.google.com/accounts/o8/id',
'Yahoo (preferred)'    : 'yahoo.com',
'AOL'      : 'aol.com',
'MyOpenID' : 'myopenid.com',
'ClaimID':'http://openid.claimid.com',
'mozilla':'mozilla.com'
}

user = ""


# Code to deal with the generation, storage and retrieval of shortened link code
class UrlData(db.Model):
	url = db.StringProperty()
	code = db.StringProperty()
	user = db.StringProperty()

class newUrl:
	CodeFrom = "abcdefghijklmnopqrstuvwxyz1234567890"
	def __init__(self, url):	
		self.url = url
		self.user = user
	def checkCode(self):
		if len(self.code) < 3:
			return 1
		back = UrlData.gql("WHERE code = :1 LIMIT 1", self.code)
		return back.count(1) > 0
	def makeCode(self):
		self.code = str(random.randint(0,9))
		while self.checkCode():
			self.code += self.CodeFrom[random.randint(0, len(self.CodeFrom) - 1)]
	def build(self):
		self.makeCode()
		info = UrlData(url = self.url, code = self.code, user = self.user)
		info.put()
		return self.code

def getCode(url):
	# get the code for the url
	data = UrlData.gql("WHERE url = :1 LIMIT 1", url)
	if data.count(1) > 0:
		return data.fetch(1)[0].code
	else:
		u = newUrl(url)
		return u.build()
	
def getUrl(code):
	# get the url from the code
	data = UrlData.gql("WHERE code = :1 LIMIT 1", code)
        url = ""
        for urls in data:
                url = urls.url
        return url


class UserPair(db.Model):
	user = db.StringProperty()
	username = db.StringProperty()

def newUser(user,username):
	info = UserPair(user=user, username=username)
	info.put()

def getUser(user):
	# get the url from the code
	data = UserPair.gql("WHERE user = :1 LIMIT 1", user)
        url = ""
        for urls in data:
                url = urls.username
        return url


# Where the web interface is handled
class UrlHandler(webapp.RequestHandler):

	def get(self, parm = ""):
		url = ""
		code = ""
		if parm == 'create':
			parm = self.request.get('url')
		if len(parm) > 0:
			if parm.lower().startswith('http'):
				code = getCode(parm)
			else:
				url = getUrl(parm)
				if len(url) > 0:
					url = urllib.unquote_plus(url)
					self.redirect(url)
					self.response.headers.add_header("Window-target", "_top")
					self.response.out.write("<html><head><META HTTP-EQUIV=\"Refresh\" CONTENT=\"0;URL=" + url + "\"><META HTTP-EQUIV=\"Window-target\" CONTENT=\"_top\"><script type='text/javascript'>top.location.href='" + url + "';</script></head><body></body></html>")
					return
		urlDict=["index","","register","create","login","index"]

		isConf="false"
		for pram in urlDict:
			if parm.lower().startswith(pram):
				isConf="true"
		if isConf=="false":
			self.response.out.write("<html><head></head><body>Nope! Nothing here...</body></html>")
		global user
		user = users.get_current_user();
		if user:
			user = str(user.nickname())
		else:
			user = ""
		if user and parm != 'register':
			if getUser(user)=="":
				self.redirect("/register")
			user=getUser(user)
			url = urllib.unquote_plus(parm)
			disp_url = url
			if len(disp_url) > 40:
				disp_url = disp_url[0:40] + '...'
			template_values = {
			'code': code,
			'url': url,
			'disp_url': disp_url,
			'parsedContent':self.request.host_url+"/"+code,
			'twitter':"http://twitter.com/home?status="+urllib.quote(self.request.host_url+"/"+code),
                        'username':user,
                        'logoutlink':users.create_logout_url(self.request.uri)
			}
			if len(code) == 0:
				path = os.path.join(os.path.dirname(__file__), 'index.html')
			else:
				path = os.path.join(os.path.dirname(__file__), 'create')
			self.response.out.write(template.render(path, template_values))
		elif parm == 'login':
			providerz=''
			for name, uri in providers.items():
				providerz+=('[<a href="%s">%s</a>]' % (
					users.create_login_url(federated_identity=uri), name))
			template_values = {
			'provider':providerz
			}
			path = os.path.join(os.path.dirname(__file__), 'login')
			self.response.out.write(template.render(path, template_values))
		elif parm == 'register':
			parm = user
			parm3 = self.request.get('setnick')
			if getUser(parm)!="":
				self.redirect("/")
			if parm3:
				newUser(user,parm3)
				self.redirect("/")
			elif parm:
				template_values = {
                        	'logoutlink':users.create_logout_url(self.request.uri)
				}
				path = os.path.join(os.path.dirname(__file__), 'register')
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect("/")
			

		else:     # let user choose authenticator
			self.redirect("/login")

def hostnameGet(url):
    return urlparse(url)[1]

def main():
  application = webapp.WSGIApplication([('/', UrlHandler)],
                                       debug=True)
  application = webapp.WSGIApplication([('/(.*)', UrlHandler)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)
if __name__ == '__main__':
  main()
