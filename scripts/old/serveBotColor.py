#!/usr/bin/env python3

import cmd
from compileall import compile_file
from glob import glob

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
moving_bool = False
prev_cmd = "None"
state_label = ''

def solicit():
    next_goal = 0
    global client
    global solicit_bool

    while solicit_bool == True:
        goal = goal_pose(waypoints[next_goal])
        client.send_goal(goal)
        client.wait_for_result()
        # print(next_goal, "goal complete")
        if next_goal == 3:
            next_goal = 0
        else:
            next_goal = next_goal + 1

def goto(waypoint):
    global client
    
    goal = goal_pose(waypoints[waypoint])
    client.send_goal(goal)
    # client.wait_for_result()


def state():
    #0 pending, 1 active, 2 preempted, 3 succeeded, 4 aborted
    #5 rejected, 6 preempting, 7 recalling, 8 recalled, 9 lost
    global client
    state = client.get_state()
    print(state)
    confirm_pub.publish("test")
    if state == 0 or 1:
        confirm_pub.publish(state_label)
        print(state_label)
    elif state == (3 or 9)  and state_label == "Going_to_kitchen":
        confirm_pub.publish("At_kitchen")
        print(state_label)
    elif state == (3 or 9) and state_label == "Going_to_charging":
        confirm_pub.publish("At_charger")
        print(state_label)
 

def actionFollow(msg):
    global solicit_bool
    global client
    global waypoints
    global state_label
    global goal

    if msg.data == 'a': 
        goto(4)
        print("at kitchen")
        print("publish confirm_A?")
        confirm_pub.publish("confirm_A")
    elif msg.data == 'toA':
        state_label = "In_customer_delivery"
        confirm_pub.publish("")
        print("A confirmed")
        goto(0)
        # rospy.sleep(2)
        # goto(4)

    elif msg.data == 'b':
        goto(4)
        print("at Kitchen")
        print("publish confirm_B")
        confirm_pub.publish("confirm_B")
    elif msg.data == 'toB':
        confirm_pub.publish("")
        state_label = "In_customer_delivery"
        print("B confirmed")
        goto(1)
        # rospy.sleep(2)
        # goto(4)

    elif msg.data == 'c':
        goto(4)
        print("at Kitchen")
        print("publish confirm_C")
        confirm_pub.publish("confirm_C")
    elif msg.data == 'toC':
        state_label = "In_customer_delivery"
        print("C confirmed")
        goto(2)

    elif msg.data == 'd':
        goto(4)
        print("at Kitchen")
        print("publish confirm_D?")
        confirm_pub.publish("confirm_D")
    elif msg.data == 'toD':
        state_label = "In_customer_delivery"
        print("D confirmed")
        goto(3)


    elif msg.data == 'cancel':
        state_label = "Going_to_kitchen"
        solicit_bool = False
        client.cancel_all_goals()
        print("Order cancelled, returning to Kitchen")
        goto(4)

    elif msg.data == 'change':
        print("Changing order")
        client.cancel_goal()
        goal = goal_pose(waypoints[4])
    elif msg.data == 'solicit':
        print("Soliciting")
        solicit_bool = True
    elif msg.data == 'state':
        confirm_pub.publish(state())
    elif msg.data == 'alt':
        goto(5)

    elif msg.data == 'start':
        confirm_pub.publish("start")



if __name__ == '__main__':

    rospy.init_node('patrol')
    print("patrol node initiated")
    rospy.Subscriber("commands", String, actionFollow)
    

    confirm_pub = rospy.Publisher("state_confirm", String, queue_size=1)
    confirm_pub.publish("0")

    client = actionlib.SimpleActionClient('move_base', MoveBaseAction)

    while not rospy.is_shutdown():
        solicit()

    rospy.spin()