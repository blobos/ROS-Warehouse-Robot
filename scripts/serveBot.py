#!/usr/bin/env python3

import rospy
import actionlib
from std_msgs.msg import Bool, String
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal

waypoints = [
    # 0 A Left Top
    [(-5.9, 2.7, 0.0), (0.0, 0.0, -1, 0.0)],
    # 1 B Right Top
    [(5.0, 5.0, 0.0), (0.0, 0.0, -5, 1.0)],
    # 2 C Left Bottom
    [(-5.0, 0.5, 0.0), (0.0, 0.0, 1.0, 0.0)],
    # 3 D Right Bottom
    [(5.5, 2.3, 0.0), (0.0, 0.0, 0, 1.0)],
    # 4 Kitchen
    [(5.5, 2.3, 0.0), (0.0, 0.0, 0, 1.0)],
    # 5 Charging Station
    [(7.8, -8.4, 0.0), (0.0, 0.0, -1, 0.0)],
    # 6 Garbage/Return/Drink Refill
    [(4, -9.3, 0.0), (0.0, 0.0, 0.7, 0.7)],
    ]

client = None
solicit_bool = False

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
    client.wait_for_result

def actionFollow(msg):
    global solicit_bool
    global client
    global waypoints

    if msg.data == 'a':
        print("Going to A")
        goto(0)
        print("Enjoy your meal.")
        goto(4)
        # pub.publish("kitchen")
        goal = goal_pose(waypoints[4])
        client.send_goal(goal)
        print("Returning to Kitchen")
        client.wait_for_result()
        # pub.publish("kitchen")
    elif msg.data == 'b':
        goal = goal_pose(waypoints[1])
        client.send_goal(goal)
        print("Going to B")
        client.wait_for_result()
        print("Enjoy your meal.")
        goal = goal_pose(waypoints[4])
        client.send_goal(goal)
        print("Returning to Kitchen")
        client.wait_for_result()
        # pub.publish("kitchen")
    elif msg.data == 'c':
        print("Going to C")
        goal = goal_pose(waypoints[2])
        client.send_goal(goal)
        client.wait_for_result()
        # pub.publish("kitchen")
    elif msg.data == 'd':
        print("Going to D")
        goal = goal_pose(waypoints[3])
        client.send_goal(goal)
        client.wait_for_result()
        # pub.publish("kitchen")
    elif msg.data == 'cancel':
        solicit_bool = False
        client.cancel_goal()
        print("Order cancelled, returning to Kitchen")
        goal = goal_pose(waypoints[4])
    elif msg.data == 'change':
        print("Changing order")
        client.cancel_goal()
        goal = goal_pose(waypoints[4])
    elif msg.data == 'solicit':
        print("Soliciting")
        solicit_bool = True


if __name__ == '__main__':

    rospy.init_node('patrol')
    print("patrol node initiated")
    rospy.Subscriber("commands", String, actionFollow)

    

    confirm_pub = rospy.Publisher("state", String, queue_size=1)

    client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
    client.wait_for_server()

    rospy.spin()