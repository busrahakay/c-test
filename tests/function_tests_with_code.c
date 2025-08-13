#include "get_age_category.h"

void test_get_age_category__invalid_age_negative(void) {
    TEST_ASSERT_EQUAL_STRING("Invalid", get_age_category(-1));
}

void test_get_age_category__invalid_age_above_max(void) {
    TEST_ASSERT_EQUAL_STRING("Invalid", get_age_category(121));
}

void test_get_age_category__child_min_boundary(void) {
    TEST_ASSERT_EQUAL_STRING("Child", get_age_category(0));
}

void test_get_age_category__child_max_boundary(void) {
    TEST_ASSERT_EQUAL_STRING("Child", get_age_category(12));
}

void test_get_age_category__teen_min_boundary(void) {
    TEST_ASSERT_EQUAL_STRING("Teen", get_age_category(13));
}

void test_get_age_category__teen_max_boundary(void) {
    TEST_ASSERT_EQUAL_STRING("Teen", get_age_category(19));
}

void test_get_age_category__adult_min_boundary(void) {
    TEST_ASSERT_EQUAL_STRING("Adult", get_age_category(20));
}

void test_get_age_category__adult_max_boundary(void) {
    TEST_ASSERT_EQUAL_STRING("Adult", get_age_category(64));
}

void test_get_age_category__senior_min_boundary(void) {
    TEST_ASSERT_EQUAL_STRING("Senior", get_age_category(65));
}

void test_get_age_category__senior_max_boundary(void) {
    TEST_ASSERT_EQUAL_STRING("Senior", get_age_category(120));
}