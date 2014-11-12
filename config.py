class Config:
    def __init__(self):
        pass

    LOGGING_NAME = "GoombungeeShowServer"

    #The amount each person can control the robot for
    CONTROL_TIME = 60

    #The TCP bridge connects the serial port associated with the hexapod with a network socket
    TCP_BRIDGE_HOST = "25.14.67.122"
    TCP_BRIDGE_PORT = 1997