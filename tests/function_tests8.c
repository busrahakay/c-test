// Otomatik üretilmiş Black Box test suite'i
// Birden fazla fonksiyon için testler

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#include "get_led_state_based_on_temperature.h"

void test_get_led_state_based_on_temperature__below_threshold(void)
{
    TEST_ASSERT_EQUAL_INT(0, get_led_state_based_on_temperature(30));
}

void test_get_led_state_based_on_temperature__above_threshold(void)
{
    TEST_ASSERT_EQUAL_INT(1, get_led_state_based_on_temperature(31));
}

void test_get_led_state_based_on_temperature__threshold_boundary(void)
{
    TEST_ASSERT_EQUAL_INT(0, get_led_state_based_on_temperature(30));
    TEST_ASSERT_EQUAL_INT(1, get_led_state_based_on_temperature(31));
}

void test_get_led_state_based_on_temperature__minimum_value(void)
{
    TEST_ASSERT_EQUAL_INT(0, get_led_state_based_on_temperature(INT_MIN));
}

void test_get_led_state_based_on_temperature__maximum_value(void)
{
    TEST_ASSERT_EQUAL_INT(1, get_led_state_based_on_temperature(INT_MAX));
}

#include "get_led_state_based_on_temperature.h"

void test_get_led_state_based_on_temperature__below_threshold(void)
{
    TEST_ASSERT_EQUAL_INT(0, get_led_state_based_on_temperature(29));
    TEST_ASSERT_EQUAL_INT(0, get_led_state_based_on_temperature(30));
}

void test_get_led_state_based_on_temperature__above_threshold(void)
{
    TEST_ASSERT_EQUAL_INT(1, get_led_state_based_on_temperature(31));
    TEST_ASSERT_EQUAL_INT(1, get_led_state_based_on_temperature(100));
}

void test_get_led_state_based_on_temperature__boundary_value(void)
{
    TEST_ASSERT_EQUAL_INT(0, get_led_state_based_on_temperature(30));
    TEST_ASSERT_EQUAL_INT(1, get_led_state_based_on_temperature(31));
}

#include "control_led_based_on_temperature.h"
#include "mock_led.h"
#include "mock_get_led_state_based_on_temperature.h"

void test_control_led_based_on_temperature__led_on_when_get_led_state_true(void)
{
    get_led_state_based_on_temperature_ExpectAndReturn(25, true);
    led_on_Expect();
    control_led_based_on_temperature(25);
}

void test_control_led_based_on_temperature__led_off_when_get_led_state_false(void)
{
    get_led_state_based_on_temperature_ExpectAndReturn(15, false);
    led_off_Expect();
    control_led_based_on_temperature(15);
}

int main(void) {
    printf("Black Box Test Suite Başlatılıyor\n\n");
    
    test_from_llm();
    test_from_llm();
    test_from_llm();
    
    printf("Tüm testler tamamlandı\n");
    return 0;
}
