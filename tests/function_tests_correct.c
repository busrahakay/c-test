#include "get_age_category.h"
#include "unity.h"

void test_get_age_category__child(void) {
    TEST_ASSERT_EQUAL_STRING("child", get_age_category(0));
    TEST_ASSERT_EQUAL_STRING("child", get_age_category(5));
    TEST_ASSERT_EQUAL_STRING("child", get_age_category(12));
}

void test_get_age_category__teenager(void) {
    TEST_ASSERT_EQUAL_STRING("teenager", get_age_category(13));
    TEST_ASSERT_EQUAL_STRING("teenager", get_age_category(15));
    TEST_ASSERT_EQUAL_STRING("teenager", get_age_category(19));
}

void test_get_age_category__adult(void) {
    TEST_ASSERT_EQUAL_STRING("adult", get_age_category(20));
    TEST_ASSERT_EQUAL_STRING("adult", get_age_category(35));
    TEST_ASSERT_EQUAL_STRING("adult", get_age_category(64));
}

void test_get_age_category__senior(void) {
    TEST_ASSERT_EQUAL_STRING("senior", get_age_category(65));
    TEST_ASSERT_EQUAL_STRING("senior", get_age_category(70));
    TEST_ASSERT_EQUAL_STRING("senior", get_age_category(100));
}

void test_get_age_category__negative_age(void) {
    TEST_ASSERT_EQUAL_STRING("invalid", get_age_category(-1));
    TEST_ASSERT_EQUAL_STRING("invalid", get_age_category(-10));
}