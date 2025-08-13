#include "unity.h"
#include "age.h"

void test_age__infant(void) {
    TEST_ASSERT_EQUAL_STRING("Infant", age(0));
    TEST_ASSERT_EQUAL_STRING("Infant", age(1));
}

void test_age__child(void) {
    TEST_ASSERT_EQUAL_STRING("Child", age(2));
    TEST_ASSERT_EQUAL_STRING("Child", age(12));
}

void test_age__teenager(void) {
    TEST_ASSERT_EQUAL_STRING("Teenager", age(13));
    TEST_ASSERT_EQUAL_STRING("Teenager", age(19));
}

void test_age__adult(void) {
    TEST_ASSERT_EQUAL_STRING("Adult", age(20));
    TEST_ASSERT_EQUAL_STRING("Adult", age(64));
}

void test_age__senior(void) {
    TEST_ASSERT_EQUAL_STRING("Senior", age(65));
    TEST_ASSERT_EQUAL_STRING("Senior", age(100));
}

void test_age__negative(void) {
    TEST_ASSERT_NULL(age(-1));
    TEST_ASSERT_NULL(age(-100));
}