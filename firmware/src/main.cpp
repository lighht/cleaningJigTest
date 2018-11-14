
#include <Arduino.h>
/******PRINTING PARAMS****************/

uint16_t V_SLOW_SEP = 5; //mm per second - UP speed
uint16_t V_SLOW_RET = 10; // Down Speed


/******COMMAND LIST*******************/
const uint8_t ENABLE_MOTOR = 0x00;
const uint8_t MOVE_UP = 0x01;
const uint8_t MOVE_DOWN = 0x02;
const uint8_t DISABLE_MOTOR = 0x03;

/****MOTOR CONSTANTS**********/
const uint16_t STEPS_PER_REV = 1600;          // Steps per revolution set on the driver
const uint16_t PULSE_DURATION_1REV_PS = 624U; //if we need 1rev per second.
const uint16_t HALF_PULSE_DURATION_1REV_PS = 312U;
const uint16_t MULTIPLIER_DIST_10um_TO_STEPS = 8;
const double MULTIPLIER_SPEED_1mmps_REVPS = 0.5;
//Moves 2mm for 1600 steps. 1.25 microns per step


uint16_t HPD_SLOW_SEP = HALF_PULSE_DURATION_1REV_PS / (V_SLOW_SEP * MULTIPLIER_SPEED_1mmps_REVPS);
uint16_t HPD_SLOW_RET = HALF_PULSE_DURATION_1REV_PS / (V_SLOW_RET * MULTIPLIER_SPEED_1mmps_REVPS);
uint32_t HPD_LOW_LIM = HALF_PULSE_DURATION_1REV_PS * 2;

/*******HARDWARE CONSTANTS************/
const uint8_t PULSE_PIN = 2;
const uint8_t DIR_PIN = 4;
const uint8_t OPTO_PIN = 8;
const uint8_t ENA_PIN = 7;
const uint8_t ADDRESS = 0x1A;

void setup()
{
    Serial.begin(115200);
    DDRD = DDRD | B10010100; //Pins 2, 4, and 8 are outputs
    DDRB = DDRB | B00000001; //Pin 8 is output
    digitalWrite(OPTO_PIN, HIGH);
    digitalWrite(ENA_PIN, LOW);
}

void loop()
{
    while (Serial.available() < 1)
    {
    }
    uint8_t command = Serial.read();
    if (MOVE_UP == command)
    {
        digitalWrite(ENA_PIN, HIGH);
        digitalWrite(DIR_PIN, HIGH);
        while (Serial.available() < 1)
        {
            PORTD |= 0x04; //sets pulse pin to high
            delayMicroseconds(HPD_SLOW_SEP);
            PORTD &= ~(0x04);
            delayMicroseconds(HPD_SLOW_SEP);
        }
        digitalWrite(ENA_PIN, LOW);
    }
    else if (MOVE_DOWN == command)
    {
        digitalWrite(ENA_PIN, HIGH);
        digitalWrite(DIR_PIN, LOW);
        while (Serial.available() < 1)
        {
            PORTD |= 0x04; //sets pulse pin to high
            delayMicroseconds(HPD_SLOW_RET);
            PORTD &= ~(0x04);
            delayMicroseconds(HPD_SLOW_RET);
        }
        digitalWrite(ENA_PIN, LOW);
    }
    else if (ENABLE_MOTOR == command)
    {
        digitalWrite(ENA_PIN, HIGH);
    }
    else if (DISABLE_MOTOR == command)
    {
        digitalWrite(ENA_PIN, LOW);
    }
    Serial.write(0x01);
}