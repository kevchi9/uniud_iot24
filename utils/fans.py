#!/usr/bin/env python3

import RPi.GPIO as GPIO
from gpiozero import CPUTemperature
from time import sleep

ther = CPUTemperature()
fan1 = 6
fan2 = 13

GPIO.setmode(GPIO.BCM)
GPIO.setup(fan1, GPIO.OUT)
GPIO.setup(fan2, GPIO.OUT)

pi_pwm6 = GPIO.PWM(fan1, 220)
pi_pwm13 = GPIO.PWM(fan2, 220)
pi_pwm6.start(0)
pi_pwm13.start(0)

try:
    while True:
        if (ther.temperature >= 65):
            pi_pwm6.ChangeDutyCycle(100)
            pi_pwm13.ChangeDutyCycle(100)
        elif (ther.temperature >= 57):
            pi_pwm6.ChangeDutyCycle(70)
            pi_pwm13.ChangeDutyCycle(70)
        else:
            pi_pwm6.ChangeDutyCycle(0)
            pi_pwm13.ChangeDutyCycle(0)
        sleep(2)
except KeyboardInterrupt:
    pass
pi_pwm6.stop()
pi_pwm13.stop()
GPIO.cleanup()
