from FileInterface import *
class File(FileInterface):
    #files should be able to display multi lines so \n needs to be added if you want a new line
    def __init__(self, name,size=1024, contents="",parent=None,):
        self.__contents = contents;
        super().__init__(name, size, parent)
        self.__hardlinks = 1 

    def getContents(self,)->str:
        return self.__contents
    
    def setContents(self,text):
        self.__contents = text

    def setContentFromFile(self,fileName):
        l = ""
        with open(f"text/{fileName}") as text:
            for i in enumerate(text):
                l += (i[1] + "\r")
        self.__contents = l

    def getSize(self):
        return self.size

    def getLongFormat(self,colour:str)->str:
        #random date too 
        #returns longformat this is random as it not really needed tbh 
        return f"drwxr-xr-x {self.__hardlinks} root root {self.getSize()} {self.getRandomAccessTime()} {colour}{self.getName()} \033[37m" 
        
