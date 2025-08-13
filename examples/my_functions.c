/**
 * @file led_controller.c
 * @brief Controls an LED based on the temperature value.
 *
 * This module controls the LED state depending on the current temperature.
 * Hardware access is abstracted through the led_driver interface.
 * 
 * The core logic is separated to allow Black Box testing.
 */

 #include "led_driver.h"

 /**
  * @brief Determines the LED state based on the temperature.
  *
  * Returns 1 if the temperature is above 30°C (LED should be ON),
  * or 0 otherwise (LED should be OFF).
  * 
  * This pure function allows Black Box testing independent of hardware.
  *
  * @param temperature The temperature value in degrees Celsius.
  * @return int 1 if LED should be on, 0 if off
  */
 int get_led_state_based_on_temperature(int temperature) {
     return (temperature > 30) ? 1 : 0;
 }
 
 /**
  * @brief Controls the LED based on the temperature value.
  *
  * This function calls hardware-specific LED functions based on
  * the logic determined by `get_led_state_based_on_temperature`.
  *
  * @param temperature The temperature value in degrees Celsius.
  */
 void control_led_based_on_temperature(int temperature) {
     if (get_led_state_based_on_temperature(temperature)) {
         led_on();
     } else {
         led_off();
     }
 }
 