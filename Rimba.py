import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import datetime

# ---------- Data Model ---------- #
class ItemSewa:
    def __init__(self, nama, harga):
        self.nama = nama
        self.harga = harga

class PaketCamping:
    def __init__(self, nama, harga, items):
        self.nama = nama
        self.harga = harga
        self.items = items

class TransaksiSewa:
    def __init__(self, nama_pelanggan, tanggal_pinjam, tanggal_kembali, items, paket, paket_jumlah):
        self.nama_pelanggan = nama_pelanggan
        self.tanggal_pinjam = tanggal_pinjam
        self.tanggal_kembali = tanggal_kembali
        self.items = items  # list of tuples (ItemSewa, jumlah)
        self.paket = paket
        self.paket_jumlah = paket_jumlah

    def total_biaya(self):
        hari = (self.tanggal_kembali - self.tanggal_pinjam).days or 1
        total = 0
        for item, jumlah in self.items:
            total += item.harga * jumlah * hari
        if self.paket and self.paket_jumlah > 0:
            total += self.paket.harga * self.paket_jumlah * hari
        return total

    def generate_struk(self):
        hari = (self.tanggal_kembali - self.tanggal_pinjam).days or 1
        struk = "===== STRUK SEWA ALAT CAMPING =====\n"
        struk += f"Nama Pelanggan : {self.nama_pelanggan}\n"
        struk += f"Tgl Pinjam     : {self.tanggal_pinjam.strftime('%d-%m-%Y')}\n"
        struk += f"Tgl Kembali    : {self.tanggal_kembali.strftime('%d-%m-%Y')}\n"
        struk += f"Lama Sewa      : {hari} hari\n"
        struk += "-----------------------------------\n"
        if self.paket and self.paket_jumlah > 0:
            struk += f"Paket {self.paket.nama} x{self.paket_jumlah} @ Rp{self.paket.harga:,} = Rp{self.paket.harga * self.paket_jumlah * hari:,}\n"
        if self.items:
            for item, jumlah in self.items:
                struk += f"{item.nama} x{jumlah} @ Rp{item.harga:,} = Rp{item.harga * jumlah * hari:,}\n"
        struk += "-----------------------------------\n"
        struk += f"TOTAL BAYAR    : Rp{self.total_biaya():,}\n"
        struk += "===================================\n"
        return struk

# ---------- Aplikasi GUI ---------- #
class AplikasiSewa:
    def __init__(self, root):
        self.root = root
        self.root.title("Anak Rimba - Sewa Alat Camping")
        self.root.geometry("820x780")
        self.root.configure(bg="#E9F1F7")  # warna latar lembut biru muda

        # Data Alat & Paket
        self.daftar_alat = [
            ItemSewa("Tenda", 50000),
            ItemSewa("Sleeping Bag", 30000),
            ItemSewa("Kompor", 25000),
            ItemSewa("Carrier", 40000),
            ItemSewa("Matras", 15000),
            ItemSewa("Flysheet", 10000),
            ItemSewa("Jas Hujan", 8000),
            ItemSewa("Senter Kepala", 12000),
            ItemSewa("Trangia", 20000),
            ItemSewa("Lampu Tenda", 10000)
        ]
        self.daftar_paket = [
            PaketCamping("Paket Hemat", 250000, ["Tenda Dome", "Matras", "Kompor Portable", "Gas Butane"]),
            PaketCamping("Paket Solo", 180000, ["Tenda Dome", "Matras", "Sleeping Bag"]),
            PaketCamping("Paket Rame-rame", 500000, ["2x Tenda Dome", "4x Matras", "2x Kompor", "4x Sleeping Bag", "2x Gas"])
        ]

        # Variabel
        self.var_nama = tk.StringVar()
        self.var_tanggal_pinjam = tk.StringVar()
        self.var_tanggal_kembali = tk.StringVar()
        self.jumlah_vars = []
        self.var_paket_pilih = tk.StringVar(value="Tidak Ada")
        self.var_paket_jumlah = tk.IntVar(value=0)
        self.var_pembayaran = tk.StringVar()
        self.var_kembalian = tk.StringVar()

        self.setup_ui()

    def setup_ui(self):
        header = tk.Label(
            self.root, text="Anak Rimba - Sewa Alat Camping",
            font=("Segoe UI", 26, "bold"),
            bg="#116466", fg="#D9CAB3",
            pady=20
        )
        header.pack(fill="x")

        # Scrollable Area
        container = tk.Frame(self.root, bg="#E9F1F7")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        canvas = tk.Canvas(container, bg="#E9F1F7", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#E9F1F7")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Form Frame dalam scrollable_frame
        form_frame = tk.Frame(scrollable_frame, bg="white", bd=1, relief="ridge", padx=30, pady=20)
        form_frame.pack(fill="x", padx=10, pady=10)

        # Nama Pelanggan
        tk.Label(form_frame, text="Nama Pelanggan:", font=("Segoe UI", 13), bg="white").grid(row=0, column=0, sticky="w")
        ent_nama = tk.Entry(form_frame, textvariable=self.var_nama, font=("Segoe UI", 13), bd=2, relief="groove")
        ent_nama.grid(row=0, column=1, columnspan=2, padx=10, pady=12, sticky="ew")

        # Konfigurasi agar bisa melebar
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(2, weight=1)

        # Tanggal Pinjam & Kembali
        tk.Label(form_frame, text="Tanggal Pinjam:", font=("Segoe UI", 13), bg="white").grid(row=1, column=0, sticky="w")
        self.cal_pinjam = DateEntry(form_frame, textvariable=self.var_tanggal_pinjam, date_pattern='dd-mm-yyyy',font=("Segoe UI", 13), width=18)
        self.cal_pinjam.grid(row=1, column=1, sticky="w", pady=12, padx=10)

        tk.Label(form_frame, text="Tanggal Kembali:", font=("Segoe UI", 13), bg="white").grid(row=2, column=0, sticky="w")
        self.cal_kembali = DateEntry(form_frame, textvariable=self.var_tanggal_kembali, date_pattern='dd-mm-yyyy',font=("Segoe UI", 13), width=18)
        self.cal_kembali.grid(row=2, column=1, sticky="w", pady=12, padx=10)

        # Paket Sewa
        paket_frame = tk.LabelFrame(scrollable_frame, text="Paket Camping", font=("Segoe UI", 14, "bold"), bg="#e3f6f5", fg="#05445e", padx=20, pady=15)
        paket_frame.pack(fill="x", padx=30, pady=15)

        paket_options = ["Tidak Ada"] + [paket.nama for paket in self.daftar_paket]
        self.paket_combo = ttk.Combobox(paket_frame, values=paket_options, state="readonly", textvariable=self.var_paket_pilih, font=("Segoe UI", 12), width=30)
        self.paket_combo.grid(row=0, column=0, sticky="w", pady=8)

        tk.Label(paket_frame, text="Jumlah Paket:", font=("Segoe UI", 12), bg="#e3f6f5").grid(row=0, column=1, sticky="w", padx=15)
        spin_jumlah = tk.Spinbox(paket_frame, from_=0, to=10, textvariable=self.var_paket_jumlah, width=5, font=("Segoe UI", 12))
        spin_jumlah.grid(row=0, column=2, sticky="w", pady=8)

        # Pilih alat tambahan
        alat_frame = tk.LabelFrame(scrollable_frame, text="Alat Sewa Satuan", font=("Segoe UI", 14, "bold"), bg="#e3f6f5", fg="#05445e", padx=20, pady=15)
        alat_frame.pack(fill="x", padx=30, pady=15)

        for i, alat in enumerate(self.daftar_alat):
            tk.Label(alat_frame, text=f"{alat.nama} (Rp{alat.harga:,}/hari)", font=("Segoe UI", 12), bg="#e3f6f5").grid(row=i, column=0, sticky="w", pady=5)
            var_jml = tk.IntVar(value=0)
            spin = tk.Spinbox(alat_frame, from_=0, to=10, width=5, textvariable=var_jml, font=("Segoe UI", 12))
            spin.grid(row=i, column=1, sticky="w", pady=5, padx=15)
            self.jumlah_vars.append(var_jml)
            
        # Tombol dengan warna kontras dan hover effect
        btn_frame = tk.Frame(scrollable_frame, bg="#E9F1F7")
        btn_frame.pack(fill="x", padx=10, pady=25)

        def on_enter(e):
            e.widget['background'] = '#0b4f6c'
        def on_leave(e):
            e.widget['background'] = '#116466'

        btn_proses = tk.Button(btn_frame, text="Proses Sewa", font=("Segoe UI", 16, "bold"), bg="#116466", fg="white", relief="flat", command=self.proses_sewa)
        btn_proses.pack(side="left", expand=True, fill="x", padx=(0, 10))
        btn_proses.bind("<Enter>", on_enter)
        btn_proses.bind("<Leave>", on_leave)

        btn_reset = tk.Button(btn_frame, text="Reset", font=("Segoe UI", 16, "bold"), bg="#4FA4D9", fg="white", relief="flat", command=self.reset_form)
        btn_reset.pack(side="left", expand=True, fill="x", padx=(0, 10))

        btn_keluar = tk.Button(btn_frame, text="Keluar", font=("Segoe UI", 16, "bold"), bg="#DA1010", fg="white", relief="flat", command=self.root.destroy)
        btn_keluar.pack(side="left", expand=True, fill="x")



        # Output Text
        out_frame = tk.Frame(scrollable_frame, bg="#E9F1F7")
        out_frame.pack(fill="both", expand=True, padx=10, pady=15)
        self.txt_output = tk.Text(out_frame, font=("Consolas", 13), height=14, relief="solid", bd=1, bg="#FFFFFF")
        self.txt_output.pack(fill="both", expand=True)

        # Pembayaran
        bayar_frame = tk.Frame(scrollable_frame, bg="#f4f7f6")
        bayar_frame.pack(fill="x", padx=30, pady=10)

        tk.Label(bayar_frame, text="Bayar (Rp):", font=("Segoe UI", 14), bg="#f4f7f6").grid(row=0, column=0, sticky="w")
        self.ent_bayar = tk.Entry(bayar_frame, font=("Segoe UI", 14), textvariable=self.var_pembayaran, relief="groove", bd=2)
        self.ent_bayar.grid(row=0, column=1, padx=10, sticky="w")

        btn_bayar = tk.Button(bayar_frame, text="Bayar", font=("Segoe UI", 14, "bold"), bg="#1f6f8b", fg="white", relief="flat", command=self.proses_bayar)
        btn_bayar.grid(row=0, column=2, padx=10)

        tk.Label(bayar_frame, text="Kembalian (Rp):", font=("Segoe UI", 14), bg="#f4f7f6").grid(row=1, column=0, sticky="w", pady=8)
        self.lbl_kembalian = tk.Label(bayar_frame, textvariable=self.var_kembalian, font=("Segoe UI", 14, "bold"), bg="#f4f7f6", fg="green")
        self.lbl_kembalian.grid(row=1, column=1, sticky="w")


    def proses_sewa(self):
        nama = self.var_nama.get().strip()
        if not nama:
            messagebox.showerror("Error", "Nama pelanggan harus diisi.")
            return

        try:
            tgl_pinjam = datetime.datetime.strptime(self.var_tanggal_pinjam.get(), "%d-%m-%Y").date()
            tgl_kembali = datetime.datetime.strptime(self.var_tanggal_kembali.get(), "%d-%m-%Y").date()
        except ValueError:
            messagebox.showerror("Error", "Format tanggal salah.")
            return

        if tgl_kembali < tgl_pinjam:
            messagebox.showerror("Error", "Tanggal kembali harus setelah tanggal pinjam.")
            return

        # Ambil daftar alat yang dipilih
        items_terpilih = []
        for i, var_jml in enumerate(self.jumlah_vars):
            jumlah = var_jml.get()
            if jumlah > 0:
                items_terpilih.append((self.daftar_alat[i], jumlah))

        # Paket
        paket_nama = self.var_paket_pilih.get()
        paket_obj = None
        if paket_nama != "Tidak Ada":
            for pkt in self.daftar_paket:
                if pkt.nama == paket_nama:
                    paket_obj = pkt
                    break
        paket_jml = self.var_paket_jumlah.get()

        transaksi = TransaksiSewa(nama, tgl_pinjam, tgl_kembali, items_terpilih, paket_obj, paket_jml)

        self.transaksi_aktif = transaksi

        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, transaksi.generate_struk())

        # Reset pembayaran dan kembalian
        self.var_pembayaran.set("")
        self.var_kembalian.set("")

    def reset_form(self):
        self.var_nama.set("")
        self.var_tanggal_pinjam.set("")
        self.var_tanggal_kembali.set("")
        self.var_paket_pilih.set("Tidak Ada")
        self.var_paket_jumlah.set(0)
        self.var_pembayaran.set("")
        self.var_kembalian.set("")
        for var in self.jumlah_vars:
            var.set(0)
        self.txt_output.delete("1.0", "end")


    def proses_bayar(self):
        if not hasattr(self, 'transaksi_aktif'):
            messagebox.showerror("Error", "Proses sewa terlebih dahulu.")
            return
        try:
            bayar = int(self.var_pembayaran.get())
        except ValueError:
            messagebox.showerror("Error", "Input bayar harus berupa angka.")
            return

        total = self.transaksi_aktif.total_biaya()
        if bayar < total:
            messagebox.showwarning("Kurang Bayar", f"Bayar kurang dari total: Rp{total:,}")
            return

        kembalian = bayar - total
        self.var_kembalian.set(f"Rp{kembalian:,}")
        messagebox.showinfo("Transaksi Sukses", "Pembayaran berhasil.\nTerima kasih telah menyewa alat camping di Anak Rimba!")

if __name__ == "__main__":
    root = tk.Tk()
    app = AplikasiSewa(root)
    root.mainloop()