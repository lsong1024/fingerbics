from picamera2 import Picamera2, Preview
import requests
from io import BytesIO
from time import sleep
import time
import RPi.GPIO as GPIO

RED_LED_PIN = 18
GREEN_LED_PIN = 12
YELLOW_LED_PIN = 13

GPIO.setmode(GPIO.BCM)
GPIO.setup(RED_LED_PIN, GPIO.OUT)
GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
GPIO.setup(YELLOW_LED_PIN, GPIO.OUT)

camera = Picamera2()
camera.configure()
camera.start_preview(Preview.QT)
camera.start()

start_time_all = time.time()
success_count1 = success_count2 = success_count3 = 0
stage = 1
success_signal = False
success_signal_1 = False
success_signal_2 = False

while time.time() - start_time_all < 90:

    image_stream = BytesIO()
    camera.capture_file(image_stream, format='jpeg')
    image_data = image_stream.getvalue()

    url = "http://192.168.50.87:8001/upload-image"
    response = requests.post(url, files={'file': ('image.jpg', image_data, 'image/jpeg')})

    predictions = response.json().get("predictions")
    label1 = predictions['label1']
    label2 = predictions['label2']

    if predictions and stage == 1:
        GPIO.output(RED_LED_PIN, GPIO.HIGH)
        GPIO.output(GREEN_LED_PIN, GPIO.LOW)
        GPIO.output(YELLOW_LED_PIN, GPIO.LOW)

        if label1 == 1 and label2 == 1:
            if not success_signal:
                success_signal = True

        else:
            if success_signal:
                success_count1 += 1
                success_signal = False

                if success_count1 > 2:
                    stage += 1


    elif predictions and stage == 2:
        GPIO.output(RED_LED_PIN, GPIO.LOW)
        GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
        GPIO.output(YELLOW_LED_PIN, GPIO.LOW)

        if (label1 == 0 and label2 == 1) or (label1 == 1 and label2 == 0):
            if not success_signal:
                success_signal = True
        else:
            if success_signal:
                success_count2 += 1
                success_signal = False

                if success_count2 > 2:
                    stage += 1

    elif predictions and stage == 3:
        GPIO.output(RED_LED_PIN, GPIO.LOW)
        GPIO.output(GREEN_LED_PIN, GPIO.LOW)
        GPIO.output(YELLOW_LED_PIN, GPIO.HIGH)

        if (label1 == 2 or label1 == 3) and (label2 == 2 or label2 == 3):
            if not success_signal:
                success_signal = True

        elif (label1 == 4 or label1 == 5) and (label2 == 4 or label2 == 5):
            if success_signal:
                success_signal_1 = True

        elif label1 == 0 and label2 == 0:
            if success_signal_1:
                success_signal_2 = True

        else:
            if success_signal_2:
                success_count3 += 1
                success_signal = False
                success_signal_1 = False
                success_signal_2 = False
                if success_count3 > 2:
                    GPIO.output(RED_LED_PIN, GPIO.HIGH)
                    GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
                    GPIO.output(YELLOW_LED_PIN, GPIO.HIGH)
                    sleep(1)
                    break

GPIO.output(RED_LED_PIN, GPIO.LOW)
GPIO.output(GREEN_LED_PIN, GPIO.LOW)
GPIO.output(YELLOW_LED_PIN, GPIO.LOW)

print(success_count1, success_count2, success_count3, start_time_all)

url = "http://192.168.50.87:8001/upload-results"
result_payload = {
    "count1": success_count1,
    "count2": success_count2,
    "count3": success_count3,
    "start_time": start_time_all
}
requests.post(url, json=result_payload)

camera.stop()
camera.close()


