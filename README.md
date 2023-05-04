# ROS Warehouse Robot
Scripts for ROS robot with robot arm:

This scenario mimics a shipping warehouse environment. In this scenario, the robot picks up a crate of products and transports them from their respective storage locations to the loading station. There is also a charging station. 
Once the robot reaches the inventory site, it will ask for confirmation if the object is securely placed. Once confirmation is received, the robot will move towards the loading station for drop off. The pickup operation can be canceled by entering ‘n’.  By entering any other key, the robot will try to pick it up again. After each pickup/drop off, the camera is set back to camera forward. 
Before each pickup, the person detection will be turned on. When a person (or shoe) is detected, it will tell the person to move. As the robot’s purpose is only to load crates for shipping, there is no need for it to patrol.


![image](https://user-images.githubusercontent.com/7018624/236269920-4bf3ebea-aef4-45ee-a6fb-fbf0fff41607.png)

Voice commands – 
‘Home’ returns the robot to the charging station. At the charging station, the command PC will speak and remind the user to plug in the charging cable. 
‘A/B/C site’ moves the robot to the respective pickup sites and picks up the crate of products
‘Drop’ moves the robot to drop off site to set the crate down.
https://youtu.be/RZ_vFJ7vA90
