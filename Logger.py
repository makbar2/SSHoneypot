import requests
import datetime
import json
import os

class Logger():
    def __init__(self, clientIP=None):
        self.clientIP = clientIP
        time =  datetime.datetime.now()
        self.time = time.strftime("%d-%m-%Y %H:%M:%S")
        self.commands = []
        self.attempts = []
        self.log = {
            "time" : self.time,
        }
        if(clientIP):
            self.findLocation()


    def findLocation(self)->bool:
        response = requests.get(f"http://ip-api.com/json/{self.clientIP}")
        jsonData = response.json()
        if(response.status_code == 200 and jsonData["status"] != "fail"):
            self.log["IPData"] = jsonData
            return True
        else:#api fail,private range, or invalid ip
            self.log["IPData"] = jsonData
            return False

    def updateStatus(self,status:str):
        """
            Sets the action of the log, created.

            Args:
            `status`: A string representing the action done by client to enter into the log.
                Valid strings are:

                    - connection probed
                    - login
                    - login fail
                    - banner error
            Raises: 
                `ValueError`: If the value of status is not a valid one.
        """
        match(status):
            case "probed":
                self.log["action"] = "connection probed"
            case "login":
                self.log["action"] = "login"
                self.log["login attempts"] = self.attempts
            case "login fail":
                if(len(self.attempts) == 0):
                    self.log["action"] = "no login attempted"
                    print("client didn't attmept to login")
                else:
                    self.log["action"] = "login fail"
                    self.log["login attempts"] = self.attempts
                    print("client failed to login")
            case "bannerError":
                self.log["action"] = "banner error"
            case _:
                raise ValueError("Value of status isn't valid")
        
        
    def addAttempt(self,name,password):
        print(f"login attempt: username:{name}, password:{password}")
        self.attempts.append([name,password])

    def writeLogFile(self):
        self.log["commands"] = self.commands
        jsonFile = json.dumps(self.log,indent=4)
        split = self.time.split()
        name  = split[0] + "_" + split[1]
        name = name.replace(":","-")
        with open(f"logs/{name}.json", "w") as f:
            f.write(jsonFile)
        f.close()
    
    def logCommand(self,command):
        self.commands.append(command)
    

    def totalHits(self):
        count = 0
        for i in os.listdir("logs"):
            count += 1
        return count


    def filterData(self):
        """
        Returns a json will all the logs, that don't come from a private range.
        """
        jsonList = []
        for i in os.listdir("logs"):
            with open(f"logs/{i}") as file:
                
                data = json.load(file)
                if(data["IPData"]["status"] != "fail"):
                    jsonList.append(data)        
            file.close()
        print(len(jsonList),"connections were recived")
        return jsonList
    

    def mostCommonCountry(self,):
        """
            print to the screen a list of all the countries where IP address originate from 
        """
        data = self.filterData()
        
        countries = {}
        for i in data:
            country = i["IPData"]["country"]
            if(country in countries):
                countries[country] += 1
            else:
                countries[country] = 1
        
        for i in sorted(countries):
            print(i, countries[i])

    def loginAttemptPerCountry(self):
        data = self.filterData()
        print("login attempts per country")
        countries = {}
        attempts = 0
        for i in data:
            #i changed the format of logging data, so i need to have this catch
            
            try:
                usernamePassword = i["login attempts"]
                count = len(usernamePassword)#one connection can have multiple attempts
                for x in range(count):
                    attempts +=1
                    if(usernamePassword != []):
                        country = i["IPData"]["country"]
                        if(country in countries):
                            countries[country] += 1
                        else:
                            countries[country] = 1
            except:
                pass
        print(f"number of attempts recived {attempts}")
        for i in sorted(countries):
            print(i, countries[i])

    def getMostUsedUsername(self):
        data = self.filterData()
        print("most used usernames")
        usernameDict = {}
        for i in data:
            #i changed the format of logging data, so i need to have this catch
            try:
                usernamePassword = i["login attempts"]
                if(usernamePassword != []):
                    for x in usernamePassword:
                        username = x[0]
                        if(username in usernameDict):
                            usernameDict[username] += 1
                        else:
                            usernameDict[username] =1
            except:
                pass
        for i in sorted(usernameDict):
            print(f"{i}: {usernameDict[i]}")

    def usernamePasswordCombo(self):
        
        data = self.filterData()
        combos = {}
        for i in data:
            #i changed the format of logging data, so i need to have this catch
            try:
                usernamePassword = i["login attempts"]
                if(usernamePassword != []):
                    for x in usernamePassword:
                        string = f"{x[0]} : {x[1]}"
                        if(string in combos):
                            combos[string] += 1
                        else:
                            combos[string] =1
            except:
                pass
        for i in sorted(combos):
            print(f"combonation: {i}, \n    {combos[i]}")

    

    def logsPerCountry(self,country):
        data = self.filterData()
        count = 0
        print("logs per country specified")
        for i in data:
            countryData = i["IPData"]["country"]
            if(countryData == country):
                count +=1
        print(f"number of logs from {country} were {count}")
    
    def getMostUsed(self,option:bool):
        """
            Args:
                option:bool `True` if you want to get passwords. `False` if you want to get usernames
        """
        data = self.filterData()
        if(option):
            key = 1#passwrod
            print("getting most ussed passwords")
        else:
            key = 0#username
            print("getting most used usernames")
        dataDict = {}
        for i in data:
            #i changed the format of logging data, so i need to have this catch
            try:
                usernamePassword = i["login attempts"]
                if(usernamePassword != []):
                    for x in usernamePassword:
                        value = x[key]
                        if(value in dataDict):
                            dataDict[value] += 1
                        else:
                            dataDict[value] =1
            except:
                pass
        for i in sorted(dataDict):
            print(f"{i}: {dataDict[i]}")


    def findDetail(self,detail:str,type:bool):
        """
            Searches through either passwords or usernames to see if there is a match, if there will print match found

            Args:
               -  details:string could be a password or username
               - type:bool `True` if you want to search through usernames. `False` if you want to search through passwords

            Return:
                bool: True if a match was found
        """
        pass




    def getIP(self)->str:
        """
          Returns:
            string: the ip address that has been logged
        """
        return self.clientIP
    def getTime(self)->str:
        """
          Returns:
            string: current time in d-m-Y H:M:S
        """
        return self.time
    
    def getLatestLog(self):
        """
            prints the details of the latest log
        """



#l = Logger()
#l.loginAttemptPerCountry()
#l.getMostUsed(True)
# l.logsPerCountry("Germany")
# l.usernamePasswordCombo()
# # #l.usernamePasswordCombo()
# l.mostCommonCountry()




  