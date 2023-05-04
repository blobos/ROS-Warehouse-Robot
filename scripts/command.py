#!/usr/bin/env python

import rospy
import socket
from threading import Thread
import actionlib
from std_msgs.msg import Bool, String, Int32
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal

from coco_labels import ssd_coco_labels 

detect_object = False  # Do something when object is detected or not 
recognize_person = False

pub_patrol_control = None
object_to_detect = 'person'

def detect_obj_cb(msg):
	global detect_object 
	global pub_patrol_control
	global object_to_detect

	if detect_object:
		print("Object {} is detected".format(ssd_coco_labels[msg.data]))
		# compare with a target object
		if msg.data == ssd_coco_labels.index(object_to_detect):  # id == 1, a person
			print("Our target object is detected ... stop the robot")
			pub_patrol_control.publish('pause')
			# and do other behaviors as you see fit
			detect_object = False  # switch off the object detection when the desired object is detected, until called again 
			print("'m' to move to Goal A \n'd' to detect an object \n'r' to recognize a person \n'p' to pick up an object \n'q' to quit.\n")
		else:
			print("object detected not our target object")

def recognized_cb(msg):
	global recognize_person
	if recognize_person: 
		print(msg.data, " is recognized")
		# do something here
		recognize_person = False  # just do once and switch off the callback until called again 

def socket_listen():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('', 8084))
	s.listen(2)
	s.settimeout(None)
	while True:
		conn, addr = s.accept()
		# with conn:
		print("Connected by {}".format(addr))
		try:         
			data = conn.recv(1024).decode()
			if data: 
				print("data received: ", data)
				# check and execute the command here:
				if data == 'forward':
					pub_cf_move.publish('forward')
					# pub_bot_speak.publish('I have arrived at the location')
				elif data == 'backward':
					pub_cf_move.publish('backward')
				elif data == 'pick':
					pub_arm_cmd.publish('pick')
				elif data == 'speak':
					pub_bot_speak.publish('Hello, how are you?')
		finally:
			conn.close()

if __name__ == '__main__':

	rospy.init_node('command_center')
	print("command_center node initiated ... ")
	# obj_detect_pub = rospy.Publisher("/my_cmd/detect_obj_id", Int32, queue_size=1)

	detect_object_sub = rospy.Subscriber("/my_cmd/object_detected", Int32, detect_obj_cb)
	recognized_sub = rospy.Subscriber("/my_cmd/recognized_person", String, recognized_cb)

	pub_patrol_control = rospy.Publisher('/my_cmd/patrol_control', String, queue_size=1)
	pub_arm_cmd = rospy.Publisher('/my_cmd/arm_cmd', String, queue_size=1)
	pub_cf_move = rospy.Publisher('/my_cmd/cf_move', String, queue_size=1)
	pub_bot_speak = rospy.Publisher('/my_cmd/bot_speak', String, queue_size=1)
	
	thread_listen = Thread(target=socket_listen, args=())
	thread_listen.setDaemon(True)
	thread_listen.start()

	cmd = raw_input("'m' to move to Goal A \n'd' to detect an object \n'r' to recognize a person \n'p' to pick up an object \n'f' to move forward \n's' to ask for command \n'q' to quit.\n")
	while True:
		print ("cmd is", cmd)
		if cmd == 'm':
			pub_patrol_control.publish('move_goal')
		elif cmd == 'd':
			# just get ready to detect one object. Stop detecting when the specific object detected
			detect_object = True
		elif cmd == 'r':
			recognize_person = True
		elif cmd == 'p':
			pub_arm_cmd.publish('pick')
		elif cmd == 'f':
			pub_cf_move.publish('forward')
		elif cmd == 's':
			pub_bot_speak.publish('What can I do for you')		
		elif cmd == 'q':
			pub_patrol_control.publish('quit')
			break
		else: 
			print("Command not recognized. Please enter again")
		cmd = raw_input("'m' to move to Goal A \n'd' to detect an object \n'r' to recognize a person \n'p' to pick up an object \n'f' to move forward \n's' to ask for command \n'q' to quit.\n")

	print("Hit Ctrl-C to terminate the node")

	rospy.spin()