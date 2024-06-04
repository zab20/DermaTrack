import board

STATE_OFF       = 0
STATE_READY     = 1
STATE_CAPTURE   = 2

SPI_PORT   = 0
SPI_DEVICE = 0

LED_RING_PIN    = board.D12
RING_LED_COUT   = 16
RING_COLOR      = (255, 255, 255) # rgb
MIN_BRIGHTNESS = 0.01 # should be grater than 0
MAX_BRIGHTNESS = 1   # should be less or equal to 1

GREEN_LED_PIN   = 17
READY_BTN       = 27
CAPTURE_BTN     = 22
BUZZER_PIN      = 23


# image capture if person is in between these limits
# green LED will light up if person is in between these limits
# values are in mm
DISTANCE_MIN    =   80
DISTANCE_MAX    =   120

IMAGE_WIDTH  = 1280
IMAGE_HEIGHT = 720
