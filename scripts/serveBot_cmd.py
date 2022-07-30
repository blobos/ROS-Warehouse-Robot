#! /usr/bin/env python3

import rospy
from std_msgs.msg import Bool, String, Int32

start_ = True

goal = ''
cmd = ''
submenu_ = False
def sendGoal(ABCD):
    if goal == 'a':
        print("publish toA")
        pub.publish("toA")
    if goal == 'b':
        print("publish toB")
        pub.publish("toB")
    if goal == 'c':
        print("publish toC")
        pub.publish("toC")
    if goal == '':
        print("publish toD")
        pub.publish("toD")

""" def goal_confirm(ABCD):
    global goal
    global submenu_
    goal = ABCD.upper()
    cmd_confirm = input("\ Enter 'Y' to send robot to ", goal, ": ")
    if cmd_confirm == 'y':
        print("confirmation sent")
        print("sending bot to ", goal)
        sendGoal(goal)
    submenu_ = False  """

def menu(msg):
    global start_
    global goal
    global cmd
    global submenu_
    # while not rospy.is_shutdown():
    
#confirmation
    if submenu_:
        if msg.data == "confirm_A":
            cmd_confirm = input("\n Enter 'Y' to send robot to A:").lower()
            goal = 'a'
            if cmd_confirm == 'y':
                sendGoal(goal)    
            submenu_ = False    
            
        elif msg.data == "confirm_B" :
            cmd_confirm = input("\n Enter 'Y' to send robot to B:")
            goal = 'b'
            if cmd_confirm == 'y':
                print("confirmation sent")
                print("sending bot to ", goal)
                sendGoal(goal)
            submenu_ = False    

        elif msg.data == "confirm_C":
            cmd_confirm = input("\n Enter 'Y' to send robot to C:")
            goal = 'b'
            if cmd_confirm == 'y':
                print("confirmation sent")
                print("sending bot to ", goal)
                sendGoal(goal)                 
            submenu_ = False    

        elif msg.data == "confirm_D":
            cmd_confirm = input("\n Enter 'Y' to send robot to D:")
            goal = 'd'
            if cmd_confirm == 'y':
                print("confirmation sent")
                print("sending bot to ", goal)
                sendGoal(goal)  
            submenu_ = False   

        # elif msg.data == 'state_feedback':
        #     print("state_fb_received")
        #     print(msg.data)
        #     submenu_ = False
    

    if msg.data == ("At_kitchen" or "At_charger" or "In_customer_delivery"):
        print(msg.data)
        
    print("last cmd bot received: ", msg.data)

    
    cmd = input("\nEnter one of the following commands:\n \
'A', 'B', 'C', or 'D' to order to respective table\n \
'Cancel' to cancel current order and return to station\n \
'Change' to change current order\n \
'Solicit' to advertise to special to customers\n \
'State' to query current robot state\n \
Command: ").lower()
    if cmd == 'a':
        pub.publish('a')
        submenu_ = True
        # break
    elif cmd == 'b':
        pub.publish('b')
        submenu_ = True
        # break
    elif cmd == 'c':
        pub.publish('c')
        submenu_ = True
        # break
    elif cmd == 'd':
        pub.publish('d')
        submenu_ = True
        # break
    elif cmd == 'cancel':
        pub.publish('cancel')
    elif cmd == 'change':
        pub.publish('change')
    elif cmd == 'solicit':
        pub.publish('solicit')
    elif cmd == 'state':
        pub.publish('state')  
        # submenu_ = True 
    # elif cmd == 'y':
    #     print("confirmation sent")
    #     print("sending bot to ", goal)
    #     sendGoal(goal)        
    else: 
        print("Command not recognized. Please enter again")
    #confirm
        # rospy.spin()


def start():
    global start_
    # print(start_==True) #startup check
    if start_ == True:
        cmd = input('Enter Manager username to begin: ')
        pub.publish("start")
        print("\n")
        print("Welcome", cmd)
        start_ = False



if __name__ == '__main__':

    rospy.init_node('restaurant_robot_controller')
    sub = rospy.Subscriber("state_confirm", String, menu)
    pub = rospy.Publisher("commands", String, queue_size=1)

    start()

    rospy.spin()
