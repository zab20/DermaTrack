import time

from picamera2 import Picamera2, Preview

picam2 = Picamera2()
picam2.start_preview(Preview.QTGL)
preview_config = picam2.create_preview_configuration(main={"size": (1536, 864)})
capture_config = picam2.create_still_configuration(main={"size": (1536, 864)})

picam2.configure(preview_config)
picam2.start()
time.sleep(3)

#image = picam2.capture_file('test.jpg')
image = picam2.switch_mode_and_capture_image(capture_config)
image.show()


time.sleep(5)

picam2.close()