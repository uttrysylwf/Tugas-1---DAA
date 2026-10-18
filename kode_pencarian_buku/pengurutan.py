# merge sort berdasarkan judul (dibuat sendiri, tanpa sorted())
def urutkan_judul(data):
    if len(data) <= 1:
        return data

    tengah = len(data) // 2
    kiri = urutkan_judul(data[:tengah])
    kanan = urutkan_judul(data[tengah:])

    hasil = []
    i = 0
    j = 0
    while i < len(kiri) and j < len(kanan):
        if kiri[i].judul <= kanan[j].judul:
            hasil.append(kiri[i])
            i = i + 1
        else:
            hasil.append(kanan[j])
            j = j + 1
    while i < len(kiri):
        hasil.append(kiri[i])
        i = i + 1
    while j < len(kanan):
        hasil.append(kanan[j])
        j = j + 1
    return hasil


# hapus judul kembar (data harus sudah terurut, jadi judul kembar pasti bersebelahan)
def hapus_kembar(data):
    hasil = []
    for buku in data:
        if len(hasil) == 0:
            hasil.append(buku)
        elif hasil[len(hasil) - 1].judul != buku.judul:
            hasil.append(buku)
    return hasil
