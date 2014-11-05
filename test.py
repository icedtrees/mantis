from pyoarkit import Mantis

robot = Mantis()

def execute_command(cmd):
    if cmd[0] == 'v':
        # Modify velocity
        vel = int(cmd[1:])

        robot.moveVel = vel
    elif cmd[0] == 's':
        # Spin
        vel = int(cmd[1:])

        robot.skidVel = vel
    elif cmd[0] == 't':
        # Turn
        vel = int(float(cmd[1:]))
        
        robot.turnVel = vel
    elif cmd[0] == 'l':
        # Lift
        vel = int(float(cmd[1:]))
        
        robot.liftVel = vel
    elif cmd[0] == 'T':
        # Turn
        position = float(cmd[1:])
        
        robot.turnTo(position, 50) # Arbitrary speed
    elif cmd[0] == 'L':
        # Lift
        position = float(cmd[1:])
        
        robot.liftTo(position, 50) # Arbitrary speed

    robot.execute()

while True:
	execute_command(raw_input())