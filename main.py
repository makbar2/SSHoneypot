import sys
from SshServer import SshServer#for somereason i have to specifiy the class 
from Logger import Logger
from FileSystem import FileSystem
from Folder import *
from File import *
from Logger import * 


"""
    Before you're able to start up this honeypot you need to create an RSA key,
    run ssh-keygen -t rsa -b 2048 -m PEM -f ~/.ssh/id_rsa in cmd to get the proper key, it only accepts rsa, not any of  the newer standards
    make sure you configure the ip address correctly too
"""




def start():
    with open("config.json","r") as file:
        data = json.load(file)
    file.close()
    port = data["port"]
    ip = data["ipAddress"]
    key = data["keyLocation"]
    s = SshServer(ip,port,key)
    s.start()


def config():
    print("Select an option to modify")
    print("1. RSA Key")
    print("2. ip address")
    print("3. port")
    option = int(input(": "))
    match(option):
        case 1:
            option = "keyLocation"
            value = input("Please enter new key path: ")
        case 2:
            option = "ipAddress"
            value = input("Please enter ip address: ")
        case 3:
            option = "port"
            value = int(input("Please enter port: "))
        case _:
            raise ValueError("invalid option selected")
    with open("config.json","r") as file:
        data = json.load(file)
    file.close()
    data[option] = value
    with open("config.json","w") as file:
        json.dump(data,file)
    file.close()
    options()#this is probs bad but idc


def options():
    l = Logger()
    print("Please select an option")#why cvant you make multi line strings this is annoying 
    print("1. start honeypot")
    print("2. view country statistics")
    print("3. view username and password combonation statistics")
    print("4. view password statistics")
    print("5. view username statistics")
    print("6. view latest log")
    print("7. configure")
    option =  int(input(": "))
    match(option):
        case 1:
            start()
        case 2:
            l.mostCommonCountry()
        case 3:
            l.usernamePasswordCombo()
        case 4:
            l.getMostUsed(True)
        case 5:
            l.getMostUsed(False)
        case 6:
            l.getLatestLog()
        case 7:
            config()
        case _:
           raise ValueError("invalid option selected")

# def main(args):
#     print(args)
#     if(args[1] == "-o"):
#         options()
#     else:
#       start()


if __name__ == "__main__":
    #start()
    options()
    #main(sys.argv) turn this off for testing purposes

    
    # s = SshServer("192.168.0.10",22,"C:/Users/moham/.ssh/id_rsa")
    # s.start()
    #main(sys.argv)

    #ssh root@192.168.0.10
    #ip for laptop is :192.168.0.32
    #82.29.108.166
