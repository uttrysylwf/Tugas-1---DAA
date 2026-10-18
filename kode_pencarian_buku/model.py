# kelas untuk data buku (input)
class Buku:
    def __init__(self, judul, penulis, kategori):
        self.judul = judul          # str
        self.penulis = penulis      # str
        self.kategori = kategori    # str


# kelas untuk hasil pencarian (output)
class HasilPencarian:
    def __init__(self, algoritma, indeks, buku, jumlah_perbandingan, waktu_eksekusi):
        self.algoritma = algoritma                      # str
        if indeks == -1:
            self.ditemukan = False                      # bool
        else:
            self.ditemukan = True
        self.indeks = indeks                            # int, -1 kalau tidak ketemu
        self.buku = buku                                # Buku, None kalau tidak ketemu
        self.jumlah_perbandingan = jumlah_perbandingan  # int
        self.waktu_eksekusi = waktu_eksekusi            # float (detik)
