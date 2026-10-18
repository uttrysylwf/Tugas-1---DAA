# Pencarian buku: Linear Search vs Binary Search
# Taruh google_books_dataset.csv di folder yang sama dengan main.py, lalu jalankan main.py
import os
import sys
from dataset import baca_dataset
from pengurutan import urutkan_judul, hapus_kembar
from linear_search import linear_search
from binary_search import binary_search
from pengujian import cari, tampilkan, uji_ukuran, buat_grafik


# menu 1: petugas mengetik judul, dicari dengan kedua algoritma
def menu_cari(data, terurut):
    judul = input("Masukkan judul buku (harus sama persis): ").strip()
    if judul == "":
        print("Judul tidak boleh kosong.")
        return
    print("")
    hasil_linear = cari("Linear Search", linear_search, data, judul)
    hasil_binary = cari("Binary Search", binary_search, terurut, judul)
    tampilkan(hasil_linear)
    tampilkan(hasil_binary)
    if not hasil_linear.ditemukan:
        print("")
        print("Tips: judul harus sama persis (huruf besar/kecil dan spasi dibedakan).")
        print("      Coba salin judul dari contoh di atas.")


# menu 2: uji n = 100, 1000, 10000 lalu tampilkan tabel dan grafik
def menu_pengujian(unik):
    print("")
    print("%7s %-14s %-16s %12s %12s" % ("n", "Algoritma", "Skenario", "Perbandingan", "Waktu (us)"))
    semua = []
    for n in [100, 1000, 10000]:
        hasil = uji_ukuran(unik, n)
        for r in hasil:
            print("%7d %-14s %-16s %12d %12.3f" % (r["n"], r["algoritma"], r["skenario"],
                                                   r["perbandingan"], r["waktu"] * 1000000))
        semua = semua + hasil
    print("")
    buat_grafik(semua)


def main():
    # file csv dicari di folder yang sama dengan main.py (boleh juga ditulis lewat argumen)
    folder = os.path.dirname(os.path.abspath(__file__))
    nama_file = os.path.join(folder, "google_books_dataset.csv")
    if len(sys.argv) > 1:
        nama_file = sys.argv[1]

    if not os.path.exists(nama_file):
        print("File dataset tidak ditemukan:", nama_file)
        print("Taruh google_books_dataset.csv di folder yang sama dengan main.py")
        return
    print("Membaca file:", nama_file)
    data = baca_dataset(nama_file)
    terurut = urutkan_judul(data)
    unik = hapus_kembar(terurut)
    print("Jumlah buku:", len(data), "| judul unik:", len(unik))
    print("Contoh judul yang ada:", unik[len(unik) // 3].judul)

    while True:
        print("")
        print("=== MENU ===")
        print("1. Cari buku")
        print("2. Jalankan pengujian (n = 100, 1.000, 10.000)")
        print("0. Keluar")
        pilihan = input("Pilih menu: ").strip()
        if pilihan == "1":
            menu_cari(data, terurut)
        elif pilihan == "2":
            menu_pengujian(unik)
        elif pilihan == "0":
            print("Selesai.")
            break
        else:
            print("Pilihan tidak ada.")


main()
