from wheel_velocity import calculate_angle, get_angle_value

# TODO better name pls
# Make negative velocities into correct corresponding positive one
def _fix_vel(vel):
    if vel <= -2048:
        return _fix_vel(vel + 2048)
    elif vel <= -1024:
        return abs(vel + 1024)
    elif vel < 0:
        return abs(vel) + 1024
    elif vel >= 2048:
        return vel - 2048
    else:
        return vel

def _reverse(vel):
    vel = _fix_vel(vel)
    if vel < 1024:
        return vel + 1024
    elif vel >= 1024:
        return vel - 1024

class Mantis(object):
    __init__(self):
        # Establish a serial connection to the dynamixel network.
        # This usually requires a USB2Dynamixel
        serial = dynamixel.SerialStream(port=config.port,
                                        baudrate=config.baudRate,
                                        timeout=1)

        # Instantiate our network object
        self.net = dynamixel.DynamixelNetwork(serial)

        # Populate our network with dynamixel objects
        for servoId in config.wheels[0] + config.wheels[1] + config.joints:
            newDynamixel = dynamixel.Dynamixel(servoId, net)
            self.net._dynamixel_map[servoId] = newDynamixel

        # Set some variables about the state of the Mantis
        self.turnVel = 0
        self.liftVel = 0
        self.moveVel = 0
        self.skidVel = 0

    turnTo(self, angle, velocity):
        """Given an angle between -1 and 1, turn to that angle"""
        # Front joint turning
        actuator = self.net[config.joints[0]]
        if velocity == 0:
            actuator.stop()
        else:
            actuator.moving_speed = velocity
            actuator.goal_position = get_angle_value(angle)

        # Rear joint turning
        actuator = self.net[config.joints[2]]
        if velocity == 0:
            actuator.stop()
        else:
            actuator.moving_speed = velocity
            actuator.goal_position = get_angle_value(-angle)

    liftTo(self, angle, velocity):
        """Given an angle between -1 and 1, lift to that angle"""
        actuator = net[config.joints[1]]
        if velocity == 0:
            actuator.stop()
        else:
            actuator.moving_speed = velocity
            actuator.goal_position = 412 if angle < 0 else 652 # TODO arbitrary - linearly interpolate also

    execute(self):
        """Based on the 4 velocities (turn, lift, move, skid), move the mantis robot"""
        # Calculate the speed differential between left and right wheels, take angle from front joint
        data = calculate_angle(self.moveVel, net[config.joints[0]].current_position)

        # Set moving speed of wheels
        for servo in zip(config.wheels[0], data['wheels'][0]): # Left wheels
            # Servo is a tuple (id, vel)
            actuator = self.net[servo[0]]
            actuator.moving_speed = _fix_vel(servo[1] - self.skidVel)
        for servo in zip(config.wheels[1], data['wheels'][1]): # Right wheels
            # Servo is a tuple (id, vel)
            actuator = self.net[servo[0]]
            actuator.moving_speed = _reverse(servo[1] + self.skidVel)

        # Front joint turning
        actuator = self.net[config.joints[0]]
        if self.turnVel == 0:
            actuator.stop()
        else:
            actuator.moving_speed = abs(self.turnVel)
            actuator.goal_position = get_angle_value(1 if self.turnVel > 0 else -1)

        # Rear joint turning
        actuator = self.net[config.joints[2]]
        if self.turnVel == 0:
            actuator.stop()
        else:
            actuator.moving_speed = abs(self.turnVel)
            actuator.goal_position = get_angle_value(1 if self.turnVel > 0 else -1)

        # Lifting joint
        actuator = net[config.joints[1]]
        if self.liftVel == 0:
            actuator.stop()
        else:
            actuator.moving_speed = abs(self.liftVel)
            actuator.goal_position = 412 if self.liftVel < 0 else 652 # TODO arbitrary

        # Write the changes
        net.synchronize()