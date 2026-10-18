import csv
from model import Buku


# baca data dari file csv
def baca_dataset(nama_file):
    data = []
    file = open(nama_file, encoding="utf-8-sig", newline="")
    baca = csv.DictReader(file)
    for baris in baca:
        judul = baris["title"].strip()
        if judul == "":
            continue            # judul kosong dilewati
        penulis = baris["authors"]
        if penulis == "":
            penulis = "-"
        kategori = baris["categories"]
        if kategori == "":
            kategori = "-"
        data.append(Buku(judul, penulis, kategori))
    file.close()
    return data
