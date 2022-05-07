from servo import Servo, servo2040
from time import sleep

s = Servo(servo2040.SERVO_18)
s.to_mid()
# s.to_max()
# sleep(1)
# s.value(-50)
# sleep(1)
# s.to_min()