/**
 * @file test_function.c
 * @brief Test fonksiyonları için örnek dosya
 */

/**
 * @brief İki sayıyı toplar
 * @param a İlk sayı
 * @param b İkinci sayı
 * @return Toplam sonucu
 */
int add_numbers(int a, int b) {
    return a + b;
}

/**
 * @brief Bir sayının karesini hesaplar
 * @param x Hesaplanacak sayı
 * @return Sayının karesi
 */
int square_number(int x) {
    return x * x;
}

/**
 * @brief Bir sayının pozitif olup olmadığını kontrol eder
 * @param num Kontrol edilecek sayı
 * @return 1 eğer pozitif, 0 eğer negatif veya sıfır
 */
int is_positive(int num) {
    if (num > 0) {
        return 1;
    }
    return 0;
} 