#include "unity.h"
#include "yaşı.h"

void setUp(void) {}
void tearDown(void) {}

void test_yaşı__0_yaş(void) {
    TEST_ASSERT_EQUAL_STRING("Bebek", yaşı(0));
}

void test_yaşı__1_yaş(void) {
    TEST_ASSERT_EQUAL_STRING("Bebek", yaşı(1));
}

void test_yaşı__2_yaş(void) {
    TEST_ASSERT_EQUAL_STRING("Bebek", yaşı(2));
}

void test_yaşı__3_yaş(void) {
    TEST_ASSERT_EQUAL_STRING("Çocuk", yaşı(3));
}

void test_yaşı__12_yaş(void) {
    TEST_ASSERT_EQUAL_STRING("Çocuk", yaşı(12));
}

void test_yaşı__13_yaş(void) {
    TEST_ASSERT_EQUAL_STRING("Genç", yaşı(13));
}

void test_yaşı__19_yaş(void) {
    TEST_ASSERT_EQUAL_STRING("Genç", yaşı(19));
}

void test_yaşı__20_yaş(void) {
    TEST_ASSERT_EQUAL_STRING("Yetişkin", yaşı(20));
}

void test_yaşı__64_yaş(void) {
    TEST_ASSERT_EQUAL_STRING("Yetişkin", yaşı(64));
}

void test_yaşı__65_yaş(void) {
    TEST_ASSERT_EQUAL_STRING("Yaşlı", yaşı(65));
}

void test_yaşı__120_yaş(void) {
    TEST_ASSERT_EQUAL_STRING("Yaşlı", yaşı(120));
}

void test_yaşı__negatif_yaş(void) {
    TEST_ASSERT_NULL(yaşı(-1));
}

void test_yaşı__çok_büyük_yaş(void) {
    TEST_ASSERT_NULL(yaşı(121));
}