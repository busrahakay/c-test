#include "unity.h"
#include "age.h"

void test_age__child(void) {
    TEST_ASSERT_EQUAL_STRING("Child", age(0));
    TEST_ASSERT_EQUAL_STRING("Child", age(5));
    TEST_ASSERT_EQUAL_STRING("Child", age(12));
}

void test_age__teenager(void) {
    TEST_ASSERT_EQUAL_STRING("Teenager", age(13));
    TEST_ASSERT_EQUAL_STRING("Teenager", age(15));
    TEST_ASSERT_EQUAL_STRING("Teenager", age(19));
}

void test_age__adult(void) {
    TEST_ASSERT_EQUAL_STRING("Adult", age(20));
    TEST_ASSERT_EQUAL_STRING("Adult", age(35));
    TEST_ASSERT_EQUAL_STRING("Adult", age(64));
}

void test_age__senior(void) {
    TEST_ASSERT_EQUAL_STRING("Senior", age(65));
    TEST_ASSERT_EQUAL_STRING("Senior", age(70));
    TEST_ASSERT_EQUAL_STRING("Senior", age(120));
}

void test_age__invalid_negative(void) {
    TEST_ASSERT_EQUAL_STRING("Invalid", age(-1));
    TEST_ASSERT_EQUAL_STRING("Invalid", age(-100));
}

void test_age__boundary_values(void) {
    TEST_ASSERT_EQUAL_STRING("Child", age(12));
    TEST_ASSERT_EQUAL_STRING("Teenager", age(13));
    TEST_ASSERT_EQUAL_STRING("Teenager", age(19));
    TEST_ASSERT_EQUAL_STRING("Adult", age(20));
    TEST_ASSERT_EQUAL_STRING("Adult", age(64));
    TEST_ASSERT_EQUAL_STRING("Senior", age(65));
}