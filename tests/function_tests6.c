// Otomatik üretilmiş Black Box test suite'i
// Birden fazla fonksiyon için testler

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#include "control_led_based_on_temperature.h"
#include "mock_led.h"

void test_control_led_based_on_temperature__high_temperature(void)
{
    led_off_Expect();
    control_led_based_on_temperature(30);
    
    led_on_Expect();
    control_led_based_on_temperature(31);
}

void test_control_led_based_on_temperature__low_temperature(void)
{
    led_off_Expect();
    control_led_based_on_temperature(29);
}

void test_control_led_based_on_temperature__boundary_value(void)
{
    led_off_Expect();
    control_led_based_on_temperature(30);
    
    led_on_Expect();
    control_led_based_on_temperature(31);
}

void test_control_led_based_on_temperature__negative_temperature(void)
{
    led_off_Expect();
    control_led_based_on_temperature(-5);
}

#include "unity.h"
#include "control_led_based_on_temperature.h"
#include "mock_led.h"

void setUp(void) {}
void tearDown(void) {}

void test_control_led_based_on_temperature__led_on_above_threshold(void)
{
    led_on_Expect();
    control_led_based_on_temperature(31);
}

void test_control_led_based_on_temperature__led_off_below_threshold(void)
{
    led_off_Expect();
    control_led_based_on_temperature(30);
}

void test_control_led_based_on_temperature__led_on_at_boundary(void)
{
    led_on_Expect();
    control_led_based_on_temperature(31);
}

void test_control_led_based_on_temperature__led_off_at_boundary(void)
{
    led_off_Expect();
    control_led_based_on_temperature(30);
}

void test_control_led_based_on_temperature__led_on_extreme_high(void)
{
    led_on_Expect();
    control_led_based_on_temperature(INT_MAX);
}

void test_control_led_based_on_temperature__led_off_extreme_low(void)
{
    led_off_Expect();
    control_led_based_on_temperature(INT_MIN);
}

int main(void) {
    printf("Black Box Test Suite Başlatılıyor\n\n");
    
    test_from_llm();
    test_from_llm();
    
    printf("Tüm testler tamamlandı\n");
    return 0;
}
