/**
 * @file array_utils.c
 * @brief Dizi işlemleri için yardımcı fonksiyonlar
 */

#include <limits.h>

/**
 * @brief Bir tamsayı dizisindeki en büyük elemanı bulur.
 *
 * @param arr İncelenecek tamsayı dizisi
 * @param size Dizinin eleman sayısı (0'dan büyük olmalıdır)
 * @return Dizideki en büyük değer; eğer dizi boşsa INT_MIN döner
 *
 * @note Eğer `size <= 0` ise fonksiyon INT_MIN döner.
 */
int find_max_in_array(const int *arr, int size) {
    if (size <= 0 || arr == NULL) {
        return INT_MIN;
    }

    int max = arr[0];
    for (int i = 1; i < size; ++i) {
        if (arr[i] > max) {
            max = arr[i];
        }
    }
    return max;
}
