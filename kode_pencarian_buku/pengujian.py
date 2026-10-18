import time
from model import HasilPencarian
from linear_search import linear_search
from binary_search import binary_search


# jalankan 1 pencarian lalu simpan hasilnya
def cari(nama, fungsi, data, kunci):
    mulai = time.perf_counter()
    indeks, perbandingan = fungsi(data, kunci)
    waktu = time.perf_counter() - mulai
    if indeks == -1:
        buku = None
    else:
        buku = data[indeks]
    return HasilPencarian(nama, indeks, buku, perbandingan, waktu)


def tampilkan(h):
    print("[" + h.algoritma + "]")
    if h.ditemukan:
        print("  Status      : DITEMUKAN di indeks", h.indeks)
        print("  Judul       :", h.buku.judul)
        print("  Penulis     :", h.buku.penulis)
        print("  Kategori    :", h.buku.kategori)
    else:
        print("  Status      : TIDAK DITEMUKAN - buku tidak ada di dataset")
    print("  Perbandingan:", h.jumlah_perbandingan)
    print("  Waktu       : %.2f mikrodetik" % (h.waktu_eksekusi * 1000000))


# uji 4 skenario untuk n data
# data_unik = data yang sudah terurut dan tidak ada judul kembar
def uji_ukuran(data_unik, n):
    # ambil n data dengan jarak rata supaya contohnya tersebar
    langkah = len(data_unik) // n
    sub = []
    for i in range(n):
        sub.append(data_unik[i * langkah])
    judul_awal = sub[0].judul
    judul_tengah = sub[(n - 1) // 2].judul
    judul_akhir = sub[n - 1].judul

    nama_skenario = ["awal", "tengah", "akhir", "tidak ditemukan"]
    kunci_skenario = [judul_awal, judul_tengah, judul_akhir, "judul tidak ada"]
    nama_algo = ["Linear Search", "Binary Search"]
    fungsi_algo = [linear_search, binary_search]

    hasil = []
    for a in range(2):
        for s in range(4):
            fungsi = fungsi_algo[a]
            kunci = kunci_skenario[s]

            indeks, perbandingan = fungsi(sub, kunci)

            # diulang 200 kali supaya waktunya kebaca, lalu dirata-rata
            mulai = time.perf_counter()
            for ulang in range(200):
                fungsi(sub, kunci)
            waktu = (time.perf_counter() - mulai) / 200

            hasil.append({"n": n, "algoritma": nama_algo[a], "skenario": nama_skenario[s],
                          "perbandingan": perbandingan, "waktu": waktu})
    return hasil


# buat grafik perbandingan (skenario terburuk: data tidak ditemukan), disimpan jadi gambar
def buat_grafik(hasil):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib belum terpasang (pip install matplotlib), grafik dilewati")
        return

    ukuran = []
    linear_cmp = []
    binary_cmp = []
    linear_waktu = []
    binary_waktu = []
    for r in hasil:
        if r["skenario"] == "tidak ditemukan":
            if r["algoritma"] == "Linear Search":
                ukuran.append(r["n"])
                linear_cmp.append(r["perbandingan"])
                linear_waktu.append(r["waktu"] * 1000000)
            else:
                binary_cmp.append(r["perbandingan"])
                binary_waktu.append(r["waktu"] * 1000000)

    plt.figure(figsize=(10, 4))

    plt.subplot(1, 2, 1)
    plt.plot(ukuran, linear_cmp, marker="o", label="Linear Search")
    plt.plot(ukuran, binary_cmp, marker="s", label="Binary Search")
    plt.xscale("log")
    plt.yscale("log")
    plt.title("Jumlah perbandingan")
    plt.xlabel("n (jumlah data)")
    plt.ylabel("perbandingan")
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(ukuran, linear_waktu, marker="o", label="Linear Search")
    plt.plot(ukuran, binary_waktu, marker="s", label="Binary Search")
    plt.xscale("log")
    plt.yscale("log")
    plt.title("Waktu eksekusi")
    plt.xlabel("n (jumlah data)")
    plt.ylabel("mikrodetik")
    plt.legend()

    plt.tight_layout()
    plt.savefig("grafik_pengujian.png")
    plt.close()
    print("Grafik disimpan di grafik_pengujian.png")
