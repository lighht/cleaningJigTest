/****** MOTION PROFILE PARAMS **********/
const double INITIAL_DT = 10.0 / 8.00; //Translates to 1mm per second. This is the lowest speed. 

/****** OVERWRITTEN BY GUI *************/

uint16_t D_SUBMERGE = 2000; //Set to 20mm... Change according to need. Max for any distance is 65535DU = 655mm.
uint16_t D_WASH_RANGE = 1500; //All distances are in DU. 1DU=10 microns.
double ACCELERATION = 500;//DU per second per second

/******COMMAND LIST*******************/
const uint8_t ENABLE_MOTOR = 0x00;
const uint8_t DISABLE_MOTOR = 0x01;
const uint8_t SUBMERGE = 0x02;
const uint8_t RAISE = 0x03;
const uint8_t AGITATE = 0x04;
const uint8_t DATA_WRITE = 0x05;

/****MOTOR CONSTANTS**********/
const uint16_t STEPS_PER_REV = 1600;            // Steps per revolution set on the driver
const uint16_t DU_PER_REV = 200;                //2mm per revolution

/*******HARDWARE CONSTANTS************/
const uint8_t PULSE_PIN = 2;
const uint8_t DIR_PIN = 4;
const uint8_t ENA_PIN = 7;
const uint8_t OPTO_PIN = 8;
const uint8_t ADDRESS = 0x1A;
//HPD  is half pulse duration
 
/******DERIVED CONSTANTS************/

const uint8_t STEPS_PER_DU = STEPS_PER_REV/DU_PER_REV;
//Moves 2mm for 1600 steps. 1.25 microns per step. 8 steps per DU
uint32_t STEPS_SUBMERGE = D_SUBMERGE * STEPS_PER_DU; //The first value in du. 
                                                 
uint32_t STEPS_WASH_RANGE = D_WASH_RANGE * STEPS_PER_DU; 