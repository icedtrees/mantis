from wheel_velocity import calculate_angle, get_angle_value
import dynamixel
import config

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
    def __init__(self):
        # Establish a serial connection to the dynamixel network.
        # This usually requires a USB2Dynamixel
        serial = dynamixel.SerialStream(port=config.port,
                                        baudrate=config.baudRate,
                                        timeout=1)

        # Instantiate our network object
        self.net = dynamixel.DynamixelNetwork(serial)

        # Populate our network with dynamixel objects
        for servoId in config.wheels[0] + config.wheels[1] + config.joints:
            newDynamixel = dynamixel.Dynamixel(servoId, self.net)
            self.net._dynamixel_map[servoId] = newDynamixel

        # Initial read in
        for actuator in self.net.get_dynamixels():
            print 'Currently on motor %d' % actuator.id
            actuator.read_all()
            if actuator.id in config.wheels[0]:
                print '    Left wheel'
                actuator.cw_angle_limit = 0
                actuator.ccw_angle_limit = 0
                # actuator.moving_speed = 200
            elif actuator.id in config.wheels[1]:
                print '    Right wheel'
                actuator.cw_angle_limit = 0
                actuator.ccw_angle_limit = 0
                # actuator.moving_speed = 1223
            elif actuator.id in config.joints:
                print '    Joint'
                actuator.cw_angle_limit = 0
                actuator.ccw_angle_limit = 1023
                # actuator.moving_speed = 100
                # actuator.torque_enable = True
                # actuator.torque_limit = 800 
                # actuator.max_torque = 800
                # actuator.goal_position = 512
            else:
                print '    Something is wrong'

        # Some state information of the Mantis robot
        self.moveVel = 0
        self.skidVel = 0

    def move(self, velocity, skid):
        """
        Given a velocity, move at that velocity. If skid is true, this sets the skid
        steering velocity.
        """
        if skid:
            self.skidVel = velocity
        else:
            self.moveVel = velocity

        # Calculate the speed differential between left and right wheels, take angle from front joint
        data = calculate_angle(self.moveVel, self.net[config.joints[0]].current_position)

        # Set moving speed of wheels
        for servo in zip(config.wheels[0], data['wheels'][0]): # Left wheels
            # Servo is a tuple (id, vel)
            actuator = self.net[servo[0]]
            actuator.moving_speed = _fix_vel(servo[1] - self.skidVel)
        for servo in zip(config.wheels[1], data['wheels'][1]): # Right wheels
            # Servo is a tuple (id, vel)
            actuator = self.net[servo[0]]
            actuator.moving_speed = _reverse(servo[1] + self.skidVel)

        self.net.synchronize()

    def turn(self, angle, velocity):
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

        self.net.synchronize()

    def lift(self, angle, velocity):
        """Given an angle between -1 and 1, lift to that angle"""
        actuator = net[config.joints[1]]
        if velocity == 0:
            actuator.stop()
        else:
            actuator.moving_speed = velocity
            actuator.goal_position = 412 if angle < 0 else 652 # TODO arbitrary - linearly interpolate also

        self.net.synchronize()
