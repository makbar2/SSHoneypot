from FileSystem import FileSystem
from Folder import Folder
from File import File 
from FileInterface import FileInterface
from Logger import Logger
import re

class Terminal():
    def __init__(self,seed=""):
        self.fileSystem = FileSystem(seed)
        self.__blank = False
        self.__blue = "\033[34m"
        self.__white = "\033[37m"
        self.__red = "\033[31m"
        self.__green = "\033[32m"
        self.__emtpyLine = "\n\r\n\r"
        self.__cursorPointer = 0
        self.__command = ""
        self.__filePointer = None#e.g. admin@ubuntu:~$
        fileNode = self.fileSystem.getWorkingDirectory()
        self.__updateFilePointer()
        self.__logger = None
        self.commandList = ["echo 3"]
        self.commandListPointer = 0
        self.commandPointer = 0
        self.beforeEnter = ""
        self.__endTrail = self.__filePointer


    def setLogger(self,logger:Logger):
        self.__logger = logger

    def handleInput(self,message,):
        #does the handeling of the keypresses
        #print(message)
        if(message==b"\x08" or message== b"\x7f"):#kali for somereason sends \x08 and win sends x7f no idea why--------------backspace
            #clear the line move cursor to start
            #redraw pointer
            #then text
            #adjust cursor
            if(self.__blank == True):#quickly implented as i forgot to do this 
                string = "[sudo] password for root: "
                return [b"\x1b[2K\r",string]
            else:
                screenOutput = self.__updateText(True)
                return [b"\x1b[2K\r",self.__filePointer,screenOutput]
        elif(message == b"\t"):#------------------------------------tab
            if(self.__command != ""):
                suggestion = self.autoCompleteSuggestion(self.__command)
                print(suggestion)
                if(suggestion != None):
                    text = self.autoComplete(self.__command,suggestion)
                    self.__command = text
                    return [b"\x1b[2K\r",self.__filePointer,text]
        elif(message == (b"\x1b[D")):#left arrow
            if(self.__updateCursorPointer("left")):
                return[message]
        elif(message == b""):#probs means that the user has closed the terminal
            return "quit"

        elif(message == b"\r"):#---------------------------------------------------------enter
            if(self.__blank == True):
                self.__blank =False
                self.__endTrail = self.__filePointer
                self.__command = ""
                return [f"\n\rsudo: 1 incorrect password attempt\n\r{self.__endTrail}"]
            else:
                self.__updateCursorPointer("reset")
                self.beforeEnter = None
                self.commandListPointer = 0#reset the position of the cusor
                return [self.processCommand(),self.__endTrail]
        elif(message == (b"\x1b[C")):#-------------------------------------------------right 
            if(self.__updateCursorPointer("right")):
                return[message]
        elif(message ==b"\x1b[A"):#------------------------------------------------------up
            if(self.beforeEnter == None):
                self.beforeEnter = ""+self.__command
            previousCommand = self.getCommandHistory(True)
            if(previousCommand != False):
                self.__command = previousCommand
                return [b"\x1b[2K\r",self.__filePointer,previousCommand]
        elif(message ==b"\x1b[B"):#-----------------------------------------------------down
            previousCommand = self.getCommandHistory(False)
            if(previousCommand != False):
                self.__command = previousCommand
                return [b"\x1b[2K\r",self.__filePointer,previousCommand]
            else:
                if(self.commandListPointer != 0):
                    print("before :"+self.beforeEnter)
                    self.__command = ""
                    self.commandListPointer = 0
                    return [b"\x1b[2K\r",self.__filePointer,self.beforeEnter]
                
        elif(message ==b'\x1b[B\x1b[B\x1b[B'):#----------------------------------------scroll downm, this is a gnome thing other terminals cant do it
            pass
        elif(message ==b'\x1b[A\x1b[A\x1b[A'):#-----------------------------------------scroll up 
            pass
        elif(message ==b'\x03'):
            pass
        else:
            if(self.__blank == True):#for sudo
                string = "[sudo] password for root: "
                return [b"\x1b[2K\r",string]
            else:
                if(self.__cursorPointer != 0):
                    screenOutput = self.__updateText(False,message.decode("utf-8"))
                    return [b"\x1b[2K\r",self.__filePointer,screenOutput]#clear screen, current working dir text output
                else:
                    return self.__updateText(False,message.decode("utf-8"))


    def __updateText(self,delete,char=None):
        """
            Backend:
                Modifies the current command string by deleting a character or adding a new character at the current cursor position.
                If `delete` is `True`, the character immediately to the left of the cursor is removed. If `char` is not `None`, the
                character is added at the current cursor position.

            FrontEnd:
                When a key is pressed the character should appear in the correct position on the line and the cursor will be moved to right to acomodate the new char
                when a character is deleted then the correct character will be removed on the screen adn the cursor will be moved to the left. 
            

            Returns the modified command string.

            Parameters:
            - delete (bool): `True` if the character to the left of the cursor should be deleted.
            - char (str): The character to be inserted at the current cursor position.

            Returns:
            - str: The modified command string.

        """
        if(self.__cursorPointer == 0):
            if(delete):
                self.__command = self.__command[:-1]
                return self.__command
            else:
                self.__command += char
                return char
        else:
            if(delete):
                #print(f"deleting and this is the curors val {self.__cursorPointer}, the length of string is {len(self.__command)} ")
                if(self.__cursorPointer != len(self.__command)):#when the cursor is behind the string dont do anything 
                    pointer = len(self.__command) - self.__cursorPointer - 1
                    self.__command = self.__command[:pointer] + self.__command[pointer+1:]
                else:
                    print("cant delete nothing")
                    pass
            else:#adding characters
                pointer = len(self.__command) - self.__cursorPointer
                lower = self.__command[:pointer]
                lowerLength = len(lower)
                self.__command = self.__command[:pointer] + char + self.__command[pointer:]

            return self.__command+f"\x1b[{self.__cursorPointer}D"
            #send the text and then tell the cursor to move left


    def __updateCursorPointer(self,direct: str):
        """
            Updates the position of the cursor on the client's terminal screen and returns whether the user cursor should still move
            based on the direction specified.
    
            Args:
                direct string: The direction you want to move the cursor. Can be "left" or "right". If anything else is passed in, 
                the cursor position is reset to 0.
                  
            Returns:
            bool: True if the user cursor should still move based on the string length, False otherwise.
        """
        #print(self.__command,len(self.__command))
        if(direct == "left"):
            
            if(len(self.__command) > self.__cursorPointer):    
                self.__cursorPointer += 1
                return True;
            else:
                return False
        elif(direct == "right"):
            if(self.__cursorPointer != 0):
                self.__cursorPointer -= 1    
                return True;
            else:
                return False
        else:
            self.__cursorPointer = 0
        print(self.__cursorPointer)    

    def __updateFilePointer(self):
        if(self.fileSystem.getWorkingDirectory().getName() == "root"):
            self.__filePointer = f"{self.__green}root@ubuntu-server:~${self.__white} "
            self.__endTrail = self.__filePointer#tech debt lol
        else:
            if(self.fileSystem.getWorkingDirectory().getName() == "/"):
                self.__filePointer = f"{self.__green}root@ubuntu-server:~{self.__blue}[{self.fileSystem.getWorkingDirectory().getName()}]{self.__white}$ "
            else:
                self.__filePointer = f"{self.__green}root@ubuntu-server:~/{self.__blue}{self.fileSystem.getWorkingDirectory().getName()}{self.__white}$ "
            self.__endTrail = self.__filePointer#stupid thing needed for sudo to work wtihout having to rebuild the entire program 


    #returns the node that 
    def getFilePointer(self):
        return self.__filePointer

    def getPreviousCommand(self):
        return self.commandList[-1]

    def processCommand(self):
        print(f"command entered: {self.__command}")
        self.__command = self.__command.strip()
        if(self.__command != ""):
            self.commandList.append(self.__command)       
            if(self.__logger != None):
                self.__logger.logCommand(self.__command)
            #take the first part of the command
            command = self.__command.split().pop(0)
            arguments = self.__command.replace(command, "").lstrip()#take the command leaving the arguments
            recordCommand = ""+self.__command#ik this is bad but its only for the autocomplete
            self.__command = ""
            match(command):
                case "grep":
                    return self.__commandGrep(arguments)
                case "touch":
                    return self.__commandTouch(arguments)
                case "mkdir":
                    return self.__commandMkdir(arguments)
                case "cat":
                    return self.__commandCat(arguments)
                case "ls":
                    return self.__commandLS(arguments)
                case "cd":
                    return self.__commandCD(arguments)
                case "rm":
                    return self.__commandRM(arguments)
                case "clear":
                    return b"\x1b[2J\x1b[H"
                case "echo":
                    return self.__commandEcho(arguments)
                case "pwd":
                    return self.__commandPWD(arguments)
                case "mv":
                    return self.__commandMV(arguments)
                case "quit":
                    return "quit"
                case "lscpu":
                    return self.outputTxt("lsCPU.txt")
                case "service":#ifrogot waht the commadn was called
                    return self.__commandService(arguments)
                case "whoami":
                    return self.__commandWho()
                case "ps":
                    return self.__comandPS(arguments)
                case "sudo":#will always be false
                    return self.__commandSudo()
                case "ifconfig":
                    return self.outputTxt("ifconfig.txt")
                case "ip":
                    return self.__commandIP(arguments)
                case __:
                    return f"\r\n {recordCommand}: command not found\r\n"    
        else:
            return "\r\n"

    def __commandService(self,argument):
        if(argument == "--status-all"):

            return self.outputTxt("service.txt")
        else:
            return "\r\nUsage: service < option > | --status-all | [ service_name [ command | --full-restart ] ]\r\n"

    def __commandIP(self, argument):
        if(argument == "addr"):
            return self.outputTxt("ipaddr.txt")
        elif(argument == ""):
            return self.outputTxt("helpIP.txt")

    def __commandPWD(self,argument):
        if(argument != ""):
            return f"\r\npwd: bad option:{argument} \r\n"
        else:
            return f"\r\n {self.fileSystem.getPath()}\r\n"

    def __comandPS(self,argument):
        #taken from a text file as its too much effort otherwise
        argument = argument.strip()#should really do this before hand
        if(argument == "-v"):
            string = "ps/psv.txt"
        elif(argument == "-f"):
            string = "ps/psf.txt"
        elif(argument == "-l"):
            string = "ps/psl.txt"
        elif(argument == "-s"):
            string = "ps/pss.txt"
        elif(argument == "-u"):
            string = "ps/psu.txt"
        elif(argument == ""):
            string = "ps/ps.txt"
        else:
            string = "ps/pserror.txt"#cba doing the rest 
        return self.outputTxt(string)

    def __commandLS(self,argument:str):
        string = ""
        if(argument == "--help"):
            return self.outputTxt("helpLs.txt")
        elif("-l" in argument):
            print("-l sent")
            #remove the -l do everything else
            argument = argument.replace("-l","")
            argument = argument.strip()
            children = self.fileSystem.listChildren(argument)
            if(children !=None):
                for i in children:
                    if(type(i) == Folder):
                        colour = self.__blue
                        string += f"\n\r{i.getLongFormat(colour)}"
                    else:
                        colour = self.__white
                        string += f"\n\r{i.getLongFormat(colour)}"
                return "\n\r"+string+"\n\r"
        else:
            children = self.fileSystem.listChildren(argument)
            if(children != None):
                for i in children:
                    if(type(i) == Folder):
                        string += f" {self.__blue}{i.getName()}{self.__white}"
                    else:
                        string += " "+i.getName()
                return "\n\r"+string+"\n\r"
            else:
                 return f"\n\r ls: cannot access '{argument}': no such file or directory\n\r"

    def __commandCat(self,command):
        output = self.fileSystem.outputContent(command)
        if(output == False):
            return f"\n\r cat: {command}: Is a directory\n\r"
        elif(output == None):
            return f"\n\r cat: {command}: No such file or directory\n\r"
        else:
            return f"\n\r {output}\n\r"
            #return [f"cat : {command}: No such file or directory"]
    
    def __commandEcho(self,argument):
        #echo the > file
        if(">"  in argument):
            textToEnter = argument.split(">")[0].rstrip()
            nodePath = argument.split(">")[1].lstrip()
            if(nodePath == None):#if nothing was placed after the >
                return ["zsh: parse error near `\\n' "]#thats what its like on kali
            else:
                success = self.fileSystem.addText(nodePath,textToEnter)
                if(success):
                    return "\n\r"#
                else:
                    return f"zsh: no such file or directory: {nodePath}\n\r"
        elif("<" in argument):            
            extToEnter = argument.split("<")[0].rstrip()
            nodePath = argument.split("<")[1].lstrip()
            success = self.fileSystem.findNodePath(nodePath)
            if(success):
               return f"\n\r{argument}\n\r"
            else:
                return f"zsh: no such file or directory: {nodePath}\n\r"
        else:
            return f"\n\r{argument}\n\r"

    def __commandWho(self,):
        return f"\n\rroot\n\r"

    def __commandRM(self,argument):
        if(argument == "--help"):
            return self.outputTxt("helpRm.txt")
        elif("-d" in argument):
            argument = argument.replace("-d","")
            argument = argument.strip()
            success =self.fileSystem.removeNode(argument,True)#t
            if(success == True):
                return self.__emtpyLine
            elif(success == "not empty"):
                return f"\n\r rm: cannot remove '{argument}': Directory is not empty\n\r"
        else:
            success = self.fileSystem.removeNode(argument,False)
            if(success == True):
                return self.__emtpyLine
            elif(success == "Folder"):
                return f"\n\r rm: cannot remove '{argument}': Is a directory\n\r"
            else:
                return f"\n\r rm: cannot remove '{argument}': No such file or directory\n\r"

    def __commandCD(self,path: str):
        path = path.strip()
        print("path: "+path )
        success = self.fileSystem.changeDirectory(path)
        if(success == True):
            self.__updateFilePointer()
            return "\n\r"
        elif(success == False):
            return f"\n\r cd: not a directory: {path}\n\r"
        else:
            if(path == ""):#bad code but cba doing a proper fix as its not needed really, im probs gonne regret this everytime ive had to redo the code later on. this is  "technical debt" lol
                print("path was empty")
                return self.__emtpyLine
            else:
                return f"\n\r cd: no such file or directory: {path}\n\r"

    def __commandMV(self,argument:str):
        name = ""
        argument = argument.split()
        location = argument[0]
        destination = argument[1]
        nodeToMove = self.fileSystem.findNodePath(location)
        if(nodeToMove == None):
            return f"\n\rmv: cannot move '{location}' to '{destination}' No such file or directory'\n\r"
        else:
            destinationNode = self.fileSystem.findNodePath(destination)
            if(location == None):
                return f"\n\rmv: cannot move '{location}' to '{destination}' No such file or directory'\n\r"
            elif(destinationNode == None):#maybe renaming the node
                destinationList = destination.split("/")
                name = destinationList[-1]
                destination = "/".join(destinationList[:-1])
                destinationNode = self.fileSystem.findNodePath(destination)
                if(destinationNode == None):
                    return f"\n\rmv: cannot move '{location}' to '{destination}' No such file or directory'\n\r"
                else:#poop repeated code
                    success = self.fileSystem.moveNode(nodeToMove,destinationNode,name)
                    if(success):
                        return "\n\r"
                    else:
                        raise ValueError("unable to move node, no idea why ")
            else:
                success = self.fileSystem.moveNode(nodeToMove,destinationNode,name)
                if(success):
                    return self.__emtpyLine
                else:

                    raise ValueError("unable to move node, no idea why ")

    def outputTxt(self,textFile:str):
        """
        Reads the contents of a text file located in the 'text' directory and appends each line to a list along with a
        return character '\\r'. The list is then returned with the __filePointer appended to the end.

        Args:
            textFile (str): A string representing the name of the text file to be read, including its extension.

        Returns:
            List[str]: A list of strings containing the contents of the specified text file with '\\r' appended to each line and
                the value of the private variable '__filePointer' appended to the end.

        Raises:
            FileNotFoundError: If the specified text file cannot be found in the 'text' directory.
        """
        l = ["\r\n"]
        with open(f"text/{textFile}") as text:
            for i in enumerate(text):
                l.append(i[1] + "\r")
        text.close()
        return l
    
    def __commandMkdir(self,command):
        if(command == ""):
            return "\n\rmkdir: missing operand\n\r Try 'mkdir --help' for more information.\n\r"
        elif(command == "--help"):
            return self.outputTxt("helpMkdir.txt")
        else:
            try:
                success = self.fileSystem.createNode(command,True)

                if(success):
                    return "\n\r"
                else:
                    return f"\n\rmkdir: cannot create directory '{command}': No such file or directory\n\r"
            except:
                return f"\n\rmkdir: cannot create directory '{command}': File exists\n\r"

    def __commandGrep(self,argument):
        if('"' in argument):
            argumentList = argument.split('" ', 1)
            filePath = argument.split('" ', 1)[1]
            text = argument.strip('"').split('"')[0]
        elif(argument == ''):
            return "\n\r Usage: grep [OPTION]... PATTERNS [FILE]...\n\r Try 'grep --help' for more information.\n\r"
        elif(argument == "--help"):
            return self.outputTxt("helpGrep.txt")
        else:
            argumentList = argument.split()
            filePath = argumentList[1]
            text = argumentList[0]
        content = self.fileSystem.outputContent(filePath)
        if(content == False):
             return f"grep: {filePath}: Is a directory"
        elif(content == None):
            return f"grep: {filePath}: No such file or directory"
        else:
        #seperate text from path
            matchPattern = re.search(text,content)
            if(matchPattern):#return but the found text is highlighted
                content = content.replace(text,self.__red+text+self.__white)
                return f"\n\r{content}\n\r"
            else:
                return "\n\r"

    def __commandTouch(self,command):
        if(command == ""):
            return self.outputTxt("helpTouch.txt")
        commandList = command.split()
        success = self.fileSystem.createNodeTouch(commandList[0],commandList[1])

        if(success):
            return "\n\r"
        else:#assume that they might be trying to create the file in another directory 
           
           return f"\n\rtouch: cannot touch '{command}': No such file or directory'\n\r"

    def setCommand(self,command):
        self.__command = command

    def getCommandHistory(self,direct:bool):
        """
        gets the previous command
        
        Parameters:
            - direct (bool): `True` if up arrow has been pressed. `False` if the down arrow has been pressed.
        """
        try:
            if(direct == True):
                self.commandListPointer -= 1
            else:
                if(self.commandListPointer < -1):
                    self.commandListPointer +=1
                else:
                    return False 
            print(self.commandList)
            print(self.commandListPointer)
            return self.commandList[self.commandListPointer]
            
        except:
            return False

    def autoCompleteSuggestion(self,text)->str:
        """
        Very basic implemtation of autocomplete, to get the job done. Trying to make the real thing will take up too much time to do.
        
        Args:
            text string: user text from terminal
        
        Returns:
            string : a match 
        """
        #text can either come as 
        #<text>
        #<command> <text>
        #<command> <filepath>
        #need to get the stuff out 
        textList = text.split()
        if(len(textList) ==  2):#command and text
            text = text.replace(textList[0],"")
            text = text.strip()
            if("/" in text):
                path = text.split("/")#
                name = path.pop()
                path = "/".join(path)
                #dwakdawd/gfsdpokg/daw]
                #/grdg[dr]/grdg/grd
                if(text.startswith("/")):
                    path = "/" + path
                names = self.fileSystem.findNodePath(path).getChildrenNames()
                text = "" +name
            else:
                names = self.fileSystem.getWorkingDirectory().getChildrenNames()
        elif(len(textList) ==  3):
            text = text.replace(textList[0],"")#get rid of the command
            text = text.replace(textList[1],"")#get rid of the first stuff, so that it gets the suggestion for the second part
            text = text.strip()
            #this bad repeated code but cba
            if("/" in text):
                path = text.split("/")#
                name = path.pop()
                path = "/".join(path)
                #dwakdawd/gfsdpokg/daw]
                #/grdg[dr]/grdg/grd
                if(text.startswith("/")):
                    path = "/" + path
                names = self.fileSystem.findNodePath(path).getChildrenNames()
                text = "" +name
            else:
                names = self.fileSystem.getWorkingDirectory().getChildrenNames()
        else:
            names =  self.fileSystem.getWorkingDirectory().getChildrenNames()
        matches = []
        for i in names:
            if i.startswith(text):
                matches.append(i)
        if(matches):
            return matches[0]
        else:
            return None

    def autoComplete(self,text,suggestion)->str:
        textList = text.split()
        if(len(textList) == 1):
            argument = textList[0]
            pathList = argument.split("/")
            #lastPath = pathList[-1]
            pathList[-1] = suggestion
            newPath = "/".join(pathList)
            return f"{newPath}"
        elif(len(textList) == 2):
            argument = textList[1]
            pathList = argument.split("/")
            #lastPath = pathList[-1]
            pathList[-1] = suggestion
            newPath = "/".join(pathList)
            return f"{textList[0]} {newPath}"
        elif(len(textList) == 3):
            argument = textList[2]
            pathList = argument.split("/")
            #lastPath = pathList[-1]
            pathList[-1] = suggestion
            newPath = "/".join(pathList)
            return f"{textList[0]} {textList[1]} {newPath}"
        
    def __commandSudo(self):
        #disable text feed back
        self.__blank = True
        self.__endTrail = ""
        return f"\n\r[sudo] password for root: "

            



t = Terminal()

def test(command:str,):
    print(f"testting command: {command}")
    t.setCommand(command)
    print(t.processCommand())



#mdkir testing
# test("ls")
# test("mkdir Desktop/theFolder")
# test("mkdir Desktop/par")
# test("ls Desktop")
# test("mv Desktop/theFolder Desktop/par")
# test("ls Desktop")
# test("ls Desktop/par")
#grep testing 
# test("echo cooler dudes > Desktop/the.txt")
# test("ls")
# test("cat Desktop/the.txt")
# test('grep "cool" Desktop/the.txt')
# test("grep")
#test("grep --help")

# ls Testing
# test("ls")
# test("ls -l")
# #test("ls Desktop/Zaam-Dox")
# #test("ls ../admin")
# test("ls ../admin/g0idrg")
# test("ls --help")

# #rm testing 
# test("touch f")
# test("ls")
# test("rm f")
# test("ls")
# test("rm Pictures")

#previous command testing
# test("echo 3")
# test("ls")
# test("touch f")
# test("cat f")
# print(t.getCommandHistory(True)+ f" pointer: {t.commandListPointer}")#cat f 
# print(t.getCommandHistory(True)+ f" pointer: {t.commandListPointer}")#toch f
# print(t.getCommandHistory(True)+ f" pointer: {t.commandListPointer}")#ls
# print(t.getCommandHistory(True)+ f" pointer: {t.commandListPointer}")#echo 3

# print("down")
# print(t.getCommandHistory(False)+ f" pointer: {t.commandListPointer}")#ls
# print(t.getCommandHistory(False)+ f" pointer: {t.commandListPointer}")#touch f
# print(t.getCommandHistory(False)+ f" pointer: {t.commandListPointer}")#cat f

# #print(t.getCommandHistory(False)+ f" pointer: {t.commandListPointer}")
#print(t.getCommandHistory(False)+ f" pointer: {t.commandListPointer}")

#testing echo 


#testing rm
# test("touch f")
# test("mkdir yep")
# test("ls")
# # test("rm f")
# # test("ls")
# test("rm -d yep")
# test("ls")
# test("rm -d Downloads")



#test auto 
# test("ls")
# test("cd Desktop")
# test("ls")
# test("cd ..")

# test("ls")
# test("cd Desktop")
# test("touch pooy")
# test("mkdir coolFolder")
# test("mkdir cool")
# test("ls")
# test("mv cool coolFolder/")
# x = t.fileSystem.getWorkingDirectory()
# print("ss")
# test("ls coolFolder")


# test("ls")
# test("mkdir f")
# test("echo waaa > l")
# test("ls")
# test('grep "wa" l')
# test('grep "was" f')


# test("mkdir loop")
# test("mv loopdwad Desktop/fart")
# test("ls Desktop")
# test("cd ../../etc")
# test("cd ..")
# test("pwd")
# test("ls")
# test("touch f root/Desktop")




