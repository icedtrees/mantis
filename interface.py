"""
A sample interface which uses the pyoarkit library.
This interface involves a very simple command system:
    <command><value>
where <command> is a single letter and <value> is some number.

For example: v200 sets the velocity to 200.
"""

from pyoarkit import Mantis

robot = Mantis()


def execute_command(cmd):
    command, value = cmd[0], int(cmd[1:])
    commands = dict(v=robot.move, s=robot.skid, t=robot.turn, l=robot.lift, T=robot.turn_to, L=robot.lift_to)
    # Call the mantis command using the given parameter
    (commands[command])(value)


if __name__ == "__main__":
    # Testing function. Type in commands
    while True:
        execute_command(raw_input())
