import numpy as np  # Mengimpor pustaka NumPy
# Matriks koefisien
A = np.array([[2, 3],
              [3, 4]])

# Vektor konstanta hasil
B = np.array([8, 11])

# Menggunakan np.linalg.solve untuk menyelesaikan SPL Ax = B
solusi = np.linalg.solve(A, B)

# Menampilkan solusi x dan y
print("Solusi SPL dengan NumPy:")
print("x =", solusi[0])
print("y =", solusi[1])
