# main.py

from servo import Servo, servo2040
from time import sleep
from pimoroni import Button
import array, time
from machine import Pin, PWM
import rp2

s = Servo(servo2040.SERVO_18)

class ws2812():
    # Configure the number of WS2812 LEDs, pins and brightness.
    NUM_LEDS = 12
    PIN_NUM = 16
    __brightness = 0.1
    
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 150, 0)
    GREEN = (0, 255, 0)
    CYAN = (0, 255, 255)
    BLUE = (0, 0, 255)
    PURPLE = (180, 0, 255)
    WHITE = (255, 255, 255)
    COLORS = (BLACK, RED, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE)
     
    @rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
    def ws2812():
        T1 = 2
        T2 = 5
        T3 = 3
        wrap_target()
        label("bitloop")
        out(x, 1)               .side(0)    [T3 - 1]
        jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
        jmp("bitloop")          .side(1)    [T2 - 1]
        label("do_zero")
        nop()                   .side(0)    [T2 - 1]
        wrap()
 
    def __init__(self):
        # Create the StateMachine with the ws2812 program, outputting on Pin(16).
        self.sm = rp2.StateMachine(0, self.ws2812, freq=8_000_000, sideset_base=Pin(self.PIN_NUM))
         
        # Start the StateMachine, it will wait for data on its FIFO.
        self.sm.active(1)
        # Display a pattern on the LEDs via an array of LED RGB values.
        self.ar = array.array("I", [0 for _ in range(self.NUM_LEDS)])
 
    @property
    def brightness(self)->float:
        return self.__brightness
    
    @brightness.setter
    def brightness(self, value:float):
        if (value <=1) and (value >=0):
            self.__brightness = value
        print(f'brightness: {self.__brightness}')
        self.show()
 
    def show(self):
        dimmer_ar = array.array("I", [0 for _ in range(self.NUM_LEDS)])
        for i,c in enumerate(self.ar):
            r = int(((c >> 8) & 0xFF) * self.__brightness)
            g = int(((c >> 16) & 0xFF) * self.__brightness)
            b = int((c & 0xFF) * self.__brightness)
            dimmer_ar[i] = (g<<16) + (r<<8) + b
        self.sm.put(dimmer_ar, 8)
#         time.sleep_ms(10)
 
    def fill_rgb(self, i, color):
        self.ar[i] = (color[1]<<16) + (color[0]<<8) + color[2]
 
    def fill(self, color):
        for i in range(len(self.ar)):
            self.fill_rgb(i, color)
 
    def set_rgb(self, index:int, red:int, green:int, blue:int):
        dimmer_ar = array.array("I", [0 for _ in range(self.NUM_LEDS)])
        for i,c in enumerate(self.ar):
            r = int(((c >> 8) & 0xFF) * self.__brightness)
            g = int(((c >> 16) & 0xFF) * self.__brightness)
            b = int((c & 0xFF) * self.__brightness)
            dimmer_ar[i] = (g<<16) + (r<<8) + b
        self.sm.put(dimmer_ar, 8)
#         time.sleep_ms(10)
        self.show()

    def cycle
class Cyber_glasses():
    
    arm_position = 'down'
    led_strip = ws2812()
    
    def __init__(self):
        self.led_strip.set_rgb(0,255,0,0)
        self.led_strip.show()
        self.led_strip.fill(self.led_strip.WHITE)
        for i in range(-1,100,1):
            self.led_strip.brightness = i / 100
#             self.led_strip.show()
            sleep(0.0001)
        for i in range(100,-1,-1):
            self.led_strip.brightness = i / 100
#             self.led_strip.show()
            sleep(0.0001)

    def light_away(self):
        s.to_max()
        self.arm_position = 'up'
        sleep(0.5)
        
    def light_down(self):
        arm_position = 'down'
        s.value(-30)
        sleep(0.5)
    
    def glow(self, r,g,b):
        for led in range(self.NUM_LEDS):
            self.led_strip.set_rgb(led, r, g, b)
            

glasses = Cyber_glasses()
glasses.led_strip.set_rgb(1,255,255,0)
glasses.led_strip.show()

# while True:
#     glasses.glow(255,0,0)
#     glasses.light_away()
#     sleep(1)
#     glasses.light_down()
#     sleep(1)
