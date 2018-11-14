#include <Arduino.h>
#include <Constants.h>

inline void moveStepsConstantAcceleration(uint32_t steps, double &dt_prev, double a){
    double hpd = 1E6 * dt_prev / 2;
    for (uint32_t step = 0; step < steps; step++)
        {
            PORTD |= 0x04; //sets pulse pin to high
            delayMicroseconds(hpd);
            PORTD &= ~(0x04);
            unsigned long m0 = micros();
            bool new_loop = true;
            while ((micros() - m0) < hpd)
            {
                if (new_loop)
                {
                    dt_prev = dt_prev / (1.0 + (8.0 * a * dt_prev * dt_prev));
                    hpd = 1E6 * dt_prev / 2;
                    new_loop = false;
                }
            }
            new_loop = true;
        }
}
inline void moveSteps(uint32_t steps, uint8_t direction){
    digitalWrite(DIR_PIN, direction);
    double dt_prev = INITIAL_DT;
    moveStepsConstantAcceleration(steps/2, dt_prev, ACCELERATION);
    moveStepsConstantAcceleration(steps/2, dt_prev, -ACCELERATION);
}

void setup()
{
    Serial.begin(115200);
    DDRD = DDRD | B10010100; //Pins 2, 4, and 7 are outputs
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
    if(command == AGITATE){
        digitalWrite(ENA_PIN, HIGH);
        moveSteps(STEPS_WASH_RANGE, HIGH); //Stage mount inverted
        moveSteps(STEPS_WASH_RANGE, LOW);
        digitalWrite(ENA_PIN, LOW);
    }

    else if(command == SUBMERGE){
        digitalWrite(ENA_PIN, HIGH);
        moveSteps(STEPS_SUBMERGE, HIGH); //Stage mount inverted
        digitalWrite(ENA_PIN, LOW);
    }
    else if(command == RAISE){
        digitalWrite(ENA_PIN, HIGH);
        moveSteps(STEPS_SUBMERGE, LOW);//Stage mount inverted
        digitalWrite(ENA_PIN, LOW);
    }

    else if(command == DATA_WRITE){
        while (Serial.available() < 1)
        {
        }
        uint8_t byte_lower = Serial.read();
        while (Serial.available() < 1)
        {
        }
        uint8_t byte_higher = Serial.read();
        D_WASH_RANGE = 0x0000 | byte_lower;
        D_WASH_RANGE |= (byte_higher << 8);

        while (Serial.available() < 1)
        {
        }
        uint8_t acceleration_lower = Serial.read();
        while (Serial.available() < 1)
        {
        }
        uint8_t acceleration_higher = Serial.read();        
        uint8_t acceleration = 0x0000 | acceleration_lower;
        ACCELERATION = static_cast<double>(acceleration | (acceleration_higher << 8));

        while (Serial.available() < 1)
        {
        }
        byte_lower = Serial.read();
        while (Serial.available() < 1)
        {
        }
        byte_higher = Serial.read();
        D_SUBMERGE = 0x0000 | byte_lower;
        D_SUBMERGE |= (byte_higher << 8);
        
        STEPS_SUBMERGE = D_SUBMERGE * STEPS_PER_DU;
        STEPS_WASH_RANGE = D_WASH_RANGE * STEPS_PER_DU; 
    }
    Serial.write(0x01);
}
