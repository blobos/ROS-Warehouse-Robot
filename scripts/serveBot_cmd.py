#! /usr/bin/env python3

import rospy
from std_msgs.msg import String, UInt8

start_ = True

goal = ''
# prev_cmd = '' #for remote confirmation of delivery


# def Confirm(msg): #for remote confirmation
#     global prev_cmd
#     if msg.data:
#         print("prev_cmd", prev_cmd)
#         if prev_cmd == ('A' or 'B' or 'C' or 'D'):
#             prompt = String("Enter 'y' to confirm order to ", prev_cmd)
#             cmd = input(prompt)
#             if cmd.lower() == 'y':
#                 sendGoal(msg)
#     menu(msg)


def sendGoal(ABCD):
    if goal == 'A':
        print("publish toA")
        pub.publish("toA")
    if goal == 'B':
        print("publish toB")
        pub.publish("toB")
    if goal == 'C':
        print("publish toC")
        pub.publish("toC")
    if goal == 'D':
        print("publish toD")
        pub.publish("toD")



def StateRec(msg):
    if msg.data:
        print("\n STATE:", msg.data)
        menu(msg)
    


def menu(msg):
    global start_
    global goal
    # global prev_cmd
    while True:
        cmd = input("\nEnter one of the following commands:\n \
    'A', 'B', 'C', or 'D' to order to respective table\n \
    'Cancel' to cancel current order and return to station\n \
    'Change' to change current order\n \
    'Solicit' to advertise to special to customers\n \
    'State' to query current robot state\n \
    Command: ").upper()
        if cmd in 'ABCD':
            pub.publish(cmd)
            # prev_cmd = cmd
        elif cmd == 'CANCEL':
            # prev_cmd = cmd
            pub.publish('cancel')
        elif cmd == 'CHANGE':
            # prev_cmd = cmd
            pub.publish('change')
        elif cmd == 'SOLICIT':
            # prev_cmd = cmd
            cmd = int(input ("Enter number loops to run for soliciting (0 for infinite): ")) *4
            if cmd == 0:
                print(0)
                pub_solicit_count.publish(9999)    
            else:
                # print(cmd)
                pub_solicit_count.publish(cmd)
            cmd = input("Enter advertising message: ")
            pub.publish('solicit')
            pub_solicit.publish(cmd)
        elif cmd == 'STATE':
            ##not navigation command so no prev_cmd
            pub.publish('state')  
            break    
        else: 
            print("Command not recognized. Please enter again")
        #confirm
        # rospy.spin()



def startMessage():
    global start_
    # print(start_==True) #startup check
    if start_ == True:
        cmd = input('Enter Manager username to begin: ')
        while True:
            pwd = input('Enter password: ')
            if pwd == 'password':
                pub.publish("start")
                print("\n")
                print("Welcome", cmd)
                start_ = False
                break
            else: print("Wrong password")

        



if __name__ == '__main__':

    rospy.init_node('restaurant_robot_controller')
    sub = rospy.Subscriber("main_menu", String, menu)
    pub = rospy.Publisher("commands", String, queue_size=1)
    sub_state = rospy.Subscriber("state", String, StateRec)
    pub_solicit = rospy.Publisher("solicit_message", String, queue_size=1)
    pub_solicit_count = rospy.Publisher("solicit_count", UInt8, queue_size=1)
    # sub_confirm = rospy.Subscriber("confirm", String, Confirm) #remote_confirm

    startMessage()

    rospy.spin()
