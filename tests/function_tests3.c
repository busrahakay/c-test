```c
#include "unity.h"
#include "unity_fixture.h"
#include "yasi.h"

TEST_GROUP(yasi);

TEST_SETUP(yasi)
{
}

TEST_TEAR_DOWN(yasi)
{
}

TEST(yasi, test_yasi__bebek_kategori)
{
    TEST_ASSERT_EQUAL_STRING("Bebek", yasi(0));
    TEST_ASSERT_EQUAL_STRING("Bebek", yasi(2));
    TEST_ASSERT_EQUAL_STRING("Bebek", yasi(3));
}

TEST(yasi, test_yasi__cocuk_kategori)
{
    TEST_ASSERT_EQUAL_STRING("Cocuk", yasi(4));
    TEST_ASSERT_EQUAL_STRING("Cocuk", yasi(7));
    TEST_ASSERT_EQUAL_STRING("Cocuk", yasi(12));
}

TEST(yasi, test_yasi__ergen_kategori)
{
    TEST_ASSERT_EQUAL_STRING("Ergen", yasi(13));
    TEST_ASSERT_EQUAL_STRING("Ergen", yasi(16));
    TEST_ASSERT_EQUAL_STRING("Ergen", yasi(19));
}

TEST(yasi, test_yasi__yetiskin_kategori)
{
    TEST_ASSERT_EQUAL_STRING("Yetiskin", yasi(20));
    TEST_ASSERT_EQUAL_STRING("Yetiskin", yasi(35));
    TEST_ASSERT_EQUAL_STRING("Yetiskin", yasi(64));
}

TEST(yasi, test_yasi__yasli_kategori)
{
    TEST_ASSERT_EQUAL_STRING("Yasli", yasi(65));
    TEST_ASSERT_EQUAL_STRING("Yasli", yasi(80));
    TEST_ASSERT_EQUAL_STRING("Yasli", yasi(120));
}

TEST(yasi, test_yasi__gecersiz_negatif)
{
    TEST_ASSERT_EQUAL_STRING("Gecersiz yas", yasi(-1));
    TEST_ASSERT_EQUAL_STRING("Gecersiz yas", yasi(-10));
}
```