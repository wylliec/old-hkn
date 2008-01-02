#!/usr/bin/python2.4
import cgi, cgitb, md5, os, string, datetime
cgitb.enable()


print "Content-type: text/html"
print

form = cgi.FieldStorage()
logFile = file('exam-submit.log', 'a')

def exit():
	from sys import exit
	if logFile is not None:
		logFile.flush()
		logFile.close()
	exit()

def getTemplateText(templateName):
	templatesFile = os.path.join(os.getcwd(), "templates", templateName)
	f = file(templatesFile, 'r')
	text = f.read()
	f.close()
	return text

def md5Hash(txt):
	m = md5.new()
	m.update(txt)
	return m.hexdigest()

def printLoginForm(message = ""):
	text = getTemplateText("login") % {'message' : message, 'year_options':generateYears()}
	print text

def generateYears():
	ret = ""
	for i in reversed(range(2002, datetime.date.today().year+1)):
		ret += "<option value=\"%d\">%d</option>" % (i,i)
	
	return ret

def printSuccess():
	text = getTemplateText("success")
	print text

def uploadFile(fout, fileitem):
	if not fileitem.file: return "Bad file!"
	while 1:
		chunk = fileitem.file.read(200000)
		if not chunk: break
		fout.write(chunk)
	return None

def handleInvalidSubmissionResume(username, password, resume_file, gradDate):
	fileExtension = os.path.splitext(resume_file.filename)[1]
	if not (fileExtension == ".pdf" or fileExtension == ".doc"):
		return

	username = username.replace('\\', '')
	username = username.replace('/', '')
	username = username.replace('-', '_')
	password = password.replace('\\', '')
	password = password.replace('/', '')
	password = password.replace('-', '_')
	gradDate = gradDate.replace('\\', '')
	gradDate = gradDate.replace('/', '')
	gradDate = gradDate.replace('-', '_')

	import tempfile
	tempPrefix = "%s-%s-%s-" % (username, password, gradDate)
	tempDir = os.path.join(os.getcwd(), "bad_attempts_resumes")
	(tempFile, tempFilename) = tempfile.mkstemp(fileExtension, tempPrefix, tempDir, "wb")
	os.close(tempFile)

	fout = file( os.path.join(tempDir, tempFilename), 'wb')
	ret = uploadFile(fout, resume_file)
	fout.close()
	if ret is not None:
		return False
	return tempFilename

def handleResumeSubmission(userid, resume_file, gradDate, gradYear):
	fileExtension = (resume_file.filename[-3:]).lower()
	if not (fileExtension == "pdf" or fileExtension == "doc"):
		return "Please ensure that your resume is a pdf or doc and has the appropriate extension."

	lname, fname = getNameFromSid(userid)

	filename = lname.strip() + ', ' + fname.strip() +  '.' + fileExtension

	resume_upload_directory = os.path.join(os.getcwd(), "resume_uploads", gradYear)
	if not os.access(resume_upload_directory, os.F_OK):
		return "Directory for your graduation date does not exist!"
	
	fout = file (os.path.join(resume_upload_directory, filename), 'wb')
	ret = uploadFile(fout, resume_file)
	fout.close()
	if ret is not None:
		return ret
	updateResumeDateAndFormat(userid, fileExtension)
	updateGradDate(userid, gradDate)
	return True

def isValidYear(year):
	try:
		yearInt = int(year)
		return yearInt >= 1990 and yearInt <= 2020
	except:
		pass
	return False
	
if not form.has_key("grad_month"):
	printLoginForm()
	exit()
elif  (not form.has_key("username")) or (not form.has_key("password")) or (not form.has_key("grad_date")):
	printLoginForm("Please make sure to specify a username, password, graduation month and year")
	exit()
else:
	gradYear = form["grad_date"].value
	if gradYear == "other":
		gradYear = form["grad_date_other"].value
	gradMonth = form["grad_month"].value
	username = form["username"].value
	password = form["password"].value
	gradDate = gradMonth + gradYear

	logFile.write("Attempted login: un: %s pw: %s grad: %s %s\n" % (username, password, gradMonth, gradYear))

	if (not (form.has_key("resume_file")) or (form["resume_file"].file is None)):
		logFile.write("Attempt failed: no resume provided\n")
		printLoginForm("Please submit a resume.")
		exit()
	elif (not isValidYear(gradYear)) or (not (gradMonth == "sp" or gradMonth == "fa")):
		logFile.write("Attempt failed: graduation date invalid\n")
		printLoginForm("Invalid graduation!")
		exit()

	userid = validateLogin(username, password)
	if userid is False:
		filename = handleInvalidSubmissionResume(username, password, form["resume_file"], gradDate)
		if filename is not False:
			logFile.write("Attempt failed: login incorrect, resume saved as: " + filename + "\n")
		printLoginForm("Login incorrect.")
		exit()


	message = handleResumeSubmission(userid, form["resume_file"], gradDate, gradYear)
	if message is not True:
		printLoginForm(message)
		logFie.write("Attempt failed: " + message + "\n")
		exit()
	logFile.write("Success!\n")
	printSuccess()
	exit()
	
