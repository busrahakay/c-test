// Otomatik üretilmiş Black Box test suite'i
// Birden fazla fonksiyon için testler

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#include "unity.h"
#include "add.h"

void test_add__positive_numbers(void) {
    TEST_ASSERT_EQUAL_INT(5, add(2, 3));
}

void test_add__negative_numbers(void) {
    TEST_ASSERT_EQUAL_INT(-2, add(-5, 3));
}

void test_add__zero_values(void) {
    TEST_ASSERT_EQUAL_INT(0, add(0, 0));
}

void test_add__positive_negative_boundary(void) {
    TEST_ASSERT_EQUAL_INT(0, add(INT_MAX, INT_MIN));
}

void test_add__max_positive_values(void) {
    TEST_ASSERT_EQUAL_INT(-2, add(INT_MAX, INT_MAX));
}

void test_add__min_negative_values(void) {
    TEST_ASSERT_EQUAL_INT(0, add(INT_MIN, INT_MIN));
}

void test_add__large_positive_numbers(void) {
    TEST_ASSERT_EQUAL_INT(2147483646, add(1073741823, 1073741823));
}

void test_add__large_negative_numbers(void) {
    TEST_ASSERT_EQUAL_INT(-2147483646, add(-1073741823, -1073741823));
}

```c
#include "unity.h"
#include "add.h"

void test_add__positive_numbers(void) {
    TEST_ASSERT_EQUAL_INT(5, add(2, 3));
}

void test_add__negative_numbers(void) {
    TEST_ASSERT_EQUAL_INT(-5, add(-2, -3));
}

void test_add__mixed_sign_numbers(void) {
    TEST_ASSERT_EQUAL_INT(1, add(4, -3));
}

void test_add__zero_values(void) {
    TEST_ASSERT_EQUAL_INT(0, add(0, 0));
}

void test_add__max_int_values(void) {
    TEST_ASSERT_EQUAL_INT(INT_MAX, add(INT_MAX, 0));
}

void test_add__min_int_values(void) {
    TEST_ASSERT_EQUAL_INT(INT_MIN, add(INT_MIN, 0));
}

void test_add__max_int_overflow(void) {
    TEST_ASSERT_EQUAL_INT(INT_MIN, add(INT_MAX, 1));
}

void test_add__min_int_underflow(void) {
    TEST_ASSERT_EQUAL_INT(INT_MAX, add(INT_MIN, -1));
}
```

int main(void) {
    printf("Black Box Test Suite Başlatılıyor\n\n");
    
    test_from_llm();
    test_from_llm();
    
    printf("Tüm testler tamamlandı\n");
    return 0;
}
