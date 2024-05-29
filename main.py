import neopixel, sys
from time import sleep
from constants import *
import Adafruit_MCP3008
import RPi.GPIO as GPIO
from datetime import datetime
import adafruit_vl53l0x, busio
import Adafruit_GPIO.SPI as SPI
from picamera2 import Picamera2
from os.path import dirname, abspath


DIR = dirname(abspath(sys.argv[0])) + '/Images/'

initialized = False
deviceState = STATE_OFF

ringLight = None
adc = None
tof = None

if (MIN_BRIGHTNESS <= 0):
    MIN_BRIGHTNESS = 0.1
if (MAX_BRIGHTNESS > 1):
    MAX_BRIGHTNESS = 1

brightness = MIN_BRIGHTNESS

camera = None

'''
    press button turn on external button to turn on RPi

    press button ready
    press button image capture
'''

def map(x: int, inLow: int, inHigh: int, outLow: int, outHigh: int) -> float:
  if inLow == inHigh:
    return outLow
  elif inLow > inHigh:
    inLow, inHigh = inHigh, inLow

  inRange = inHigh - inLow
  proportion = (x - inLow) / inRange
  out_range = outHigh - outLow
  return round((outLow + (proportion * out_range)), 2)


def resetEverything(resetCamera=False) -> None:
    global deviceState
    deviceState = STATE_OFF
    GPIO.output(GREEN_LED_PIN, GPIO.LOW)
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    if(ringLight):
        for i in range(RING_LED_COUT):
            ringLight[i] = 0
    if(camera and resetCamera):
        camera.stop()


def doExit() -> None:
    print('Exiting gracefully')
    resetEverything(True)
    exit()


def initializeSystem() -> None:
    print('Initializing...')
    global initialized, ringLight, adc, camera, tof
    if(not initialized):
        try:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)

            GPIO.setup(CAPTURE_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(READY_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
            GPIO.setup(BUZZER_PIN, GPIO.OUT)

            ringLight = neopixel.NeoPixel(LED_RING_PIN, RING_LED_COUT, brightness=brightness)
            adc = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
            print("ADC initialized")
            sleep(1)
            i2c = busio.I2C(board.SCL, board.SDA)
            tof = adafruit_vl53l0x.VL53L0X(i2c)
            tof.measurement_timing_budget = 200000
            print("Distance sensor initialized")
            sleep(1)
            camera = Picamera2()
            config = camera.create_still_configuration(main={"size": (IMAGE_WIDTH, IMAGE_HEIGHT)})
            camera.configure(config)
            camera.start()
            initialized = True

            resetEverything(False)
            print('Initialized')
        except Exception as e:
            print(e)
            print('Unable to initialize')
            resetEverything(True)
            print('Exiting...')
            exit()


def watchToF() -> bool:
    dist = tof.range

    if(dist > DISTANCE_MIN and dist < DISTANCE_MAX):
        GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        return True
    else:
        GPIO.output(GREEN_LED_PIN, GPIO.LOW)
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
    
    # if(dist <= DISTANCE_MIN):
    #     GPIO.output(BUZZER_PIN, GPIO.HIGH)
    # else:
    #     GPIO.output(BUZZER_PIN, GPIO.LOW)
    return False


def capture() -> None:
    if(watchToF()):
        global deviceState
        filename = DIR + datetime.now().strftime("%Y-%m-%d_%H-%M-%S_image.jpg")
        camera.capture_file(filename)
        deviceState = STATE_OFF
        GPIO.output(GREEN_LED_PIN, GPIO.LOW)
        ringLight.fill(0)
        ringLight.show()
        print('Image captured')
    else:
        print('Image capture failed. User not in range')


def readButtons() -> None:
    global deviceState
    if(deviceState == STATE_OFF):
        if(GPIO.input(READY_BTN)):
            deviceState = STATE_READY
            ringLight.fill(RING_COLOR)
            ringLight.show()
            print('Device Ready')
    elif(deviceState == STATE_READY):
        if(GPIO.input(CAPTURE_BTN)):
            capture()


def updateADC() -> bool:
    global brightness
    value = adc.read_adc(0)
    currentBrightness = map(value,0,1024,MIN_BRIGHTNESS,MAX_BRIGHTNESS)
    if(currentBrightness != brightness):
        brightness = currentBrightness
        print('Ring brightness: ', brightness)
        return True
    return False


def updateRingLight() -> None:
    if(deviceState != STATE_READY):
        return
    if(updateADC()):
        ringLight.brightness = brightness


def main() -> None:
    try:
        initializeSystem()
        if(initialized):
            while (True):
                readButtons()
                updateRingLight()
                if(deviceState == STATE_READY):
                    watchToF()
                sleep(0.1)
    except KeyboardInterrupt:
        doExit()
    except Exception as e:
        print(e)
        doExit()


if __name__ == '__main__':
    main()