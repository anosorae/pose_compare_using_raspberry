#!/usr/bin/python3
#coding=utf-8

import RPi.GPIO as GPIO
import time


PWMA = 18
AIN2 = 22  # reversed because some mistake
AIN1 = 27

PWMB = 23
BIN2 = 25   # also reversed
BIN1 = 24


class Car:
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(AIN2, GPIO.OUT)
    GPIO.setup(AIN1, GPIO.OUT)
    GPIO.setup(PWMA, GPIO.OUT)

    GPIO.setup(BIN1, GPIO.OUT)
    GPIO.setup(BIN2, GPIO.OUT)
    GPIO.setup(PWMB, GPIO.OUT)
    L_Motor = GPIO.PWM(PWMA, 100)
    L_Motor.start(0)
    R_Motor = GPIO.PWM(PWMB, 100)
    R_Motor.start(0)

    def t_up(self, speed, t_time):
        self.L_Motor.ChangeDutyCycle(speed)
        GPIO.output(AIN2, False)  # AIN2
        GPIO.output(AIN1, True)  # AIN1

        self.R_Motor.ChangeDutyCycle(speed)
        GPIO.output(BIN2, False)  # BIN2
        GPIO.output(BIN1, True)  # BIN1
        time.sleep(t_time)

    def t_stop(self, t_time):
        self.L_Motor.ChangeDutyCycle(0)
        GPIO.output(AIN2, False)  # AIN2
        GPIO.output(AIN1, False)  # AIN1

        self.R_Motor.ChangeDutyCycle(0)
        GPIO.output(BIN2, False)  # BIN2
        GPIO.output(BIN1, False)  # BIN1
        time.sleep(t_time)

    def t_down(self, speed, t_time):
        self.L_Motor.ChangeDutyCycle(speed)
        GPIO.output(AIN2, True)  # AIN2
        GPIO.output(AIN1, False)  # AIN1

        self.R_Motor.ChangeDutyCycle(speed)
        GPIO.output(BIN2, True)  # BIN2
        GPIO.output(BIN1, False)  # BIN1
        time.sleep(t_time)

    def t_left(self, speed, t_time):
        self.L_Motor.ChangeDutyCycle(speed)
        GPIO.output(AIN2, True)  # AIN2
        GPIO.output(AIN1, False)  # AIN1

        self.R_Motor.ChangeDutyCycle(speed)
        GPIO.output(BIN2, False)  # BIN2
        GPIO.output(BIN1, True)  # BIN1
        time.sleep(t_time)

    def t_right(self, speed, t_time):
        self.L_Motor.ChangeDutyCycle(speed)
        GPIO.output(AIN2, False)  # AIN2
        GPIO.output(AIN1, True)  # AIN1

        self.R_Motor.ChangeDutyCycle(speed)
        GPIO.output(BIN2, True)  # BIN2
        GPIO.output(BIN1, False)  # BIN1
        time.sleep(t_time)

