from Folder import Folder
from File import File
from FileInterface import FileInterface
import re
import random
import json
import os


class FileSystem():
    #need to emulate fs of a linux machine
    def __init__(self,seed="bruh") -> None:
        #i hate myself
        self.root = Folder(
            "/",
            [
                Folder("bin",[]),
                Folder("boot",[
                    Folder("grub",[
                        Folder("fonts",[]),
                        Folder("i386-pc",[]),
                        Folder("locale",[]),
                        Folder("themes",[])
                    ]),
                    File("config-6.1.0,ubuntu-amd64"),
                    File("initrd.img-6.1.0-ubuntu-amd64"),
                    File("System.map-6.1.0-ubuntu-amd64")
                ]),
                Folder("dev",[]),
                Folder("etc",[
                    File("passwrd",4090),
                    Folder("alsa",[]),
                    Folder("alternatives",[]),
                    Folder("appache2,",[]),
                    Folder("apparmor",[]),
                    Folder("apparmor.d",[]),
                    Folder("apt",[]),
                    Folder("arp-scan",[]),
                    Folder("avahi",[]),
                    Folder("ssh",[
                        Folder("ssh_config.d",[]),
                        Folder("sshd_config.d",[]),
                        File("moduli"),
                        File("ssh_config"),
                        File("sshd_config"),
                        File("ssh_host_ecdsa_key"),
                        File("ssh_host_ecdsa_key.pub"),
                        File("ssh_host_ed25519_key"),
                        File("ssh_host_rsa_key"),
                        File("ssh_host_rsa_key.pub"),
                    ]),
                    Folder("zsh",[
                        File("newuser.zshrc.recommended"),
                        File("newuser.zshrc.recommended.original"),
                        File("zlogin"),
                        File("zlogout"),
                        File("zprofile"),
                        File("zlogout"),
                        File("zprofile.original"),
                        File("zshenv"),
                        File("zshrc"),
                    ]),
                    File("shadow")
                ]),
                Folder("home",
                    [
                        Folder("root",
                            [
                                Folder("Desktop",[]),
                                Folder("Documents",[]),
                                Folder("Downloads",[]),
                                Folder("Music",[]),
                                Folder("Pictures",[]),
                                
                            ]
                        ),
                    ]
                ),
                Folder("lib",[]),
                Folder("lib32",[]),
                Folder("lib64",[]),
                Folder("libx32",[]),
                Folder("media",[]),
                Folder("mnt",[]),
                Folder("opt",[]),
                Folder("proc",[]),
                Folder("root",[]),
                Folder("run",[]),
                Folder("sbin",[]),
                Folder("srv",[]),
                Folder("sys",[]),
                Folder("tmp",[]),
                Folder("bin",[]),
                Folder("var",[]),
                Folder("bin",[]),
                Folder("usr",[]),
            ]
        )
        self.__rootNode = None
        self.__currentNodePointer = self.__searchTree(self.root, "root")#poitns the node that the user is currently on
        self.__homeNode = self.__searchTree(self.root,"home")
        self.jsonData = self.getJsonData()
        password = self.__searchTree(self.root,"passwrd")
        sshConfig = self.__searchTree(self.root,"ssh_config")
        shadow = self.__searchTree(self.root,"shadow")
        shadow.setContentFromFile("etc/shadow.txt")
        sshConfig.setContentFromFile("sshconfig.txt")
        password.setContentFromFile("etc/password.txt")
        if(seed):#i only have a seed because it was one of my requirments, this inst really nessary
            random.seed(seed)
        self.fileGenerator()

    
    


    def fileGenerator(self):
        #seed will be based off the ip address and time 
        
        #create a random directory of folders to be appended in 
        adminNode = self.__searchTree(self.root,"root")
        desktop = self.__findChild("Desktop",adminNode.getChildren())
        document = self.__findChild("Documents",adminNode.getChildren())
        downloads = self.__findChild("Downloads",adminNode.getChildren())
        pictures = self.__findChild("Pictures",adminNode.getChildren())
        self.generateFolderContents(desktop,2,5)
        self.generateFolderContents(downloads,2,5)
        self.generateFolderContents(pictures,1,3)
        self.generateFolderContents(document,3,10)
    
         

    def generateFolderContents(self,baseFolder, maxDepth, maxItems):
        """
        Generate a random folder structure with files and subfolders.

        Args:
            baseFolder (Folder): The starting point for generating the folder structure.
            maxDepth (int): The maximum depth of the folder structure.
            maxItems (int): The maximum number of items allowed at each level of the structure.
        """
        if(maxDepth == 0):
            return
        amount = random.randint(1,maxItems)#random amount of items on each level 
        #print(f"picked{amount}")
        for i in range(amount):
            itemType = random.choice([Folder, File])            
            if(itemType == File):
                itemName = random.choice(self.jsonData["file"])["filename"]
                itemSize = random.randint(1024, 9000)
                text = self.generateFileContents()
                item = File(itemName, itemSize, text)
            else:
                itemName = random.choice(self.jsonData["folder"])["foldernames"]
                item = Folder(itemName, [])
                self.generateFolderContents(item, maxDepth - 1, maxItems)
                #recursively call itself to create more items in each folder. 
            
            baseFolder.addChild(item)
        


    def generateFileContents(self,)->str:
        number = random.randint(2,20)
        contents = ""
        for i in range(number):
            jsonDictItem = random.choice(list(self.jsonData.keys()))
            innerJsonList = self.jsonData[jsonDictItem]#idk waht to call this var
            item = random.choice(innerJsonList)
            itemKeys = list(item.keys())
            string = item[itemKeys[0]]
            contents += f"{string}\r"
        return contents



    def getJsonData(self)->dict:
        with open("random/filenames.json") as file:
            filenames = json.load(file)
        file.close()
        with open("random/foldernames.json") as file:
            folderNames = json.load(file)
        file.close()
        with open("random/passwords.json") as file:
            passwords = json.load(file)
        file.close()
        with open("random/usernames.json") as file:
            usernames = json.load(file)
        file.close()
        with open("random/words.json") as file:
            words = json.load(file)
        file.close()
        return {
            "file" :filenames,
            "folder":folderNames,
            "password": passwords,
            "usernames":usernames,
            "words":words,
        }
            
    def __searchTree(self,startNode, targetName: str, visitedNodes=None):
        """
        Recursively searches the file system tree to find a file or directory with the specified name.

        Args:
            startNode (FileInterface): The starting point of the search. A FileInterface object representing a directory in the file system.
            targetName (str): The name of the file or directory to search for.
            visitedNodes (Optional[Set[FileInterface]]): A set containing the FileInterface objects that have already been visited. Defaults to None.

        Returns:
            Optional[FileInterface]: A FileInterface object representing the file or directory with the specified name if it is found, otherwise returns None.

        Raises:
        """
        if(visitedNodes is None):
            visitedNodes = set()#so that there are no duplicate objects 
        visitedNodes.add(startNode)
        if(startNode.name == targetName):
            return startNode
        if(type(startNode) != File):
            for i in startNode.children:
                if(i not in visitedNodes):
                    result = self.__searchTree(i, targetName, visitedNodes)
                    if(result is not None):
                        return result
            if(startNode.parent is not None and startNode.parent not in visitedNodes):
                result = self.__searchTree(startNode.parent, targetName, visitedNodes)
                if (result is not None):
                    return result
            return None
        else:
            return None
    

    def __searchTreePath(self, startNode, targetNode:FileInterface, visitedNodes=None, path=None):
        """
        Searches a tree to find a specific node and returns the path taken to reach that node.

        Args:
            startNode: The node to start the search from.
            targetNode (FileInterface): The node to search for.
            visitedNodes (set, optional): A set of nodes that have already been visited during the search.
                Defaults to None.
            path (list, optional): A list of nodes that have been visited on the path to the target node.
                Defaults to None.

        Returns:
            tuple: A tuple of two elements:
            [0] If the target node is found, it returns the target node object and a list of nodes that have been visited on the path to the target node.
                [1] If the target node is not found, it returns None and a list of nodes that have been visited during the search.
        """
        if(visitedNodes is None):
            visitedNodes = set()  # so that there are no duplicate objects
        if(path is None):
            path = []  # to keep track of the path taken to find the target node
        visitedNodes.add(startNode)
        path.append(startNode)
        if(startNode == targetNode):
            return startNode, path
        if(type(startNode) != File):
            for i in startNode.children:
                if(i not in visitedNodes):
                    result, p = self.__searchTreePath(i, targetNode, visitedNodes, path)
                    if(result is not None):
                        return result, p
            if(startNode.parent is not None and startNode.parent not in visitedNodes):
                result, p = self.__searchTreePath(startNode.parent, targetNode, visitedNodes, path)
                if (result is not None):
                    return result, p
            path.pop()  # remove current node from path as we backtrack, i completetly forgot about this in my diseration that the fact that it might not be able to find the node
            return None, path
        else:
            path.pop()  
            return None, path



    def getWorkingDirectory(self,):
        return self.__currentNodePointer




    def setPointer(self,place):
        self.__currentNodePointer = self.__searchTree(self.__currentNodePointer,place.getName())
        return self.__currentNodePointer
        
    def __pathToList(self,path):
        #if the path begins with with / start from root 
        path = path.split("/")
        return list(filter(None,path))
        


    def getPointerChildren(self):
        return self.__currentNodePointer.getChildren()
    

    def __findChild(self,name:str,list:list):
        found = None
        for i in list:
            if(i.getName() == name):
                found = i
                break
            else:
                found = False
        return found

    def createNode(self,path,isFolder:bool):
        name = path.split("/").pop()
        #remove name from path 
        path = path.replace(name,"")
        if(path == ""):
            pointer = self.__currentNodePointer
        else:
            pointer = self.__followPath(path)
        #if the path is nothing then just current working dir
        if(pointer == None ):
            return False
        else:
            if(type(pointer) == Folder):
                if(isFolder):
                    #check if a folder witht he same name already existss
                    result = self.__findChild(name,pointer.getChildren())
                    if(result != False):
                        raise ValueError("folder exits")
                    else:
                        newFolder = Folder(name,[])#for somereason the folder was getting children wtf so i have to specifiy it as empty but in the constructor it should be empty 
                        #wtf this makes no sense liek waht the fuk
                       
                        pointer.addChild(newFolder)
                else:
                    pointer.addChild(File(name,0))
                result = self.__findChild(name,pointer.getChildren())
                return result
            elif(type(pointer) == File):
                return False

    def createNodeTouch(self,name:str,path):
        #dont have time to combine the funcitonality with createNode, an error with touch was found i had to quickly fix it
        if(path == ""):
            pointer = self.__currentNodePointer
        else:
            pointer = self.__followPath(path)
            if(pointer == None):
                return False
        file = File(name)
        return True
        




 
    def listChildren(self,path=None)-> list:
        """
        Returns a list of the children of the folder specified by the path.

        Args:
            path (str, optional): The path of the folder to retrieve the children of.
               If no path is specified, it returns the children of the current folder.
                Defaults to None.

        Returns:
            list: A list of children of the folder specified by the path, or None if
            the specified path does not exist.
        """
        if(path == ""):#list current directory
            return self.__currentNodePointer.getChildren()
        else:         
            foundNode = self.__followPath(path)
            if(foundNode):
                if(type(foundNode) == Folder):
                    return foundNode.getChildren()
                else:
                    return [foundNode]
            else:
                return None 

    def __followPath(self, path:str)-> FileInterface:
        """
        follows the path given and returns the file node if its able to find it

        Args :
            path string: the file path 
        
        Returns: 
            None or FileNode
        """
        #follows path e.g. Desktop/the.txt 
        #returns the last node in the path which in the example will be the.txt
        if(path == ""):
            return None
        root = False
        if(path.startswith("/")):
            root = True
        path = self.__pathToList(path)
        childFound = None
        if(path == ""):
            return None
        try:
            lastItem = path[-1]
        except:
            lastItem = None
        if(root == True):#starting from root
            currentNode = self.root
        else:
            currentNode = self.__currentNodePointer
        for i in path:
            childFound = False
            if(".." == i):
                currentNode = currentNode.getParent()
                childFound = True
            else:
                if(currentNode.getName() != i):
                    children = currentNode.getChildren()
                    for child in children:
                        if(child.getName() == i):
                            currentNode = child
                            childFound = True
                            break
                        else:#what happnes if it cant find it 
                            childFound = False
                    if(childFound == False):
                        break
        if(currentNode != self.__currentNodePointer):
            if(childFound == False):
                return None
            else:
              return currentNode  
        else:
            if(lastItem == "admin"):
                return currentNode
            else:
                return None


    def outputContent(self,path: str):
        """
        Returns the content of the file located at the specified path.

        Args:
            path (str): The path of the file to retrieve the content from.

        Returns:
            False if the pointer wanst a file 
            File object 
        """
        #lastItem = path.pop()
        pointer = self.__followPath(path)
        if(type(pointer) == File):
            return pointer.getContents()
        elif(pointer == None):
            return None
        else:
            return False
    
 
            
    def removeNode(self,path:str,deleteFolder:bool):
        """
        removes a file or folder if the folder is empty

        Args :
            - path string: the file path 
            - deleteFolder bool: `True` if you want to delete the folder or file, `False` if you want to delete file only
        
        Returns:
            Bool or None: None if file doesn't exist, false if its a dir, true if able to delte the file
        """
        pointer = self.__followPath(path)
        if(pointer == None):
            return None
        else:
            parent = pointer.getParent()
            if(deleteFolder == False):
                parent = pointer.getParent()
                if(type(pointer) == Folder):
                    return "Folder"
                else:
                    parent.getChildren().remove(pointer)
                    return True 
            else:#check if it got children 
                if(type(pointer) == Folder):
                    if(len(pointer.getChildren()) > 0):
                        return "not empty"
                parent.getChildren().remove(pointer)
                return True 


    def changeDirectory(self,path:str):
        """
        changes the filesystem current node pointer to the place specified in the path 

        Args :
            path string: the file path 
        
        Returns:
            Bool or None: true if able to change pointer, false pointer is a file so cant change the pointer, None if unable to find the node.
        """
        pointer = self.__followPath(path)
        if(type(pointer) == Folder):
            self.__currentNodePointer = pointer
            return True
        elif(pointer == None):
            print("cannot find")
            return None
        else:
           print("not a folder")
           return False



    def moveNode(self,nodeToMove:FileInterface,destinationNode:FileInterface,newName=""):
        #nodes need have been foudn before hand as it simplifies it
        if(newName != ""):
            print("new name: "+newName)
            nodeToMove.setName(newName)
        if(type(nodeToMove) == Folder and type(destinationNode) == File):
            print("mv: cannot overwrite non-directory 'the.txt' with directory 'Music'")
            return False
        elif(type(nodeToMove) == Folder and type(destinationNode) == Folder):
            parent = nodeToMove.getParent()
            parent.removeChild(nodeToMove)
            print(f"moved {nodeToMove.getName()} folder in folder {destinationNode.getName()}")
            destinationNode.addChild(nodeToMove)
        elif(type(nodeToMove) == File and type(destinationNode) == File):
            parent = destinationNode.getParent()
            parent.removeChild(destinationNode)
            parent.addChild(nodeToMove)
            print("overwrite file")
        else:#file into dir
            if(nodeToMove == None):
                return False
            else:
                parent = nodeToMove.getParent()
                parent.removeChild(nodeToMove)#need to do this, took 20 years to figure out
                print("file into folder")
                destinationNode.addChild(nodeToMove)
        return True
            
        




    def renameNode(self,path:str,name:str):
        pointer = self.__followPath(path)
        if(pointer == None):
            return False
        else:
            pointer.setName(str)
            return True
        


    def getPath(self):
        """
        Returns the path of the current node pointer.

        Returns:
            str: The path of the current node pointer. So its formated like the pwd command: /home/admin

        """
        #for pwd so when the user does pwd should be /home/admin
        if(self.lookForHome == True):
            start = self.__homeNode
        else:
            start = self.root
        x = self.__searchTreePath(start,self.__currentNodePointer)
        print(x[0].getName())
        #x[1].pop(0)
        string = "/"
        try:
            last = x[1].pop()
            for i in x[1]:
                string = string + i.getName() + "/"
            result =  string + last.getName()
            result = result[2:]#cba doing a proper fix
            return result
        except:#lol
            return "/"
        

    def lookForHome(self,node):
        found = False
        currentNode = self.__currentNodePointer
        while(found == False):
            if(currentNode.getParent() == self.__homeNode):
                found == True
                break
            else:
                currentNode = currentNode.getParent()
                if(currentNode == None):
                    break
        return found


    def addText(self,path:str,text=""):
        """
        this function emulates the echo functionality kind of it looks for the node and checks if it exists, if it doesnt then it will create the node
        if the node exists but its a folder then false will be returned
        if it exits and is able to set the text then it returns true

        Args: 
            path string: file path 
            text string: the text you want to add 

        Returns:
            Bool or none: true if able to set text, false if node is not a file, None = error
        """
        pointer = self.__followPath(path)
        if(type(pointer) == File):
            pointer.setContents(text)
            return True
        elif(type(pointer) == Folder):
            return False
        else:
            #if the pointer wasn't found then create the file and set the contents
            #pop last node

            node = self.createNode(path,False)
            if(node):
                node.setContents(text)
                print (node.getName())
                return True
            else:
                return None

    def findNodePath(self, path:str):
        return self.__followPath(path)


##############################################
# def output(list):
#     for i in list:
#         print(i.getName())
# f = FileSystem()
# print(f.createNode("bruh",File).getName())
# print(f.createNode("Desktsp/yum.txt",File).getName())
# f = FileSystem()
# f.fileGenerator()
#print(random.choice(x["folder"])["foldernames"])
#f.fileGenerator("92.40.180.128","11-04-2023 16:40:16")

# f = FileSystem()
# print(f.root.getSize())
