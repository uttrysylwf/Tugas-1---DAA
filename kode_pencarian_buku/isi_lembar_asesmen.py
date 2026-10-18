"""
Mengisi Lembar Asesmen (.docx) otomatis dari hasil program pencarian_buku.py.
    python isi_lembar_asesmen.py TEMPLATE.docx OUTPUT.docx [--csv books.csv] [--repo URL]
Jalankan dulu tanpa --csv untuk data pengganti, atau dengan --csv untuk data Kaggle asli.
"""
import argparse, copy, io, contextlib, math, subprocess, sys, json, os
import docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import types
import dataset, model, pengujian, pengurutan
import linear_search as m_linear
import binary_search as m_binary

pb = types.SimpleNamespace(
    baca_dataset=dataset.baca_dataset, 
    urutkan_judul=pengurutan.urutkan_judul, linear_search=m_linear.linear_search,
    binary_search=m_binary.binary_search, cari=pengujian.cari,
    tampilkan=pengujian.tampilkan, uji_ukuran=pengujian.uji_ukuran)

ap = argparse.ArgumentParser()
ap.add_argument("template"); ap.add_argument("output")
ap.add_argument("--csv", default="google_books_dataset.csv"); ap.add_argument("--repo", default="")
args = ap.parse_args()

# ----------------------------------------------------------- jalankan program
data = pb.baca_dataset(args.csv)
sumber = os.path.basename(args.csv) if args.csv else "DATA PENGGANTI (sintetis)"
terurut = pb.urutkan_judul(data)
unik = pengurutan.hapus_kembar(terurut)

def tangkap(fn):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn()
    return buf.getvalue().rstrip().split("\n")

kunci_ada = unik[len(unik) // 3].judul
kunci_tidak = "Judul Yang Tidak Ada"

# jalankan main.py yang asli, lalu tampilkan ketikan seperti di terminal
def jalankan_main(masukan):
    folder = os.path.dirname(os.path.abspath(__file__))
    perintah = [sys.executable, "main.py"] + ([args.csv] if args.csv else [])
    r = subprocess.run(perintah, input="\n".join(masukan) + "\n", capture_output=True,
                       text=True, encoding="utf-8", cwd=folder)
    teks = r.stdout
    prompts = ["Pilih menu: ", "Masukkan judul buku (harus sama persis): "]
    hasil_teks, pos = "", 0
    for ketik in masukan:
        cand = [(teks.find(p, pos), p) for p in prompts if teks.find(p, pos) != -1]
        i, p = min(cand)
        j = i + len(p)
        hasil_teks += teks[pos:j] + ketik + "\n"
        pos = j
    hasil_teks += teks[pos:]
    return hasil_teks.rstrip().split("\n")

def potong_sesi(baris):
    """Pisahkan sesi jadi: bagian awal, blok Linear Search, blok Binary Search."""
    i_lin = next(k for k, l in enumerate(baris) if l.startswith("[Linear Search]"))
    i_bin = next(k for k, l in enumerate(baris) if l.startswith("[Binary Search]"))
    akhir = i_bin
    while akhir < len(baris) and baris[akhir].strip() != "":
        akhir += 1
    awal = baris[:i_lin]
    return awal, baris[i_lin:i_bin], baris[i_bin:akhir]

awal_ada, lin_ada, bin_ada = potong_sesi(jalankan_main(["1", kunci_ada, "0"]))
awal_tidak, lin_tidak, _ = potong_sesi(jalankan_main(["1", kunci_tidak, "0"]))
out_lin_ada = awal_ada + lin_ada
out_bin_ada = awal_ada + bin_ada
out_lin_tidak = awal_tidak + lin_tidak

hasil = []
for n in (100, 1000, 10000):
    hasil += pb.uji_ukuran(unik, n)

def ambil(n, algo, sk):
    return next(r for r in hasil if r["n"] == n and r["algoritma"] == algo and r["skenario"] == sk)

def us(x):
    return f"{x*1e6:.3f} µs"

def rumus_bin(n):
    return 2 * (int(math.floor(math.log2(n))) + 1)

# -------------------------------------------------------------- potongan kode
def baca_kode(nama_file, mulai=None, sampai=None):
    """Ambil isi file kode sebagai list baris (dipotong dari baris `mulai` sampai sebelum `sampai`)."""
    baris = open(nama_file, encoding="utf-8").read().rstrip().split("\n")
    i = 0 if mulai is None else next(k for k, l in enumerate(baris) if l.startswith(mulai))
    j = len(baris) if sampai is None else next(k for k in range(i + 1, len(baris)) if baris[k].startswith(sampai))
    return "\n".join(baris[i:j]).rstrip().split("\n")

kode_input = baca_kode("model.py", "class Buku", "# kelas untuk hasil")
kode_output = baca_kode("model.py", "class HasilPencarian")
kode_linear = baca_kode("linear_search.py")
kode_binary = baca_kode("binary_search.py") + ["", ""] + baca_kode("pengurutan.py")

# ------------------------------------------------------------ grafik
fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
ns = [100, 1000, 10000]
lin_c = [ambil(n, "Linear Search", "tidak ditemukan")["perbandingan"] for n in ns]
bin_c = [ambil(n, "Binary Search", "tidak ditemukan")["perbandingan"] for n in ns]
lin_t = [ambil(n, "Linear Search", "tidak ditemukan")["waktu"] * 1e6 for n in ns]
bin_t = [ambil(n, "Binary Search", "tidak ditemukan")["waktu"] * 1e6 for n in ns]
ax[0].plot(ns, lin_c, "o-", label="Linear Search  (n)")
ax[0].plot(ns, bin_c, "s-", label="Binary Search  (2(⌊log₂n⌋+1))")
ax[0].set_xscale("log"); ax[0].set_yscale("log")
ax[0].set_title("Jumlah perbandingan (worst case)"); ax[0].set_xlabel("n"); ax[0].set_ylabel("perbandingan")
ax[1].plot(ns, lin_t, "o-", label="Linear Search")
ax[1].plot(ns, bin_t, "s-", label="Binary Search")
ax[1].set_xscale("log"); ax[1].set_yscale("log")
ax[1].set_title("Waktu eksekusi (worst case)"); ax[1].set_xlabel("n"); ax[1].set_ylabel("mikrodetik")
for a in ax:
    a.grid(True, which="both", alpha=.3); a.legend()
plt.tight_layout(); plt.savefig("grafik_pengujian.png", dpi=150); plt.close()

# --------------------------------------------------------------- helper docx
d = docx.Document(args.template)
T = d.tables

def isi(cell, teks, size=9, bold=False, mono=False, center=False):
    baris = teks if isinstance(teks, list) else str(teks).split("\n")
    ps = cell.paragraphs
    for p in ps[1:]:
        p._p.getparent().remove(p._p)
    p0 = cell.paragraphs[0]
    for r in list(p0.runs):
        r._r.getparent().remove(r._r)
    for k, b in enumerate(baris):
        p = p0 if k == 0 else cell.add_paragraph()
        p.paragraph_format.space_after = Pt(1 if mono else 3)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        if center:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(b)
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.name = "Courier New" if mono else "Arial"
        rpr = r._r.get_or_add_rPr()
        rf = rpr.find(qn("w:rFonts"))
        nama = "Courier New" if mono else "Arial"
        for att in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rf.set(qn(att), nama)

def tambah_baris(tabel, jumlah_akhir):
    while len(tabel.rows) - 1 < jumlah_akhir:
        baru = copy.deepcopy(tabel.rows[-1]._tr)
        tabel._tbl.append(baru)

# 1. Link repository
isi(T[3].rows[0].cells[1], args.repo or "(isi dengan link repository GitHub publik Anda)")

# 2. Model input
tabel_in = [
    ("1", "Buku", "judul", "str", "Teks judul; menjadi kata kunci pencarian dan kunci pengurutan untuk Binary Search (urutan abjad)."),
    ("2", "Buku", "penulis", "str", "Nama penulis berupa teks bebas."),
    ("3", "Buku", "kategori", "str", "Nama kategori buku berupa label teks."),
]
tambah_baris(T[4], len(tabel_in))
for k, row in enumerate(tabel_in, start=1):
    for c, v in enumerate(row):
        isi(T[4].rows[k].cells[c], v, center=(c == 0))
isi(T[5].rows[0].cells[0], kode_input, size=8, mono=True)

# 3. Model output
tabel_out = [
    ("1", "HasilPencarian", "algoritma", "str", "Nama algoritma (\"Linear Search\"/\"Binary Search\") untuk label hasil."),
    ("2", "HasilPencarian", "ditemukan", "bool", "Status ya/tidak; bentuk paling sederhana untuk menandai ditemukan atau tidak."),
    ("3", "HasilPencarian", "indeks", "int", "Posisi data pada list; bernilai -1 bila tidak ditemukan."),
    ("4", "HasilPencarian", "buku", "Buku | None", "Objek Buku hasil pencarian (judul, penulis, kategori); None bila tidak ditemukan."),
    ("5", "HasilPencarian", "jumlah_perbandingan", "int", "Cacah operasi dasar (perbandingan judul); bilangan bulat karena berupa hitungan."),
    ("6", "HasilPencarian", "waktu_eksekusi", "float", "Waktu dalam detik dari time.perf_counter(); bernilai desimal dan sangat kecil."),
]
tambah_baris(T[6], len(tabel_out))
for k, row in enumerate(tabel_out, start=1):
    for c, v in enumerate(row):
        isi(T[6].rows[k].cells[c], v, center=(c == 0))
isi(T[7].rows[0].cells[0], kode_output, size=8, mono=True)

# 4. Linear Search
lin_q = [
    "Judul buku (atribut judul), dicocokkan secara persis (exact match, huruf besar/kecil dibedakan).",
    "String (str).",
    "Hanya 1 hasil, yaitu kemunculan pertama. Pencarian berhenti begitu judul yang cocok ditemukan (bila ada judul kembar, yang ditampilkan yang pertama).",
    "Status ditemukan, indeks, judul, penulis, kategori, jumlah perbandingan, dan waktu eksekusi (objek HasilPencarian).",
    f"Indeks bernilai -1, buku bernilai None, dan program menampilkan pesan \"TIDAK DITEMUKAN\". Seluruh n elemen sudah diperiksa sehingga jumlah perbandingan = n.",
]
for k, v in enumerate(lin_q, start=1):
    isi(T[8].rows[k].cells[2], v)
isi(T[9].rows[0].cells[0], kode_linear, size=8, mono=True)

# 5. Binary Search
bin_q = [
    "Judul buku (atribut judul). Data wajib sudah terurut menurut judul (diurutkan dengan merge sort buatan sendiri, fungsi urutkan_judul()).",
    "String (str); dibandingkan secara leksikografis dengan operator == dan <.",
    "Hanya 1 hasil (satu indeks). Bila ada judul kembar, yang ditemukan adalah salah satunya.",
    "Status ditemukan, indeks, judul, penulis, kategori, jumlah perbandingan, dan waktu eksekusi (objek HasilPencarian).",
    "Perulangan berhenti saat kiri > kanan, fungsi mengembalikan indeks -1, buku bernilai None, dan program menampilkan \"TIDAK DITEMUKAN\". Jumlah perbandingan maksimum 2(⌊log₂ n⌋+1).",
]
for k, v in enumerate(bin_q, start=1):
    isi(T[10].rows[k].cells[2], v)
isi(T[11].rows[0].cells[0], kode_binary, size=8, mono=True)

# 6. Output
isi(T[12].rows[0].cells[0], out_lin_ada, size=8, mono=True)
isi(T[13].rows[0].cells[0], out_bin_ada, size=8, mono=True)
isi(T[14].rows[0].cells[0], out_lin_tidak, size=8, mono=True)

# 7. Jumlah operasi perbandingan (n = 10.000)
N = 10000
isi(T[15].rows[1].cells[2],
    f"Best case: 1\nAverage case: ≈ (n+1)/2\nWorst case: n\n(n = {N:,}: 1 / ≈5.000 / {N:,})".replace(",", "."))
isi(T[15].rows[1].cells[3],
    f"Setiap elemen diperiksa dengan data[i].judul == kunci. Contoh n = 10.000, data tidak ditemukan: {ambil(N,'Linear Search','tidak ditemukan')['perbandingan']:,} perbandingan.".replace(",", "."))
w = rumus_bin(N)
isi(T[15].rows[2].cells[2],
    f"Best case: 1\nWorst case: 2(⌊log₂ n⌋+1)\n(n = 10.000: 1 / {w})")
isi(T[15].rows[2].cells[3],
    f"Tiap iterasi ada 2 perbandingan judul (== lalu <) dan ruang pencarian dibagi dua. Contoh n = 10.000, tidak ditemukan: ⌊log₂ 10000⌋+1 = 14 iterasi × 2 = {ambil(N,'Binary Search','tidak ditemukan')['perbandingan']} perbandingan.")

# 8. Pengujian (n = 10.000)
urut_sk = ["awal", "tengah", "akhir", "tidak ditemukan"]
baris16 = [("Linear Search", s) for s in urut_sk] + [("Binary Search", s) for s in urut_sk]
for k, (al, sk) in enumerate(baris16, start=1):
    r = ambil(N, al, sk)
    isi(T[16].rows[k].cells[3], f"{r['perbandingan']:,}".replace(",", "."))
    isi(T[16].rows[k].cells[4], us(r["waktu"]))

# 9. Kompleksitas
k_lin = ["Ω(1)", "Θ(n)", "Ο(n)", "Posisi awal: 1 perbandingan", "Posisi tengah/rata-rata: ≈ n/2", "Posisi akhir / tidak ditemukan: n"]
k_bin = ["Ω(1)", "Θ(log n)", "Ο(log n)", "Tepat di tengah: 1 iterasi", "Rata-rata: ≈ log₂ n iterasi", "Posisi ujung / tidak ditemukan: ⌊log₂ n⌋+1 iterasi"]
for c, v in enumerate(k_lin):
    isi(T[17].rows[2].cells[2 + c], v, size=8, center=(c < 3))
for c, v in enumerate(k_bin):
    isi(T[17].rows[3].cells[2 + c], v, size=8, center=(c < 3))

# 10. Algoritma terbaik per skenario
def alasan(sk):
    L, B = ambil(N, "Linear Search", sk), ambil(N, "Binary Search", sk)
    return L, B
L, B = alasan("awal")
terbaik = [
    ("Linear Search", "Binary Search",
     f"Linear Search langsung menemukan di elemen pertama ({L['perbandingan']} perbandingan, {us(L['waktu'])}); Binary Search tetap harus menyempit ke ujung kiri ({B['perbandingan']} perbandingan, {us(B['waktu'])})."),
]
L, B = alasan("tengah")
terbaik.append(("Binary Search", "Linear Search",
     f"Elemen tengah langsung ditemukan pada iterasi pertama ({B['perbandingan']} perbandingan, {us(B['waktu'])}), sedangkan Linear Search memerlukan {L['perbandingan']:,} perbandingan ({us(L['waktu'])}).".replace(",", ".")))
L, B = alasan("akhir")
terbaik.append(("Binary Search", "Linear Search",
     f"Linear Search harus memindai seluruh data ({L['perbandingan']:,} perbandingan, {us(L['waktu'])}); Binary Search cukup {B['perbandingan']} perbandingan ({us(B['waktu'])}).".replace(",", ".")))
L, B = alasan("tidak ditemukan")
terbaik.append(("Binary Search", "Linear Search",
     f"Linear Search selalu memeriksa n elemen ({L['perbandingan']:,}); Binary Search hanya {B['perbandingan']} perbandingan sehingga jauh lebih cepat ({us(B['waktu'])} vs {us(L['waktu'])}).".replace(",", ".")))
# validasi: kesimpulan harus konsisten dengan hasil ukur
for sk, (bt, bw, _) in zip(urut_sk, terbaik):
    L, B = alasan(sk)
    benar = "Linear Search" if L["perbandingan"] < B["perbandingan"] else "Binary Search"
    assert benar == bt, f"Kesimpulan skenario {sk} tidak konsisten dengan data: {benar}"
for k, (bt, bw, al) in enumerate(terbaik, start=1):
    isi(T[18].rows[k].cells[2], bt)
    isi(T[18].rows[k].cells[3], bw)
    isi(T[18].rows[k].cells[4], al, size=8)

# --------------------------------------------------- bagian analisis tambahan
anchor = next(p for p in d.paragraphs if p.text.strip() == "KRITERIA PENILAIAN")

def para(teks, bold=False, size=10, after=6, italic=False, center=False):
    p = anchor.insert_paragraph_before()
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.15
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    else:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run(teks)
    r.font.name = "Arial"; r.font.size = Pt(size); r.font.bold = bold; r.font.italic = italic
    r._r.get_or_add_rPr().find(qn("w:rFonts")).set(qn("w:eastAsia"), "Arial")
    return p

def tabel(header, rows, lebar):
    t = d.add_table(rows=1 + len(rows), cols=len(header))
    tblPr = t._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for sisi in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{sisi}")
        e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4"); e.set(qn("w:color"), "000000")
        b.append(e)
    tblPr.append(b)
    for r_i, row in enumerate([header] + rows):
        for c_i, v in enumerate(row):
            cell = t.rows[r_i].cells[c_i]
            cell.width = Inches(lebar[c_i])
            isi(cell, v, size=8.5, bold=(r_i == 0), center=(c_i != 0 and r_i == 0))
            if r_i == 0:
                shd = OxmlElement("w:shd")
                shd.set(qn("w:val"), "clear"); shd.set(qn("w:fill"), "D9D9D9")
                cell._tc.get_or_add_tcPr().append(shd)
    anchor._p.addprevious(t._tbl)
    para("", after=4)
    return t

para("ANALISIS TAMBAHAN", bold=True, size=12, after=8)

para("A. Karakterisasi Masalah", bold=True)
para("Input: kumpulan n record buku (list of Buku: judul, penulis, kategori) dan sebuah kata kunci berupa judul buku. Output: objek HasilPencarian "
     "(status ditemukan, indeks, data buku, jumlah perbandingan, waktu eksekusi). Ukuran input: n = jumlah buku pada dataset. "
     "Operasi dasar: perbandingan judul buku dengan kata kunci. Operasi yang sama dihitung pada kedua algoritma sehingga hasilnya dapat dibandingkan secara adil. "
     "Alasan pemilihan: perbandingan adalah operasi yang paling sering diulang dan menentukan pertumbuhan waktu, sedangkan inisialisasi variabel dan penggeseran indeks hanya bernilai konstan.")

para(f"Dataset: setelah baris berjudul kosong dibuang, program membaca {len(data)} buku dengan {len(unik)} judul unik. "
     "Judul kembar (misalnya penerbitan berkala) dapat menghasilkan lebih dari satu kecocokan: Linear Search menampilkan kemunculan pertama, "
     "sedangkan Binary Search menampilkan salah satunya. Untuk pengujian ukuran input (n = 100, 1.000, 10.000), data diambil dari daftar judul unik yang sudah terurut "
     "supaya posisi awal, tengah, dan akhir jelas dan identik untuk kedua algoritma.")

para("B. Analisis Kompleksitas Worst-Case", bold=True)
para("Linear Search: pada worst case (data di posisi terakhir atau tidak ada) setiap elemen diperiksa tepat satu kali, sehingga W(n) = n perbandingan = Ο(n). "
     "Best case: 1 perbandingan (data di posisi pertama), jadi Ω(1). Rata-rata bila data pasti ada: (n+1)/2 = Θ(n).")
para("Binary Search: pada tiap iterasi ruang pencarian dibagi dua: n → n/2 → n/4 → … → 1. Jumlah iterasi maksimum adalah ⌊log₂ n⌋ + 1. "
     "Pada implementasi ini tiap iterasi melakukan 2 perbandingan judul (== dan <), sehingga W(n) = 2(⌊log₂ n⌋ + 1) = Ο(log n). "
     "Untuk n = 100, 1.000, dan 10.000 nilainya berturut-turut 14, 20, dan 28. Best case: 1 perbandingan (data tepat di tengah), jadi Ω(1).")

para("C. Dampak Perubahan Ukuran Input", bold=True)
rows = []
for n in ns:
    L = ambil(n, "Linear Search", "tidak ditemukan"); B = ambil(n, "Binary Search", "tidak ditemukan")
    rows.append([f"{n:,}".replace(",", "."), f"{n:,}".replace(",", "."), str(rumus_bin(n)),
                 f"{L['perbandingan']:,}".replace(",", "."), str(B["perbandingan"]),
                 us(L["waktu"]), us(B["waktu"])])
tabel(["n", "Teori Linear", "Teori Binary", "Empiris Linear", "Empiris Binary", "Waktu Linear", "Waktu Binary"],
      rows, [0.7, 0.8, 0.8, 0.9, 0.9, 1.0, 1.0])
LL = [ambil(n, "Linear Search", "tidak ditemukan") for n in ns]
BB = [ambil(n, "Binary Search", "tidak ditemukan") for n in ns]
para("Secara kuantitatif, setiap kenaikan n sebesar 10 kali membuat jumlah perbandingan Linear Search ikut naik 10 kali (100 → 1.000 → 10.000), "
     "sedangkan Binary Search hanya bertambah 6 dan 8 perbandingan (14 → 20 → 28), karena log₂ 10 ≈ 3,3 dan tiap iterasi memakai 2 perbandingan. "
     f"Waktu eksekusi mengikuti pola yang sama: Linear Search naik dari {us(LL[0]['waktu'])} menjadi {us(LL[2]['waktu'])} "
     f"(naik ×{LL[2]['waktu']/LL[0]['waktu']:.0f} ketika n naik 100 kali), sedangkan Binary Search dari {us(BB[0]['waktu'])} menjadi {us(BB[2]['waktu'])} "
     f"(hanya naik ×{BB[2]['waktu']/BB[0]['waktu']:.1f}). Secara kualitatif, Linear Search tumbuh linear terhadap ukuran data sehingga tidak skalabel untuk jutaan buku, "
     "sedangkan Binary Search tumbuh logaritmik sehingga hampir tidak terpengaruh oleh pertambahan data.")
d_pic = anchor.insert_paragraph_before()
d_pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
d_pic.add_run().add_picture("grafik_pengujian.png", width=Inches(6.3))
para("Gambar 1. Perbandingan jumlah perbandingan dan waktu eksekusi (skala log-log, skenario data tidak ditemukan).",
     italic=True, size=9, center=True)

para("D. Algoritma Terbaik Secara Asimtotik", bold=True)
para("Untuk n yang sangat besar, Binary Search adalah algoritma terbaik karena Ο(log n) tumbuh jauh lebih lambat daripada Ο(n): "
     "lim (n→∞) (log n)/n = 0, sehingga ada n₀ dan konstanta c yang membuat 2(log₂ n + 1) < n untuk semua n ≥ n₀. "
     "Pada n = 10.000 selisihnya sudah 28 berbanding 10.000 perbandingan. Syaratnya, data harus terurut. Biaya pengurutan sekali adalah Ο(n log n); "
     "bila hanya dilakukan satu kali pencarian pada data yang belum terurut, Linear Search (Ο(n)) justru lebih murah daripada mengurutkan lalu mencari. "
     "Untuk pencarian yang berulang-ulang pada dataset tetap seperti perpustakaan digital, Binary Search lebih tepat.")

para("E. Perbandingan Hasil Teori dan Implementasi Nyata", bold=True)
para("Jumlah perbandingan hasil eksekusi sama persis dengan prediksi teori: Linear Search n perbandingan dan Binary Search 14, 20, dan 28 perbandingan "
     "untuk n = 100, 1.000, dan 10.000 pada skenario terburuk. Waktu eksekusi sesuai dalam hal tren, tetapi tidak persis proporsional. "
     f"Waktu Linear Search naik ×{LL[1]['waktu']/LL[0]['waktu']:.0f} dan ×{LL[2]['waktu']/LL[1]['waktu']:.0f} saat n naik 10 kali (prediksi teori ×10); "
     "penyimpangan ini disebabkan oleh faktor konstan interpreter Python, cache memori CPU pada data yang lebih besar, dan resolusi timer pada waktu yang sangat singkat. "
     "Binary Search juga memiliki biaya per iterasi yang lebih besar (perhitungan indeks tengah dan 2 perbandingan), sehingga pada n kecil "
     "(contoh data di posisi awal pada n = 100) Linear Search masih bisa lebih cepat; keunggulan Binary Search baru terlihat jelas ketika n membesar. "
     "Waktu yang dilaporkan adalah rata-rata dari 200 pengulangan untuk mengurangi derau pengukuran, dan dapat berbeda sedikit pada setiap komputer.")

para("Hasil pengujian lengkap (jumlah perbandingan dan waktu rata-rata) untuk semua ukuran input:", bold=True, size=9)
rows = []
for r in hasil:
    rows.append([f"{r['n']:,}".replace(",", "."), r["algoritma"], r["skenario"],
                 f"{r['perbandingan']:,}".replace(",", "."), us(r["waktu"])])
tabel(["n", "Algoritma", "Skenario", "Jumlah Perbandingan", "Waktu Eksekusi"], rows, [0.7, 1.3, 1.4, 1.4, 1.3])

d.save(args.output)
with open("hasil_pengujian.json", "w", encoding="utf-8") as f:
    json.dump({"sumber": sumber, "jumlah_data": len(data), "pengujian": hasil}, f, indent=2)
print("OK ->", args.output)
