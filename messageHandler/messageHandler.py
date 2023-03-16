# import warnings
# warnings.filterwarnings("ignore")

class MessageHandler:

	def __init__(self, message):
		self.botName = "yati"
		self.response = []
		self.possibleCommands = [
			"result", "marks", "grade", "grades", "gradecard", 
			"astatus", 
			"name",
			"enrolment", "enrol"]
		self.message = message.lower()

	async def handleMessage(self):

		# Check if mentioned, return if not
		mentioned = await self.isMentioned()
		if not mentioned: 
			return []
		
		# Parse Message
		messageParts = self.message.split()

		# Check the command
		command, dataParts = self.getCommand(messageParts)

		# Return if command didn"t match
		if command is None:
			return [(0, None, "Sorry! I did not understand")]
		
		self.response = []

		# Perform action based on command
		if command in ["marks", "result", "grade", "gradecard", "grades"]:
			requiredResponse = await self.getMarksResponse(dataParts)
			if requiredResponse[-1] is None:
				requiredResponse = await self.getResultResponse(dataParts)
			self.response.append(requiredResponse)
		
		elif command in ["name"]:
			requiredResponse = await self.getNameResponse(dataParts)
			self.response.append(requiredResponse)
		
		elif command in ["enrolment", "enrol"]:
			requiredResponse = self.getEnrolmentResponse(dataParts)
			self.response.append(requiredResponse)
		
		# elif command in ["result"]:
		# 	resultResponse = await self.getResultResponse(dataParts)
		# 	self.response.append(resultResponse)

		return self.response

	async def getMarksResponse(self, dataParts):
		studentName = []
		session = None

		for dataPart in dataParts:
			if self.isValidSession(dataPart):
				session = dataPart
				continue
			studentName.append(dataPart)

		if len(studentName) < 1:
			return (0, None, "```Make sure to include Name or Enrolment!```")
		if session is None:
			return (0, None, None)

		studentName = " ".join(studentName)
		enrolmentNumber = self.getEnrolmentNumber(studentName)

		if enrolmentNumber is None:
			return (0, None, "```Enrolment not found!```")

		marksResponse = await self.fetchMarks(enrolmentNumber, session)

		if len(marksResponse) < 1:
			return (0, None, "```Something went wrong!\nCheck your input and try again!```")

		marksResponse = self.formatMarksResponse(studentName, marksResponse)
		return (1, None, marksResponse)

	async def fetchMarks(self, enrolmentNumber, session):
		import requests
		from bs4 import BeautifulSoup

		url = "https://termendresult.ignou.ac.in/TermEnd{}/TermEnd{}.asp".format(session.capitalize(), session.capitalize())
		params = {"eno":enrolmentNumber, "myhide":"OK"}

		urlResponse = requests.post(url, params = params, verify=False)
		htmlParser = BeautifulSoup(urlResponse.text, "html.parser")

		usefulData = [x.get_text() for x in htmlParser.find_all("strong")][1:]
		requiredData = []

		for i in range(0, len(usefulData), 5):
			requiredData.append((usefulData[i].strip(), usefulData[i+1].strip(), usefulData[i+2].strip()))

		return requiredData

	def formatMarksResponse(self, studentName, marksResponse):
		requiredResponse = f"Subject     Marks\n---------------------\n"
		for subject in marksResponse:
			requiredResponse += self.fillString(subject[0], " ", 12, 1)
			requiredResponse += self.fillString(subject[1], "0", 3, -1) + " (" + self.fillString(subject[2], "0", 3, -1) + ")"
			requiredResponse += "\n"
		requiredResponse = f"*{studentName}*\n\n" + "```" + requiredResponse + "```"
		return requiredResponse

	async def getResultResponse(self, dataParts):
		studentName = " ".join(dataParts)

		if len(studentName) < 1:
			return (0, None, "```Make sure to include Name or Enrolment!```")

		enrolmentNumber = self.getEnrolmentNumber(studentName)
		if enrolmentNumber is None:
			return (0, None, "```Enrolment not found!```")

		resultResponse = await self.fetchResult(enrolmentNumber)

		if len(resultResponse) < 1:
			return (0, None, "```Something went wrong!\nCheck your input and try again!```")
		
		resultResponse = self.formatResultResponse(resultResponse)

		return (1, None, resultResponse)
	
	async def fetchResult(self, enrolmentNumber, program = "BCA", typeProgram = 1):
		import requests
		from bs4 import BeautifulSoup

		url = "https://gradecard.ignou.ac.in/gradecard/view_gradecard.aspx"
		params = {"eno":enrolmentNumber, "prog":program, "type": typeProgram}

		urlResponse = requests.post(url, params = params, verify=False)
		htmlParser = BeautifulSoup(urlResponse.text, "html.parser")

		name = htmlParser.find(id="ctl00_ContentPlaceHolder1_lblDispname").get_text()
		if len(name)==0:
			return []

		tables = htmlParser.find_all("table")
		dataTable = tables[-2]
		content = dataTable.find_all("font")
		content = [x.get_text() for x in content]
		requiredData = [name]
		percentageCalculations = [[], []]
		for i in range(9, len(content)-9, 9):
			subjectName = content[i]
			assignmentMarks = content[i+1]
			termEndMarks = content[i+6]
			practicalMarks = content[i+7]
			passStatus = "grey_tick_emoji" if "NOT" in content[i+8] else "green_tick_emoji"
			if assignmentMarks != "-":
				percentageCalculations[0].append(int(assignmentMarks))
			if termEndMarks != "-":
				percentageCalculations[1].append(int(termEndMarks))
			if practicalMarks != "-":
				percentageCalculations[1].append(int(practicalMarks))

			requiredData.append((subjectName, assignmentMarks, termEndMarks, practicalMarks, passStatus))
		requiredData.append("Percentage: {0:.2f}".format(
			( ( sum(percentageCalculations[0]) / len(percentageCalculations[0]) ) * .25 +
    		  ( sum(percentageCalculations[1]) / len(percentageCalculations[1]) ) * .75 )
		))
		return requiredData
		return "lol"

		data = ["`"+" ".join([x.capitalize() for x in name.split()])+"`", "", "`Sub         A    T    P`"]
		assignmentMarks = []
		teeMarks = []
		for i in range(9, len(content)-9, 9):
			data.append("`"+adjStr(content[i], dataAd[0]) + adjStr(content[i+1], dataAd[1]) + adjStr(content[i+6], dataAd[2]) + adjStr(content[i+7], dataAd[3])+"`")
			if not content[i+1]=="-":
				assignmentMarks.append(int(content[i+1]))
			if content[i+7]!="-":
				teeMarks.append(int(content[i+7]))
			elif content[i+6]!="-":
				teeMarks.append(int(content[i+6]))
			data[-1] += "☑️" if "NOT" in content[i+8] else "✅"
		if not len(teeMarks):
			percentage = "Not much data"#sum(assignmentMarks)/len(assignmentMarks)
		else:
			try:
				percentage = .25 * (sum(assignmentMarks)/len(assignmentMarks)) + .75 * (sum(teeMarks)/len(teeMarks))
			except:
				percentage = "Not much data"
		data.append("")
		data.append("`Percentage: {0:.2f}`".format(percentage))
		return "\n".join(data)
	
	def formatResultResponse(self, resultResponse):
		studentName = resultResponse[0]
		percentage = resultResponse[-1]
		requiredResponse = f"Subject   A   T   P   \n"
		for subject in resultResponse[1:][:-1]:
			cur = self.fillString(subject[0], " ", 10, 1)
			cur += self.fillString(subject[1], " ", 4, 1)
			cur += self.fillString(subject[2], " ", 4, 1)
			cur += self.fillString(subject[3], " ", 4, 1)
			cur += subject[4]
			cur += "\n"
			requiredResponse += cur
		requiredResponse = "*" + studentName + "*\n\n" + "```" + requiredResponse + "\n" + percentage + "```"
		return requiredResponse.strip()

	def getEnrolmentResponse(self, dataParts):
		studentName = " ".join(dataParts)
		response = None
		if len(studentName) < 1:
			response = "```Invalid Input!```"
		else:
			enrolmentNumber = self.getEnrolmentNumber(studentName)
			if enrolmentNumber is None:
				response = "```Not Found!```"
			else:
				response = enrolmentNumber
		return (0, None, response)

	def getEnrolmentNumber(self, studentName):
		if studentName.isdigit():
			if len(studentName) != 10:
				return None
			else:
				return studentName
		enrolmentNumber = None
		with open("./messageHandler/data/ignou/enrolments.txt", "r") as file:
			lines = file.readlines()
			for line in lines:
				if studentName in line:
					enrolmentNumber = line.split()[-1]
					break
		return enrolmentNumber

	async def getNameResponse(self, dataParts):
		studentName = " ".join(dataParts)
		response = None
		if len(studentName) < 1:
			response = "```Invalid Input!```"
		else:
			enrolmentNumber = self.getEnrolmentNumber(studentName)
			if enrolmentNumber is None:
				response = "```Not Found!```"
			else:
				studentName = await self.getStudentName(enrolmentNumber)
				if studentName is None:
					response = "```Not Found!```"
				else:
					response = studentName
		return (0, None, response)

	async def getStudentName(self, enrolmentNumber, program = "BCA", typeProgram = 1):
		import requests
		from bs4 import BeautifulSoup

		url = "https://gradecard.ignou.ac.in/gradecard/view_gradecard.aspx"
		params = {"eno":enrolmentNumber, "prog":program, "type": typeProgram}

		urlResponse = requests.post(url, params = params, verify=False)
		htmlParser = BeautifulSoup(urlResponse.text, "html.parser")

		name = htmlParser.find(id="ctl00_ContentPlaceHolder1_lblDispname").get_text()
		if len(name)==0:
			return "Unknown"
		return name

	def isValidSession(self, session):
		if 6 >= len(session) >= 5 and session[-2:].isdigit():
			return True
		return False

	def fillString(self, string, symbol, length, direction):
		lengthDiff = length - len(string)
		if lengthDiff < 0:
			print("Length Overflow!")
		else:
			if direction > 0:
				string += symbol * lengthDiff
			elif direction < 0:
				string = symbol * lengthDiff + string
		return string

	def getCommand(self, messageParts):
		command = None
		dataParts = []
		skipBotname = False
		for part in messageParts:
			curPart = part.strip()
			if curPart == self.botName and not skipBotname: 
				skipBotname = True
				continue
			if curPart in self.possibleCommands:
				if command is None:
					command = curPart
				continue
			dataParts.append(curPart)
		return command, dataParts

	async def isMentioned(self):
		if self.botName in self.message.split(): return True
		return False