#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import JointState
import time

def publish_joint_state():
    rospy.init_node('publish_joint_states', anonymous=True)
    pub = rospy.Publisher('/joint_states', JointState, queue_size=10)
    rate = rospy.Rate(60) 

    joint_state = JointState()
    joint_state.name = ['x_prismatic', 'y_prismatic', 'z_prismatic', 'finger_1_joint', 'finger_2_joint']
    joint_state.position = [0.0, 0.0, 0.0, 0.0, 0.0]  # Initial positions
    joint_state.velocity = []
    joint_state.effort = []

    target_positions = [-0.10, -0.30, -0.05, 0.02, 0.02]  # Target positions
    default_positions = [0.0, 0.0, 0.0, 0.0, 0.0]  # Default positions to return
    increments = 0.0005  # incremental movement step
    tolerance = 0.0001  # Tolerance - To avoid overshooting

    
    # Move a single joint smoothly to the target position
    def move_joint(index, target):
        while abs(joint_state.position[index] - target) > tolerance:
            if joint_state.position[index] < target:
                joint_state.position[index] += increments
            else:
                joint_state.position[index] -= increments
            joint_state.header.stamp = rospy.Time.now()
            pub.publish(joint_state)
            rate.sleep()
    
    # Move both finger joints together smoothly
    def move_fingers(target1, target2):
        while (abs(joint_state.position[3] - target1) > tolerance or
               abs(joint_state.position[4] - target2) > tolerance):
            if joint_state.position[3] < target1:
                joint_state.position[3] += increments
            else:
                joint_state.position[3] -= increments

            if joint_state.position[4] < target2:
                joint_state.position[4] += increments
            else:
                joint_state.position[4] -= increments

            joint_state.header.stamp = rospy.Time.now()
            pub.publish(joint_state)
            rate.sleep()

    # Move all joints back to their default positions
    def move_all_to_default():
        for index, target in enumerate(default_positions):
            move_joint(index, target)

    try:
        rospy.loginfo("Starting sequential joint movements")

        rospy.loginfo("Moving x_prismatic...")
        move_joint(0, target_positions[0])

        rospy.loginfo("Moving y_prismatic...")
        move_joint(1, target_positions[1])

        rospy.loginfo("Moving z_prismatic...")
        move_joint(2, target_positions[2])

        rospy.loginfo("Opening finger_1_joint and finger_2_joint...")
        move_fingers(target_positions[3], target_positions[4])

        rospy.loginfo("Closing finger_1_joint and finger_2_joint...")
        move_fingers(0.0, 0.0)

        rospy.loginfo("Returning to default positions...")
        move_all_to_default()

        rospy.loginfo("All movements completed successfully.")
    except rospy.ROSInterruptException:
        pass

if __name__ == '__main__':
    publish_joint_state()