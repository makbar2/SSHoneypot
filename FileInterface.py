import random
import datetime
class FileInterface():
    def __init__(self,name,size=1024,parent=None,):
        self.name = name
        self.size = size
        self.parent = parent


    
    def getName(self) -> str:
        return self.name
    


    def setName(self,name) ->str:
        self.name = name
        return self.name
    
    def setParent(self,parent):
        self.parent = parent

    def getParent(self):
        return self.parent
    
    def getSize(self):
        pass

    def getRandomAccessTime(self):
        #just randomly generate a date time for the long format 
        now = datetime.datetime.now()
        start = now - datetime.timedelta(days=365)
        randomDate = start + (now - start) * random.random()
        formattedDate = randomDate.strftime("%b %d %H:%M")
        return formattedDate 



    def longListing(self):
        pass


