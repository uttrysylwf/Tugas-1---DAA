# cek data satu per satu dari awal
def linear_search(data, kunci):
    perbandingan = 0
    for i in range(len(data)):
        perbandingan = perbandingan + 1
        if data[i].judul == kunci:
            return i, perbandingan
    return -1, perbandingan
