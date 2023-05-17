from FileInterface import *
class Folder(FileInterface):
    def __init__(self,name,children,size=1024,parent=None):
        FileInterface.__init__(self,name,size,parent)
        if(children != None):
            self.children = children
            for i in children:
                i.setParent(self)
        self.size = self.getSize()
        self.__hardlinks = self.countChildren() + 1


    def addChild(self, child):
        child.setParent(self)
        self.children.append(child)
        self.__hardlinks += 1

    def addChildren(self, children):
        #for somereason it wouldnt let me do this in the constructor no idea why
        for i in children:
            self.children.append(i)
        self.__hardlinks = self.countChildren()
    
    def removeChild(self,child):
        self.children.remove(child)
    
    def getChildren(self):
        return self.children
    
    def getChildrenNames(self): #this should have been used everywhere but cba changing the code now
        names = []
        for i in self.children:
            names.append(i.getName())
        return names


    def getSize(self):
        x = 1024 
        for i in self.children:
            x += i.getSize()
        return x

    def countChildren(self):
        return len(self.children)
    
    def getHardLinks(self):
        #update it just incase
        return self.countChildren() + 1#parent counts as a link
    
    def getLongFormat(self,colour:str)->str:
        """
        displays the long format 

        Params:
            colour: `string` must a be an escape code or it wont work 
        
        Returns:
            string: the long format
        """
        self.__hardlinks = self.getHardLinks()
        return f"drwxr-xr-x {self.getHardLinks()} root root {self.getSize()} {self.getRandomAccessTime()} {colour}{self.getName()} \033[37m" 