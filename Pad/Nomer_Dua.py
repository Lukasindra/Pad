# Perkalian Tanpa numpy
# Koefisien dari sistem persamaan:
# Persamaan 1: 2x + 3y = 8 → a1=2, b1=3, c1=8
# Persamaan 2: 3x + 4y = 11 → a2=3, b2=4, c2=11
a1, b1, c1 = 2, 3, 8
a2, b2, c2 = 3, 4, 11

# Menghitung determinan utama (D)
det = a1 * b2 - a2 * b1

# Menghitung determinan Dx dan Dy untuk x dan y
det_x = c1 * b2 - c2 * b1
det_y = a1 * c2 - a2 * c1

# Menghitung nilai x dan y
x = det_x / det
y = det_y / det

# Menampilkan hasil
print("Solusi SPL tanpa NumPy:")
print("x =", x)
print("y =", y)
