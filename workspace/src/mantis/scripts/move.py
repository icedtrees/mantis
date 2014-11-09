#!/usr/bin/python

"""
Joystick module allowing control via a Logitech xbox controller. Allows multiple modes of movement
"""

import sys
import socket

import rospy
from sensor_msgs.msg import Joy


# Velocity constants. Can go up to 1023
MAX_SKID_VELOCITY = 250
MAX_FORWARD_VELOCITY = 400
MAX_TURN_VELOCITY = 30
MAX_LIFT_VELOCITY = 40


def joy_move(data):
    # left joystick: L/R 0 T/D 1
    # right joystick: L/R 3 T/D 4
    skid, velocity, _, turn, lift, _, _, _ = data.axes

    # start button: 7 (reset)
    reset = data.buttons[7]

    # send command over UDP to server
    if reset:
        # Reset servos to starting positions and stops the robot
        for command in ("T0", "L0", "s0", "v0"):
            joy_move.sock.sendall(command + "\n")
    else:
        commands = {"s": int(skid * MAX_SKID_VELOCITY),
                    "v": int(velocity * MAX_FORWARD_VELOCITY),
                    "t": int(turn * MAX_TURN_VELOCITY),
                    "l": int(lift * MAX_LIFT_VELOCITY)}
        for command, value in commands.items():
            joy_move.sock.sendall("{}{}\n".format(command, value))

    print data


def main():
    # set the host and port of the server
    try:
        joy_move.host, joy_move.port = sys.argv[1], int(sys.argv[2])
    except IndexError:
        print("Usage: {} server port".format(sys.argv[0]))
        exit(1)

    # create the socket
    joy_move.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    joy_move.sock.connect((joy_move.host, joy_move.port))

    # initialise the subscriber
    controller = rospy.Subscriber('joy', Joy, joy_move)
    rospy.init_node('controller', anonymous=True)
    rospy.spin()


if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
