from util.sessions import Session
import os
import logging
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db

#A Model for a User
class User(db.Model):
	acct = db.StringProperty()
	pw = db.StringProperty()
	name = db.StringProperty()

# A helper to do the rendering and to add the necessary variables for _base.htm
def doRender(self, tname = "index.htm", values = {}):
    logging.info(tname)
    temp = os.path.join(os.path.dirname(__file__), 'templates/' + tname)
    if not os.path.exists(temp):
      return False

    # Make a copy of the dictionary and add basic values
    newval = dict(values)
    if not 'path' in newval:
        path = self.request.path
        newval['path'] = self.request.path

    if not 'username' in newval:
	self.session = Session()
	if 'username' in self.session:
		newval['username'] = self.session["username"]

    outstr = template.render(temp, newval)
    self.response.out.write(outstr)
    return True

class ApplyHandler(webapp.RequestHandler):
	def get(self):
		doRender(self, 'apply.htm')
		
	def post(self):
		self.session = Session()
		xname = self.request.get('name')	
		xacct = self.request.get('account')
		xpw = self.request.get('password')
		logging.info("Adding account="+xacct)
		
		if xpw == "" or xacct == "" or xname == "":
			doRender(self,"login.htm",{'error' : 'Please fill all fields'})
		#Check for a user already existing
		que = db.Query(User).filter("acct =",xacct)
		results = que.fetch(limit=1)
		
		if len(results) > 0:
			doRender(self,"apply.htm",{'error' : 'Account already exists'})
			return
		
		newuser = User(name=xname, acct=xacct, pw=xpw)
		newuser.put()
		self.session['username'] = xacct
		doRender(self,"index.htm",{})

class LoginHandler(webapp.RequestHandler):

  def get(self):
    if doRender(self, 'login.htm'):
       return
    self.response.out.write("Error - login.htm template not found")

  def post(self):
    self.session = Session()
    
    acct = self.request.get('account')
    pw = self.request.get('password')
    logging.info("Checking account="+acct+" pw="+pw)
    #self.session.delete('username')
    if pw == "" or acct == "":
      doRender(self,"login.htm",{'error' : 'Please specify Account and Password'} )
      return
    #elif pw == "secret":
     # self.session['username'] = acct
     # doRender(self,"index.htm",{ } )
     
    que = db.Query(User).filter("acct =",acct).filter("pw = ",pw)
    results = que.fetch(limit=1)
    if len(results) > 0:
	    self.session['username'] = acct
	    doRender(self,"index.htm",{})
    else:
      doRender(self,"login.htm",{'error' : 'Incorrect login data'} )

class LogoutHandler(webapp.RequestHandler):
	
	def get(self):
		self.session = Session()
		self.session.delete('username')
		doRender(self, 'index.htm')

class ListHandler(webapp.RequestHandler):
	
	def get(self):
		que = db.Query(User)
		user_list = que.fetch(limit=100)
		if doRender(self, 'list.htm', {'user_list': user_list}):
			return
		self.response.out.write("Error - list.htm not found")
		
class AddHandler(webapp.RequestHandler):
	def get(self):
		doRender(self, 'add.htm')
		
	def post(self):
		self.session = Session()
		xname = self.request.get('name')	
		xacct = self.request.get('account')
		logging.info("Adding account="+xacct)
		
		if xpw == "" or xacct == "" or xname == "":
			doRender(self,"add.htm",{'error' : 'Please fill all fields'})
		#Check for an entry already existing?
		que = db.Query(User).filter("acct =",xacct)
		results = que.fetch(limit=1)
		
		if len(results) > 0:
			doRender(self,"add.htm",{'error' : 'Entry already exists'})
			return
		
		newuser = User(name=xname, acct=xacct, pw=xpw)
		newuser.put()
		self.session['username'] = xacct
		doRender(self,"list.htm",{})
		
class MainHandler(webapp.RequestHandler):

  def get(self):
    path = self.request.path
    if path == "/":
      path = "index.htm"
    if doRender(self,path) : 
      return
    if doRender(self,"index.htm") : 
      return
    self.response.out.write("Error - unable to find index.htm")

def main():
  application = webapp.WSGIApplication([
     ('/login', LoginHandler),
     ('/logout', LogoutHandler),
     ('/apply', ApplyHandler),
     ('/add', AddHandler),
     ('/list.htm', ListHandler),
     ('/.*', MainHandler)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
