import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkcalendar import DateEntry
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import logging

# Logging untuk debugging
logging.basicConfig(level=logging.INFO)

# Atur tema seaborn untuk visual yang konsisten
sns.set_theme(style="darkgrid")

class DataHandler:
    """Kelas untuk mengelola pemuatan dan praproses data penjualan."""
    def __init__(self):
        self.data = None

    def load_csv(self, filepath):
        try:
            df = pd.read_csv(filepath)
            df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

            required_columns = ['tanggal', 'produk', 'jumlah_terjual', 'harga_satuan']
            missing = [col for col in required_columns if col not in df.columns]
            if missing:
                raise ValueError(f"Kolom berikut tidak ditemukan: {', '.join(missing)}")

            df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
            df['jumlah_terjual'] = pd.to_numeric(df['jumlah_terjual'], errors='coerce')
            df['harga_satuan'] = pd.to_numeric(df['harga_satuan'], errors='coerce')

            df.dropna(subset=['tanggal', 'jumlah_terjual', 'harga_satuan'], inplace=True)
            df.drop_duplicates(inplace=True)
            df['bulan'] = df['tanggal'].dt.to_period('M').astype(str)
            df['pendapatan'] = df['jumlah_terjual'] * df['harga_satuan']

            self.data = df
            return True
        except Exception as e:
            logging.error(f"Gagal memuat file: {e}")
            messagebox.showerror("Error", f"Gagal memuat file: {e}")
            return False

    def get_data(self):
        return self.data

    def filter_by_date(self, start, end):
        if self.data is not None:
            return self.data[(self.data['tanggal'] >= start) & (self.data['tanggal'] <= end)]
        return pd.DataFrame()

class SalesAnalyzer:
    """Kelas untuk melakukan analisis statistik dan ekspor data penjualan."""
    def __init__(self, data):
        self.data = data.copy()

    def total_sales_per_product(self):
        return self.data.groupby('produk')['jumlah_terjual'].sum()

    def daily_income(self):
        return self.data.groupby('tanggal')['pendapatan'].sum()

    def monthly_sales(self):
        return self.data.groupby(self.data['tanggal'].dt.to_period('M'))['jumlah_terjual'].sum()

    def monthly_income(self):
        return self.data.groupby(self.data['tanggal'].dt.to_period('M'))['pendapatan'].sum()

    def income_per_product(self):
        return self.data.groupby('produk')['pendapatan'].sum()

    def export_summary(self, file_path):
        total_sales = self.total_sales_per_product().sum()
        total_income = self.data['pendapatan'].sum()
        mean_income = np.mean(self.data['pendapatan'])
        std_income = np.std(self.data['pendapatan'])
        count_data = len(self.data)
        start_date = self.data['tanggal'].min().strftime('%Y-%m-%d')
        end_date = self.data['tanggal'].max().strftime('%Y-%m-%d')
        sales_series = self.total_sales_per_product()
        top_product = sales_series.idxmax()
        top_sales = sales_series.max()

        summary = pd.DataFrame({
            'Keterangan': [
                'Total Penjualan',
                'Total Pendapatan',
                'Rata-rata Pendapatan',
                'Standar Deviasi',
                'Jumlah Data',
                'Tanggal Awal',
                'Tanggal Akhir',
                'Produk Terlaris',
                'Jumlah Produk Terlaris'
            ],
            'Nilai': [
                total_sales,
                total_income,
                mean_income,
                std_income,
                count_data,
                start_date,
                end_date,
                top_product,
                top_sales
            ]
        })
        summary.to_csv(file_path, index=False)

    def draw_plot(self, series, kind, title, parent):
        """Visualisasi data dengan anotasi nilai dan tema seaborn."""
        for widget in parent.winfo_children():
            widget.destroy()
        fig, ax = plt.subplots(figsize=(12, 6))
        palette = sns.color_palette("pastel")
        if kind == 'pie':
            if series.shape[0] > 1:
                series.plot(kind=kind, ax=ax, autopct='%1.1f%%', labels=series.index, colors=palette)
                ax.set_ylabel('')
            else:
                ax.text(0.5, 0.5, 'Data tidak cukup untuk pie chart', ha='center')
        else:
            series.plot(kind=kind, ax=ax, color=palette)
            for i, (label, value) in enumerate(series.items()):
                ax.text(i, value, f'{value:,.0f}', ha='center', va='bottom')
        ax.set_title(title)
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        return fig

class MainAppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Analisis Penjualan")
        self.root.state('zoomed')
        self.data_handler = DataHandler()
        self.fig = None

        self.build_gui()

    def build_gui(self):
        # Tambahkan styling Treeview
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Treeview.Heading", background="#004080", foreground="white", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=24)
        style.map("Treeview", background=[("selected", "#007acc")])

        # Header frame dengan logo dan judul
        header_frame = tk.Frame(self.root, bg="#f0f0f0")
        header_frame.pack(fill=tk.X, padx=10, pady=10)


        ttk.Label(header_frame, text="📊 Dashboard Penjualan Sepatu", font=("Helvetica", 16, "bold"), background="#f0f0f0").pack(side=tk.LEFT)

        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(control_frame, text="Dari:").pack(side=tk.LEFT)
        self.start_date = DateEntry(control_frame, width=12, date_pattern='yyyy-mm-dd')
        self.start_date.pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="Sampai:").pack(side=tk.LEFT)
        self.end_date = DateEntry(control_frame, width=12, date_pattern='yyyy-mm-dd')
        self.end_date.pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="Produk:").pack(side=tk.LEFT)
        self.product_filter = ttk.Combobox(control_frame, values=["Semua"], state="readonly")
        self.product_filter.current(0)
        self.product_filter.pack(side=tk.LEFT, padx=5)
        self.product_filter.bind("<<ComboboxSelected>>", lambda e: (self.update_table(self.filter_data()), self.update_summary()))

        for text, cmd, color in [
            ("Load CSV", self.load_data, "#007bff"),
            ("Produk Terjual", self.analyze_sales, "#28a745"),
            ("Pendapatan Harian", self.analyze_income, "#17a2b8"),
            ("Simpan Statistik", self.save_summary, "#6c757d"),
            ("Simpan Grafik", self.save_graph, "#343a40")
        ]:
            btn = tk.Button(control_frame, text=text, command=cmd, bg=color, fg="white", font=("Segoe UI", 9, "bold"))
            btn.pack(side=tk.LEFT, padx=5)

        self.view_var = tk.StringVar()
        self.view_dropdown = ttk.Combobox(control_frame, textvariable=self.view_var,
            values=["Semua", "Pie Pendapatan", "Total Penjualan Bulanan", "Pendapatan Bulanan"],
            state="readonly")
        self.view_dropdown.current(0)
        self.view_dropdown.pack(side=tk.LEFT, padx=5)
        self.view_dropdown.bind("<<ComboboxSelected>>", lambda e: self.analyze_all())

        self.summary_label = ttk.Label(self.root, text="Ringkasan: Belum ada data", font=("Segoe UI", 10, "bold"))
        self.summary_label.pack(pady=(0, 10))

        self.tab_control = ttk.Notebook(self.root)
        self.table_tab = ttk.Frame(self.tab_control)
        self.canvas_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.table_tab, text="Laporan Penjualan")
        self.tab_control.add(self.canvas_tab, text="Dashboard Visual")
        self.tab_control.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas_frame = ttk.Frame(self.canvas_tab)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        self.tombol_visualisasi()

        search_frame = ttk.Frame(self.table_tab)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(search_frame, text="Cari Produk:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Cari", command=self.search_table).pack(side=tk.LEFT, padx=5)

        columns = ["tanggal", "produk", "jumlah_terjual", "harga_satuan", "pendapatan"]
        headings = ["Tanggal", "Produk", "Jumlah Terjual", "Harga Satuan", "Pendapatan"]

        self.table = ttk.Treeview(self.table_tab, columns=columns, show='headings', selectmode="browse")
        self.table.tag_configure('odd', background="#f9f9f9")
        self.table.tag_configure('even', background="white")

        for col, head in zip(columns, headings):
            anchor_pos = tk.CENTER
            self.table.heading(col, text=head, command=lambda _col=col: self.sort_table(_col, False))
            self.table.column(col, anchor=anchor_pos, width=150)

        vsb = ttk.Scrollbar(self.table_tab, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        self.table.pack(fill=tk.BOTH, expand=True, side='left')

    def update_table(self, data):
        for row in self.table.get_children():
            self.table.delete(row)
        for i, (_, row) in enumerate(data.iterrows()):
            tag = 'even' if i % 2 == 0 else 'odd'
            self.table.insert("", tk.END, values=(
                row['tanggal'].strftime('%Y-%m-%d'),
                row['produk'],
                row['jumlah_terjual'],
                row['harga_satuan'],
                row['pendapatan']
            ), tags=(tag,))
        self.update_summary()

    def update_summary(self):
        filtered = self.filter_data()
        try:
            total_transaksi = len(filtered)
            total_unit = int(filtered['jumlah_terjual'].sum())
            total_pendapatan = int(filtered['pendapatan'].sum())
            top_produk = filtered.groupby('produk')['jumlah_terjual'].sum()

            if not top_produk.empty:
                sepatu_terlaris = top_produk.idxmax()
                jumlah_terlaris = top_produk.max()
            else:
                sepatu_terlaris = '-'
                jumlah_terlaris = 0

            self.summary_label.config(
                text=f"Transaksi: {total_transaksi} | Unit Terjual: {total_unit} | "
                    f"Pendapatan: Rp {total_pendapatan:,} | "
                    f"Sepatu Terlaris: {sepatu_terlaris} ({jumlah_terlaris} unit)"
            )
        except Exception as e:
            self.summary_label.config(text=f"Ringkasan gagal dimuat: {e}")

    def search_table(self):
        keyword = self.search_var.get().lower()
        data = self.filter_data()
        if keyword:
            data = data[data['produk'].str.lower().str.contains(keyword, na=False)]
        self.update_table(data)
        self.update_summary() 

    def sort_table(self, col, reverse):
        data = [(self.table.set(k, col), k) for k in self.table.get_children()]
        try:
            data.sort(key=lambda t: float(t[0]) if t[0].replace('.', '', 1).isdigit() else t[0], reverse=reverse)
        except:
            data.sort(reverse=reverse)
        for index, (_, k) in enumerate(data):
            self.table.move(k, '', index)
        self.table.heading(col, command=lambda: self.sort_table(col, not reverse))

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path and self.data_handler.load_csv(file_path):
            messagebox.showinfo("Sukses", "Data berhasil dimuat.")
            data = self.data_handler.get_data()
            if data is not None:
                unique_products = sorted(data['produk'].dropna().unique().tolist())
                self.product_filter['values'] = ["Semua"] + unique_products
                self.product_filter.current(0)
                self.update_table(data)

                # Tambahkan ringkasan berdasarkan filter aktif
                filtered = self.filter_data()
                try:
                    total_transaksi = len(filtered)
                    total_unit = int(filtered['jumlah_terjual'].sum())
                    total_pendapatan = int(filtered['pendapatan'].sum())
                    top_produk = filtered.groupby('produk')['jumlah_terjual'].sum()

                    if not top_produk.empty:
                        sepatu_terlaris = top_produk.idxmax()
                        jumlah_terlaris = top_produk.max()
                    else:
                        sepatu_terlaris = '-'
                        jumlah_terlaris = 0

                    self.summary_label.config(
                        text=f"Transaksi: {total_transaksi} | Unit Terjual: {total_unit} | "
                            f"Pendapatan: Rp {total_pendapatan:,} | "
                            f"Sepatu Terlaris: {sepatu_terlaris} ({jumlah_terlaris} unit)"
                    )
                except Exception as e:
                    self.summary_label.config(text=f"Ringkasan gagal dimuat: {e}")
      


    def filter_data(self):
        start = pd.to_datetime(self.start_date.get_date())
        end = pd.to_datetime(self.end_date.get_date())
        data = self.data_handler.filter_by_date(start, end)
        selected_product = self.product_filter.get()
        if selected_product != "Semua":
            data = data[data['produk'] == selected_product]
        return data

    def analyze_sales(self):
        data = self.filter_data()
        if data.empty:
            messagebox.showinfo("Info", "Tidak ada data pada rentang waktu tersebut.")
            return
        try:
            analyzer = SalesAnalyzer(data)
            series = analyzer.total_sales_per_product()
            self.fig = analyzer.draw_plot(series, 'bar', 'Jumlah Terjual per Produk', self.canvas_frame)
            self.update_table(data)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def analyze_income(self):
        data = self.filter_data()
        if data.empty:
            messagebox.showinfo("Info", "Tidak ada data pada rentang waktu tersebut.")
            return
        try:
            analyzer = SalesAnalyzer(data)
            series = analyzer.daily_income()

            # Bersihkan frame lama
            for widget in self.canvas_frame.winfo_children():
                widget.destroy()

            # Plot lebih menarik
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(series.index, series.values, marker='o', linestyle='-', linewidth=2, color='#007acc', alpha=0.85)

            ax.set_title("📈 Pendapatan Harian", fontsize=14, fontweight='bold')
            ax.set_xlabel("Tanggal", fontsize=12)
            ax.set_ylabel("Pendapatan (Rp)", fontsize=12)
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.tick_params(axis='x', rotation=45)

            # Format angka Y pakai koma
            import matplotlib.ticker as mtick
            ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{int(x):,}'))

            fig.tight_layout()
            self.fig = fig
            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            self.update_table(data)
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def analyze_all(self):
        data = self.data_handler.get_data()
        if data is None or data.empty:
            messagebox.showwarning("Peringatan", "Data belum dimuat.")
            return

        analyzer = SalesAnalyzer(data)
        selected = self.view_var.get()

        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        if selected == "Pie Pendapatan":
            series = analyzer.income_per_product()
            self.fig = analyzer.draw_plot(series, 'pie', 'Kontribusi Pendapatan', self.canvas_frame)

        elif selected == "Total Penjualan Bulanan":
            series = analyzer.monthly_sales()
            self.fig = analyzer.draw_plot(series, 'bar', 'Jumlah Terjual per Bulan', self.canvas_frame)

        elif selected == "Pendapatan Bulanan":
            series = analyzer.monthly_income()

            # Bersihkan canvas
            for widget in self.canvas_frame.winfo_children():
                widget.destroy()

            fig, ax = plt.subplots(figsize=(12, 6))
            x = series.index.strftime('%b %Y')
            y = series.values

            ax.plot(x, y, marker='o', linestyle='-', linewidth=2, color='#2b83ba')
            for i, val in enumerate(y):
                ax.text(i, val, f'{int(val):,}', ha='center', va='bottom', fontsize=9)

            ax.set_title("📅 Pendapatan per Bulan", fontsize=14, fontweight='bold')
            ax.set_xlabel("Bulan", fontsize=12)
            ax.set_ylabel("Pendapatan (Rp)", fontsize=12)
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.tick_params(axis='x', rotation=30)

            import matplotlib.ticker as mtick
            ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{int(x):,}'))

            fig.tight_layout()
            self.fig = fig
            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


        else:
            fig, axs = plt.subplots(2, 2, figsize=(14, 8))

            monthly_sales = analyzer.monthly_sales()
            axs[0, 0].bar(monthly_sales.index.strftime('%b %Y'), monthly_sales.values, color=sns.color_palette("pastel"))
            axs[0, 0].set_title("Jumlah Terjual per Bulan")
            axs[0, 0].tick_params(axis='x', labelrotation=45)

            monthly_income = analyzer.monthly_income()
            axs[0, 1].plot(monthly_income.index.strftime('%b %Y'), monthly_income.values, marker='o', color='tab:blue')
            axs[0, 1].set_title("Pendapatan per Bulan")
            axs[0, 1].tick_params(axis='x', labelrotation=45)

            income_data = analyzer.income_per_product()
            if income_data.shape[0] > 1:
                axs[1, 0].pie(income_data, labels=income_data.index, autopct='%1.1f%%', colors=sns.color_palette("pastel"))
                axs[1, 0].set_title("Kontribusi Pendapatan")
                axs[1, 0].set_ylabel('')
            else:
                axs[1, 0].text(0.5, 0.5, 'Data tidak cukup untuk pie chart', ha='center')

            axs[1, 1].axis('off')

            fig.tight_layout(pad=3.0)
            self.fig = fig
            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.update_table(data)


    def save_summary(self):
        data = self.data_handler.get_data()
        if data is not None and not data.empty:
            analyzer = SalesAnalyzer(data)
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if file_path:
                analyzer.export_summary(file_path)
                messagebox.showinfo("Sukses", f"Statistik disimpan ke {file_path}")

    def save_graph(self):
        if self.fig:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
            if file_path:
                self.fig.savefig(file_path)
                messagebox.showinfo("Sukses", f"Grafik disimpan ke {file_path}")
    def tampilkan_bar_chart(self):
        data = self.filter_data()
        if data.empty:
            messagebox.showinfo("Info", "Tidak ada data untuk ditampilkan.")
            return
        series = data.groupby('produk')['jumlah_terjual'].sum().sort_values()
        self.draw_custom_chart(series, 'barh', 'Total Penjualan per Produk')

    def tampilkan_line_chart(self):
            data = self.filter_data()
            if data.empty:
                messagebox.showinfo("Info", "Tidak ada data untuk ditampilkan.")
                return
            series = data.groupby('tanggal')['pendapatan'].sum()
            self.draw_custom_chart(series, 'line', 'Pendapatan Harian')

    def tampilkan_pie_chart(self):
            data = self.filter_data()
            if data.empty:
                messagebox.showinfo("Info", "Tidak ada data untuk ditampilkan.")
                return
            series = data.groupby('produk')['jumlah_terjual'].sum()
            self.draw_custom_chart(series, 'pie', 'Proporsi Penjualan per Produk')

    def draw_custom_chart(self, series, kind, title):
            for widget in self.canvas_frame.winfo_children():
                widget.destroy()
            fig, ax = plt.subplots(figsize=(10, 5))
            if kind == 'pie':
                if series.shape[0] > 1:
                    ax.pie(series.values, labels=series.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"))
                    ax.set_ylabel('')
                else:
                    ax.text(0.5, 0.5, 'Data tidak cukup untuk pie chart', ha='center')
            elif kind == 'line':
                ax.plot(series.index, series.values, marker='o', linestyle='-', color='green')
                ax.set_xlabel(series.index.name or "")
                ax.set_ylabel("Nilai")
            elif kind == 'barh':
                ax.barh(series.index, series.values, color='skyblue')
                ax.set_xlabel("Jumlah")
            else:
                series.plot(kind=kind, ax=ax)
            ax.set_title(title)
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.fig = fig

    def tombol_visualisasi(self):
            frame = ttk.Frame(self.canvas_tab)
            frame.pack(pady=5)
            ttk.Button(frame, text="📊 Bar Chart", command=self.tampilkan_bar_chart).pack(side=tk.LEFT, padx=5)
            ttk.Button(frame, text="📈 Line Chart", command=self.tampilkan_line_chart).pack(side=tk.LEFT, padx=5)
            ttk.Button(frame, text="🥧 Pie Chart", command=self.tampilkan_pie_chart).pack(side=tk.LEFT, padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainAppGUI(root)
    root.mainloop()
