#!/usr/bin/env python3

import cmd
from compileall import compile_file
from glob import glob
from logging import logThreads
from multiprocessing import log_to_stderr
from threading import local

from click import confirm
import rospy
import actionlib
from std_msgs.msg import Bool, String
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal

waypoints = [
    # 0 Red Left Top A
    [(-2.0137603282928467, -0.7833502292633057, 0.0), (0.0, 0.0, .0, 1)],
    # 1 Blue Right Top B
    [(-2.06679630279541, 0.6627177596092224, 0.0), (0.0, 0.0, 0, 1.0)],
    # 2 Green Left Bottom C
    [(-1.012818694114685, 1.6285568475723267, 0.0), (0.0, 0.0, -0.7, 0.7)],
    # 3 Yellow Right Bottom D
    [(1.0090962648391724, 2.0157527923583984, 0.0), (0.0, 0.0, -0.7086653923021379, 0.705544726968643)],
    # 4 Wood Kitchen
    [(-0.870195209980011, -1.9569478034973145, 0.0), (0.0, 0.0, 0.7, 0.7)],
    # 5 Brick Station
    [(1.0314879417419434, -1.886116623878479, 0.0), (0.0, 0.0, 0.7, 0.7)],
    # 6 Orange Garbage/Return/Drink Refill
    [(2.5, -0.5, 0.0), (0.0, 0.0, -0.7, 0.7)],
    ]

def goal_pose(pose):
    goal_pose = MoveBaseGoal()
    goal_pose.target_pose.header.frame_id = 'map'
    goal_pose.target_pose.pose.position.x = pose[0][0]
    goal_pose.target_pose.pose.position.y = pose[0][1]
    goal_pose.target_pose.pose.position.z = pose[0][2]
    goal_pose.target_pose.pose.orientation.x = pose[1][0]
    goal_pose.target_pose.pose.orientation.y = pose[1][1]
    goal_pose.target_pose.pose.orientation.z = pose[1][2]
    goal_pose.target_pose.pose.orientation.w = pose[1][3]

    return goal_pose

client = None
solicit_bool = False
# confirm_bool = False #for remote confirm
change_bool = False
prev_cmd = "None"
state_label = 'default'
solicit_message = "Come and try our new dessert"

def solicit():
    next_goal = 0
    global client
    global solicit_bool
    global solicit_message
    global state_label
    
    while solicit_bool == True:
        state_label = "Soliciting"
        goal = goal_pose(waypoints[next_goal])
        client.send_goal(goal)
        client.wait_for_result()
        print(solicit_message)
        rospy.sleep(3)
        if next_goal == 3:
            next_goal = 0
        else:
            next_goal = next_goal + 1

def Solicit_Message(msg):
    global solicit_message
    solicit_message = msg.data

def goto(waypoint):
    global client
    global state_label

    TIME_ALLOWED = 300

    start_time = rospy.get_time()

    goal = goal_pose(waypoints[waypoint])
    client.send_goal(goal)
    if waypoint in range(0,3):
        time_lapse = rospy.get_time() - start_time
        state_label = "In_customer_delivery"
        rospy.loginfo(state_label)
        if time_lapse > TIME_ALLOWED:
            client.cancel_goal()
            goto(4)
            client.wait_for_result()
            print("Cannot deliver to seating",prev_cmd," for some reason")
    elif waypoint == 4:
        state_label = "Going_to_kitchen"
        rospy.loginfo(state_label)
    elif waypoint ==  5:
        state_label = "Going_to_charging"
        rospy.loginfo(state_label)

def state_update():
    #0 pending, 1 active, 2 preempted, 3 succeeded, 4 aborted
    #5 rejected, 6 preempting, 7 recalling, 8 recalled, 9 lost
    global client
    global state_label
    state = client.get_state()
    if state == 3  and state_label == "Going_to_kitchen":
        state_label = "At_kitchen"     
    elif state == 3 and state_label == "Going_to_charging":
        state_label = "At_charging"
    elif state == 9 or state_label == None:
        state_label = "N/A. Send navigation command before state retrieval"
    elif state == 3 and state_label == "In_customer_delivery":
        print("Enjoy your meal!")
        rospy.sleep(2)
        goto(5)
        

# def confirmation(): #for remote confirmation
#     global prev_cmd
#     global confirm_bool
#     # print("state_label", state_label, " confirm_bool", confirm_bool)
#     if state_label == "At_kitchen" and confirm_bool == True:
#         print("confirmation prompt sent")
#         confirm_pub.publish(prev_cmd)
#         confirm_bool = False

def local_confirmation():
    global prev_cmd
    global state_label


    if state_label == "At_kitchen" and prev_cmd in 'ABCD':
        if not change_bool:
            print("Place order onto Robot for table ", prev_cmd)
        else: 
            print("Order changed. Please give me the new ordered meal")
        cmd = input ("Enter 'y' to confirm: ")
        if cmd.lower() == 'y':
            if prev_cmd == 'A':
                state_label = "In_customer_delivery"
                rospy.loginfo("Delivering to table A")
                goto(0)
                client.wait_for_result()
                

            elif prev_cmd == 'B':
                state_label = "In_customer_delivery"
                rospy.loginfo("Delivering to table B")
                goto(1)
                client.wait_for_result()

            elif prev_cmd == 'C':
                state_label = "In_customer_delivery"
                rospy.loginfo("Delivering to table C")
                goto(2)
                client.wait_for_result()

            elif prev_cmd == 'D':
                state_label = "In_customer_delivery"
                rospy.loginfo("Delivering to table D")
                goto(3)
                client.wait_for_result()




def actionFollow(msg):
    global solicit_bool
    # global confirm_bool
    global client
    global waypoints
    global state_label
    global prev_cmd
    global change_bool


    if msg.data in 'ABCD':
        # confirm_bool = True 
        prev_cmd = msg.data
        goto(4)       

    elif msg.data == 'cancel':
        state_label = "Going_to_kitchen"
        solicit_bool = False
        client.cancel_goal()
        prev_cmd = msg.data
        print("Returning to Kitchen")
        goto(4)
        client.wait_for_result()
        print("Ordered cancelled")

    elif msg.data == 'change':
        change_bool = True
        rospy.loginfo("Changing order")
        client.cancel_goal()
        goto(4)
        client.wait_for_result()
        
    elif msg.data == 'solicit':
        print("Soliciting")
        solicit_bool = True

    elif msg.data == 'state':
        print(state_label, prev_cmd, client.get_state())
        state_pub.publish(state_label)

    elif msg.data == 'start':
        main_pub.publish("start")
        print("Robot connected")



if __name__ == '__main__':

    rospy.init_node('patrol')
    print("Robot initiated")
    rospy.Subscriber("commands", String, actionFollow)
    rospy.Subscriber("solicit_message", String, Solicit_Message)

    main_pub = rospy.Publisher("main_menu", String, queue_size=1)
    state_pub = rospy.Publisher("state", String, queue_size=1)
    # confirm_pub = rospy.Publisher("confirm", String, queue_size=1)

    client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
    client.wait_for_server()

    while not rospy.is_shutdown():
        solicit()
        state_update()
        local_confirmation()
        # confirmation()      
    rospy.spin() 