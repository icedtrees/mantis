from pyoarkit import Mantis

robot = Mantis()

def execute_command(cmd):
    if cmd[0] == 'v':
        # Modify velocity
        vel = int(cmd[1:])

        robot.move(vel, False)
    elif cmd[0] == 's':
        # Spin
        vel = int(cmd[1:])

        robot.move(vel, True)
    elif cmd[0] == 't':
        # Turn
        vel = int(float(cmd[1:]))
        
        robot.turn(1 if vel > 0 else -1, vel)
    elif cmd[0] == 'l':
        # Lift
        vel = int(float(cmd[1:]))
        
        robot.lift(1 if vel > 0 else -1, vel)
    elif cmd[0] == 'T':
        # Turn
        position = float(cmd[1:])
        
        robot.turn(position, 50) # Arbitrary speed
    elif cmd[0] == 'L':
        # Lift
        position = float(cmd[1:])
        
        robot.lift(position, 50) # Arbitrary speed
    elif cmd[0] == 'r':
    	# Reset
    	robot.turn(0, 50)
    	robot.lift(0, 50)
    	robot.move(0, True)
    	robot.move(0, False)

while True:
	execute_command(raw_input())