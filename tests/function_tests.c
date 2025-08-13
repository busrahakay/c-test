```c
#include "unity.h"
#include "yaşı.h"

void setUp(void) {}
void tearDown(void) {}

void test_yaşı__negatif_yas(void) {
    TEST_ASSERT_EQUAL_STRING("Geçersiz yaş", yaşı(-1));
}

void test_yaşı__sifir_yas(void) {
    TEST_ASSERT_EQUAL_STRING("Bebek", yaşı(0));
}

void test_yaşı__bebek_alt_sinir(void) {
    TEST_ASSERT_EQUAL_STRING("Bebek", yaşı(1));
}

void test_yaşı__bebek_ust_sinir(void) {
    TEST_ASSERT_EQUAL_STRING("Bebek", yaşı(3));
}

void test_yaşı__cocuk_alt_sinir(void) {
    TEST_ASSERT_EQUAL_STRING("Çocuk", yaşı(4));
}

void test_yaşı__cocuk_ust_sinir(void) {
    TEST_ASSERT_EQUAL_STRING("Çocuk", yaşı(12));
}

void test_yaşı__genc_alt_sinir(void) {
    TEST_ASSERT_EQUAL_STRING("Genç", yaşı(13));
}

void test_yaşı__genc_ust_sinir(void) {
    TEST_ASSERT_EQUAL_STRING("Genç", yaşı(19));
}

void test_yaşı__yetişkin_alt_sinir(void) {
    TEST_ASSERT_EQUAL_STRING("Yetişkin", yaşı(20));
}

void test_yaşı__yetişkin_ust_sinir(void) {
    TEST_ASSERT_EQUAL_STRING("Yetişkin", yaşı(64));
}

void test_yaşı__yasli_alt_sinir(void) {
    TEST_ASSERT_EQUAL_STRING("Yaşlı", yaşı(65));
}

void test_yaşı__yasli_ust_sinir(void) {
    TEST_ASSERT_EQUAL_STRING("Yaşlı", yaşı(120));
}

void test_yaşı__asiri_yasli(void) {
    TEST_ASSERT_EQUAL_STRING("Geçersiz yaş", yaşı(121));
}
```