// Otomatik üretilmiş Black Box test suite'i
// Birden fazla fonksiyon için testler

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#include "get_led_state_based_on_temperature.h"
#include "unity.h"

void test_get_led_state_based_on_temperature__below_threshold(void)
{
    TEST_ASSERT_EQUAL_INT(0, get_led_state_based_on_temperature(30));
    TEST_ASSERT_EQUAL_INT(0, get_led_state_based_on_temperature(0));
    TEST_ASSERT_EQUAL_INT(0, get_led_state_based_on_temperature(-273));
}

void test_get_led_state_based_on_temperature__above_threshold(void)
{
    TEST_ASSERT_EQUAL_INT(1, get_led_state_based_on_temperature(31));
    TEST_ASSERT_EQUAL_INT(1, get_led_state_based_on_temperature(100));
    TEST_ASSERT_EQUAL_INT(1, get_led_state_based_on_temperature(INT_MAX));
}

void test_get_led_state_based_on_temperature__boundary_value(void)
{
    TEST_ASSERT_EQUAL_INT(0, get_led_state_based_on_temperature(30));
    TEST_ASSERT_EQUAL_INT(1, get_led_state_based_on_temperature(31));
}

#include "get_led_state_based_on_temperature.h"
#include "unity.h"

void test_get_led_state_based_on_temperature__temperature_below_threshold(void) {
    TEST_ASSERT_EQUAL_INT(0, get_led_state_based_on_temperature(30));
    TEST_ASSERT_EQUAL_INT(0, get_led_state_based_on_temperature(29));
    TEST_ASSERT_EQUAL_INT(0, get_led_state_based_on_temperature(0));
    TEST_ASSERT_EQUAL_INT(0, get_led_state_based_on_temperature(-10));
}

void test_get_led_state_based_on_temperature__temperature_above_threshold(void) {
    TEST_ASSERT_EQUAL_INT(1, get_led_state_based_on_temperature(31));
    TEST_ASSERT_EQUAL_INT(1, get_led_state_based_on_temperature(40));
    TEST_ASSERT_EQUAL_INT(1, get_led_state_based_on_temperature(100));
}

void test_get_led_state_based_on_temperature__boundary_value(void) {
    TEST_ASSERT_EQUAL_INT(0, get_led_state_based_on_temperature(30));
    TEST_ASSERT_EQUAL_INT(1, get_led_state_based_on_temperature(31));
}

#include "control_led_based_on_temperature.h"
#include "mock_led.h"
#include "mock_get_led_state_based_on_temperature.h"

void test_control_led_based_on_temperature__led_state_true_turns_on(void)
{
    get_led_state_based_on_temperature_ExpectAndReturn(25, true);
    led_on_Expect();
    control_led_based_on_temperature(25);
}

void test_control_led_based_on_temperature__led_state_false_turns_off(void)
{
    get_led_state_based_on_temperature_ExpectAndReturn(15, false);
    led_off_Expect();
    control_led_based_on_temperature(15);
}

void test_control_led_based_on_temperature__minimum_int_value(void)
{
    get_led_state_based_on_temperature_ExpectAndReturn(INT_MIN, false);
    led_off_Expect();
    control_led_based_on_temperature(INT_MIN);
}

void test_control_led_based_on_temperature__maximum_int_value(void)
{
    get_led_state_based_on_temperature_ExpectAndReturn(INT_MAX, false);
    led_off_Expect();
    control_led_based_on_temperature(INT_MAX);
}

void test_control_led_based_on_temperature__zero_value(void)
{
    get_led_state_based_on_temperature_ExpectAndReturn(0, false);
    led_off_Expect();
    control_led_based_on_temperature(0);
}

void test_control_led_based_on_temperature__negative_value(void)
{
    get_led_state_based_on_temperature_ExpectAndReturn(-10, false);
    led_off_Expect();
    control_led_based_on_temperature(-10);
}

void test_control_led_based_on_temperature__positive_value(void)
{
    get_led_state_based_on_temperature_ExpectAndReturn(30, true);
    led_on_Expect();
    control_led_based_on_temperature(30);
}

int main(void) {
    printf("Black Box Test Suite Başlatılıyor\n\n");
    
    test_from_llm();
    test_from_llm();
    test_from_llm();
    
    printf("Tüm testler tamamlandı\n");
    return 0;
}
