#! /usr/bin/env python3

import rospy
import os
from std_msgs.msg import String, Bool

def bot_speak_cb(msg):
	# now use mimic to speak out the messages, not gTTS 
	if len(msg.data) != 0: 
		voicetype = 'slt'

		voice_cmd = '~/mimic1/mimic -voice {} -t "{}"'.format(voicetype, msg.data)
		print("speak_bot_msg:", msg.data)

		os.system(voice_cmd)    


if __name__ == '__main__':

    rospy.init_node('bot_speak')
    print("bot_speak node initiated ... ")

    sub = rospy.Subscriber('/my_cmd/bot_speak', String, bot_speak_cb)

    rospy.spin()



