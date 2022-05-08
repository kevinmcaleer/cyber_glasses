# main.py

from servo import Servo, servo2040
from time import sleep
from pimoroni import Button
import array, time
from machine import Pin, PWM
import rp2
import math

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
 
    def set_rgb2(self, i, r,b,g):
        self.ar[i] = (g<<16) + (r<<8) + b
        self.show()
 
    def fill(self, r,g,b):
        for i in range(len(self.ar)):
            self.set_rgb2(i, r,g,b)
        self.show()
    
    def rgb2hsv(self, r:int, g:int, b:int):
        h = 0
        s = 0
        v = 0
        # constrain the values to the range 0 to 1
        r_normal, g_normal, b_normal,  = r / 255, g / 255, b / 255
        cmax = max(r_normal, g_normal, b_normal)
        cmin = min(r_normal, g_normal, b_normal)
        delta = cmax - cmin
        
        # Hue calculation
        if(delta ==0):
            h = 0
        elif (cmax == r_normal):
            h = (60 * (((g_normal - b_normal) / delta) % 6))
        elif (cmax == g_normal):
            h = (60 * (((b_normal - r_normal) / delta) + 2))
        elif (cmax == b_normal):
            h = (60 * (((r_normal - g_normal) / delta) + 4))
        
        # Saturation calculation
        if cmax== 0:
            s = 0
        else:
            s = delta / cmax
            
        # Value calculation
        v = cmax
        
        print(f"normals are: {r_normal}, {g_normal}, {b_normal}, cmax is {cmax}, delta is {delta}")
        print(f"h:{h}, s:{s}, v:{v}")
        return h, s, v        
 
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
    
    def set_hsv(self, index, hue, sat, val):
        r,g,b = self.hsv2rgb(hue, sat,val)
#         print(f'r:{r}, g:{g}, b:{b}, hue:{hue}, sat:{sat}, val:{val}')
        self.set_rgb2(index, r, g, b)
        self.show()
    
    def hsv2rgb(self, hue, sat, val):
        """ Sets the Hue Saturation and Value of the indexed RGB LED"""
    
        i = math.floor(hue * 6)
        f = hue * 6 - i
        p = val * (1 - sat)
        q = val * (1 - f * sat)
        t = val * (1 - (1 - f) * sat)

        r, g, b = [
            (val, t, p),
            (q, val, p),
            (p, val, t),
            (p, q, val),
            (t, p, val),
            (val, p, q),
        ][int(i % 6)]
        r = int(r*255)
        g = int(g*255)
        b = int(b*255)
        
        return r, g, b

    def cycle(self):
        """ Cycle through all the colours """
#         pass
        for i in range (0, 100, 1):
            for j in range (self.NUM_LEDS):
                self.set_hsv(j,i/100,1,1) 
                sleep(0.0001)
    def spin(self, loops=None):
        if not loops:
            loops = 10
        for loop in range(0,loops):
            for i in range(0,self.NUM_LEDS):
                if i == self.NUM_LEDS:
                    self.set_hsv(i-1,0,0,0)
                else:
                    print(f'i is {i}')
                    self.set_rgb2(i,255,0,0)
                    if i > 0:
                        self.set_hsv(i-1,1,1,0)
                        
                print(f'i:{i}')
                
                delay = 1/ self.NUM_LEDS
                print(f'delay:{delay}')
                sleep(delay)
            
            self.set_rgb2(11,0,0,0)
            
    def rainbow_chaser(self, loops=None):
        if not loops:
            loops = 10
        
        # loop through the colors
        for loop in range(loops):
            for color in range(0,10,1):
                for led in range(self.NUM_LEDS): 
                    col = float(color / 10)
                    self.set_hsv(led, col, 1, 1)
                    print(f'color: {color}, col: {col}')
                    sleep(0.01)
                
    def disable_all(self):
        for led in range(self.NUM_LEDS):
            self.set_hsv(led, 0, 0, 0)
            
    def full_beam(self):
        for led in range(self.NUM_LEDS):
            self.set_hsv(led, 1, 0, 1)
    
    def off(self):
        self.disable_all()
        
    def flash(self, loop):
        for loops in range(loop):
            for led in range(self.NUM_LEDS):
                self.set_hsv(led, 1, 0, 1)
            sleep(0.5)
            self.off()
            sleep(0.5)
        
class Cyber_glasses():
    
    arm_position = 'down'
    led_strip = ws2812()
    
    def __init__(self):
        self.led_strip.set_rgb(0,255,0,0)
        self.led_strip.show()
        self.led_strip.fill(0,0,0)
        self.pulse()
            
    def pulse(self):
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
        for led in range(self.led_strip.NUM_LEDS):
            self.led_strip.set_rgb2(led, r, g, b)
        
glasses = Cyber_glasses()
#glasses.led_strip.rgb2hsv(255,0,0)

# glasses.led_strip.set_rgb2(1,255,255,0)

# glasses.led_strip.spin(1)
# glasses.led_strip.rainbow_chaser(10)

while True:
    glasses.light_away()
    sleep(1)
    glasses.light_down()
    sleep(0.25)
    glasses.led_strip.spin(1)
    glasses.led_strip.rainbow_chaser(2)
    sleep(1)
    glasses.led_strip.full_beam()
    sleep(2)
    glasses.led_strip.disable_all()
    glasses.light_away()