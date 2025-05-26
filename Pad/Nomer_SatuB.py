import numpy as np  # Mengimpor pustaka NumPy

# Mendefinisikan matriks A dan B
A = np.array([[1, 2],
              [3, 4]])
B = np.array([[5, 6],
              [7, 8]])
              

# Mengalikan matriks A dan B menggunakan fungsi dot
C = np.dot(A, B)

# Menampilkan hasil
print("Hasil perkalian dengan NumPy:")
print(C)
