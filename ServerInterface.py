import paramiko
from Logger import Logger
class ServerInterface(paramiko.ServerInterface):
    #cant just implement the interaface into SshServer due to the fact that you need to pass in an object with the overwrides when doing paramiko.Transport.startServer
    #
    def __init__(self,logger) -> None:
        super().__init__()
        self.__logger = logger
        #-----OVERRIDES-----------------
    def check_channel_request(self, kind: str, chanid: int) -> int:
        if(kind == "session"):
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def check_auth_password(self, username, password):
        #log the attempted passwords and usernames 
        self.__logger.addAttempt(username,password)
        if (username == 'root') and (password == 'password'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED
    
    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True


    def check_channel_shell_request(self, channel):
        return True
    
    def get_banner(self):
        print("sending banner")
        return ('',"en-UK")
        #return ('SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.3\n',"en-UK")
        #return ('SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.3\n',"en-UK")

    