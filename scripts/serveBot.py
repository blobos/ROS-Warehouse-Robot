#!/usr/bin/env python3

import rospy
import actionlib
from std_msgs.msg import String, UInt8
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal

waypoints = [
    # 0 A Left Top
    [(-5.996887683868408, 2.647653579711914, 0.0), (0.0, 0.0, -0.004327434578415631, 0.9999906366111483)],
    # 1 B Right Top
    [(5.017152786254883, 4.9510393142700195, 0.0), (0.0, 0.0, -0.9995205068464919, 0.030963791649797106)],
    # 2 C Left Bottom
    [(-5.948310852050781, 0.5047111511230469, 0.0), (0.0, 0.0, 0.0076742825228511445, 0.9999705522602951)],
    # 3 D Right Bottom
    [(4.877748012542725, 2.6365699768066406, 0.0), (0.0, 0.0, -0.9998994280032624, 0.01418216763223549)],
    # 4 Kitchen
    [(3.0324013233184814, -5.3826069831848145, 0.0), (0.0, 0.0, 0.0037359962408318255, 0.999993021141692)],
    # 5 Charging Station
    [(8.419149398803711, -8.167566299438477, 0.0), (0.0, 0.0, -0.9997717846494557, 0.02136301989051096)]
    # # 6 Garbage/Return/Drink Refill
    # [(4, -9.3, 0.0), (0.0, 0.0, 0.7, 0.7)],
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
solicit_count = 9999
# confirm_bool = False #for remote confirm
change_bool = False
prev_cmd = "None"
state_label = 'default'
solicit_message = "Come and try our new dessert"

def solicit():
    next_goal = 0
    global client
    global solicit_bool
    global solicit_count
    global solicit_message
    global state_label
    
    while solicit_bool == True and solicit_count > 0:
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
        solicit_count -= 1
        # print(solicit_count)
    goto(4)
    

def Solicit_Message(msg):
    global solicit_message
    solicit_message = msg.data

def Solicit_count(msg):
    global solicit_count
    solicit_count = msg.data

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
        # rospy.loginfo(state_label)
        if time_lapse > TIME_ALLOWED:
            client.cancel_goal()
            goto(5)
            client.wait_for_result()
            print("Cannot deliver to seating",prev_cmd," for some reason")
    elif waypoint == 4:
        state_label = "Going_to_kitchen"
        # rospy.loginfo(state_label)
    elif waypoint ==  5:
        state_label = "Going_to_charging"
        # rospy.loginfo(state_label)

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
                # rospy.loginfo("Delivering to table A")
                goto(0)
                client.wait_for_result()
                

            elif prev_cmd == 'B':
                state_label = "In_customer_delivery"
                # rospy.loginfo("Delivering to table B")
                goto(1)
                client.wait_for_result()

            elif prev_cmd == 'C':
                state_label = "In_customer_delivery"
                # rospy.loginfo("Delivering to table C")
                goto(2)
                client.wait_for_result()

            elif prev_cmd == 'D':
                state_label = "In_customer_delivery"
                # rospy.loginfo("Delivering to table D")
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
        # rospy.loginfo("Changing order")
        client.cancel_goal()
        goto(4)
        client.wait_for_result()
        
    elif msg.data == 'solicit':
        prev_cmd = msg.data
        # rospy.loginfo("Soliciting")
        solicit_bool = True

    elif msg.data == 'state':
        # rospy.loginfo(state_label, prev_cmd, client.get_state())
        state_pub.publish(state_label)

    elif msg.data == 'start':
        main_pub.publish("start")
        print("Robot connected")



if __name__ == '__main__':

    rospy.init_node('patrol')
    print("Robot initiated")
    rospy.Subscriber("commands", String, actionFollow)
    rospy.Subscriber("solicit_message", String, Solicit_Message)
    rospy.Subscriber("solicit_count", UInt8, Solicit_count)

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