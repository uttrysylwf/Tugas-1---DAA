# data harus sudah terurut berdasarkan judul
def binary_search(data, kunci):
    perbandingan = 0
    kiri = 0
    kanan = len(data) - 1
    while kiri <= kanan:
        tengah = (kiri + kanan) // 2

        perbandingan = perbandingan + 1
        if data[tengah].judul == kunci:
            return tengah, perbandingan

        perbandingan = perbandingan + 1
        if data[tengah].judul < kunci:
            kiri = tengah + 1
        else:
            kanan = tengah - 1
    return -1, perbandingan
