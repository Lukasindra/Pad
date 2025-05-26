# Perkalian Tanpa numpy
# Matriks A dan B masing-masing berukuran 2x2
A = [[1, 2],
     [3, 4]]
B = [[5, 6],
     [7, 8]]

# Matriks kosong untuk menyimpan hasil perkalian A * B
C = [[0, 0],
     [0, 0]]

# Melakukan perkalian matriks secara manual (triple nested loop)
for i in range(2):             # untuk setiap baris di A
    for j in range(2):         # untuk setiap kolom di B
        for k in range(2):     # untuk setiap elemen dalam baris dan kolom
            C[i][j] += A[i][k] * B[k][j]  # menjumlahkan hasil kali elemen

# Menampilkan hasil akhir
print("Hasil perkalian tanpa NumPy:")
for row in C:
    print(row)
