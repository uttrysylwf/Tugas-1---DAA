# Pencarian Buku: Linear Search vs Binary Search

Tugas 1 - Analisis kompleksitas algoritma pencarian (UIN Suska Riau, Teknik Informatika).
Pencarian dan pengurutan ditulis sendiri (tanpa `list.index()`, `in`, `sorted()`, `bisect`).

## Struktur file
- `main.py`          : program utama dengan menu (jalankan file ini)
- `model.py`         : kelas input `Buku` dan kelas output `HasilPencarian`
- `dataset.py`       : membaca dataset CSV
- `linear_search.py` : algoritma Linear Search
- `binary_search.py` : algoritma Binary Search
- `pengurutan.py`    : merge sort buatan sendiri + hapus judul kembar
- `pengujian.py`     : hitung perbandingan, ukur waktu, tampilkan hasil, buat grafik
- `isi_lembar_asesmen.py` : (opsional) mengisi lembar asesmen .docx dari hasil pengujian

## Menjalankan
1. Unduh dataset Kaggle "books-dataset-15k-books-across-100-categories" (file `google_books_dataset.csv`).
2. Taruh `google_books_dataset.csv` di folder yang SAMA dengan `main.py`.
3. Jalankan:

       pip install matplotlib        (hanya untuk grafik)
       python main.py

Menu:
1. Cari buku: ketik judul (harus sama persis), dicari dengan Linear Search dan Binary Search.
2. Pengujian: n = 100, 1.000, 10.000, tabel di terminal dan grafik `grafik_pengujian.png`.
