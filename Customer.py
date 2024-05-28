import psycopg2
import os
from tabulate import tabulate

# Integrasi database
def get_connection():
    return psycopg2.connect(
        database='Anemone Abangkuh',
        user='postgres',
        password='mega1234',
        host='localhost',
        port='5432'
    )

# Fungsi Kecamatan
def get_kecamatan(cur):
    cur.execute("SELECT id_kecamatan, nama FROM kecamatan")
    rows = cur.fetchall()
    return rows

# Fungsi Kelurahan
def get_kelurahan(cur):
    cur.execute("SELECT id_kelurahan, nama FROM kelurahan")
    rows = cur.fetchall()
    return rows

# Fungsi register pelanggan
def register_pelanggan():
    conn = get_connection()
    cur = conn.cursor()
    try:
        nama = input("Nama: ")
        nomor = input("Masukkan nomor hp: ")
        username = input("Username: ")
        password = input("Password: ")
        jalan = input("Detail alamat (Nama jalan, bangunan, dsb): ")
        kabupaten = input("Kabupaten: ")

        # Tampilkan daftar kecamatan yang tersedia
        kecamatan_list = get_kecamatan(cur)
        nama_kolom = ["ID Kecamatan", "Nama Kecamatan"]
        print("Daftar kecamatan yang tersedia:")
        print(tabulate(kecamatan_list, headers=nama_kolom, tablefmt='psql'))
        kecamatan_id = input("Masukkan ID Kecamatan: ")

        # Tampilkan daftar kelurahan yang tersedia
        kelurahan_list = get_kelurahan(cur)
        nama_kolom = ["ID Kelurahan", "Nama Kelurahan"]
        print("Daftar kelurahan yang tersedia:")
        print(tabulate(kelurahan_list, headers=nama_kolom, tablefmt='psql'))
        kelurahan_id = input("Masukkan ID Kelurahan: ")

        # Periksa apakah kecamatan dan kelurahan yang dipilih ada di database
        cur.execute("SELECT COUNT(*) FROM kecamatan WHERE id_kecamatan = %s", (kecamatan_id,))
        if cur.fetchone()[0] == 0:
            raise ValueError("ID Kecamatan tidak valid")

        cur.execute("SELECT COUNT(*) FROM kelurahan WHERE id_kelurahan = %s", (kelurahan_id,))
        if cur.fetchone()[0] == 0:
            raise ValueError("ID Kelurahan tidak valid")

        query = """
        INSERT INTO alamat (detail, kabupaten, kecamatan_id_kecamatan, kelurahan_id_kelurahan) 
        VALUES (%s, %s, %s, %s) RETURNING id_rumah
        """
        cur.execute(query, (jalan, kabupaten, kecamatan_id, kelurahan_id))
        alamat_id = cur.fetchone()[0]

        query = """
        INSERT INTO pelanggan (nama, nomor, username, password, alamat_id_rumah) 
        VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(query, (nama, nomor, username, password, alamat_id))

        conn.commit()
        print("Registrasi akun anda berhasil!")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

# Login pelanggan
def login_pelanggan():
    conn = get_connection()
    cur = conn.cursor()
    username = input("Username: ")
    password = input("Password: ")
    query = "SELECT * FROM pelanggan WHERE username = %s AND password = %s"
    cur.execute(query, (username, password))
    pelanggan = cur.fetchone()
    cur.close()
    conn.close()
    if pelanggan:
        print("Login berhasil!")
        print(f"Selamat datang {pelanggan[1]}, ID Pelanggan anda adalah : {pelanggan[0]}!")
        return pelanggan[0]
    else:
        print("Username atau password salah!")
        return None

# Fungsi lihat data pelanggan (akunnya sendiri)
def lihat_data_pelanggan(id_pelanggan):
    conn = get_connection()
    try:
        cur = conn.cursor()
        id_pelanggan = str(id_pelanggan)
        query = """
        SELECT 
            pelanggan.id_pelanggan, 
            pelanggan.nama, 
            pelanggan.nomor, 
            pelanggan.username, 
            alamat.detail, 
            kecamatan.nama AS nama_kecamatan, 
            kelurahan.nama AS nama_kelurahan
        FROM 
            pelanggan
        JOIN 
            alamat ON pelanggan.alamat_id_rumah = alamat.id_rumah
        JOIN 
            kecamatan ON alamat.kecamatan_id_kecamatan = kecamatan.id_kecamatan
        JOIN 
            kelurahan ON alamat.kelurahan_id_kelurahan = kelurahan.id_kelurahan
        WHERE 
            pelanggan.id_pelanggan = %s
        """
        cur.execute(query, (id_pelanggan,))
        pelanggan = cur.fetchone()
        
        if pelanggan:
            print(f"ID Pelanggan: {pelanggan[0]}")
            print(f"Nama: {pelanggan[1]}")
            print(f"Nomor HP: {pelanggan[2]}")
            print(f"Username: {pelanggan[3]}")
            print(f"Alamat: {pelanggan[4]}")
            print(f"Kecamatan: {pelanggan[5]}")
            print(f"Kelurahan: {pelanggan[6]}")
        else:
            print("Pelanggan tidak ditemukan.")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
    finally:
        cur.close()
        conn.close()

# Fungsi edit data pelanggan
def edit_data_pelanggan(id_pelanggan):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Menampilkan data pelanggan yang ada
        query = "SELECT id_pelanggan, nama, nomor, username, password FROM pelanggan WHERE id_pelanggan = %s"
        cur.execute(query, (id_pelanggan,))
        data_pelanggan = cur.fetchone()
        
        if data_pelanggan:
            headers = ["ID Pelanggan", "Nama", "Nomor HP", "Username", "Password"]
            rows = [data_pelanggan]
            print(tabulate(rows, headers=headers, tablefmt='psql'))
        else:
            print("Pelanggan tidak ditemukan.")
            return
        
        # Meminta pengguna memasukkan data baru untuk diperbarui
        nama = input("Nama baru: ")
        nomor = input("Nomor HP baru: ")
        username = input("Username baru: ")
        password = input("Password baru: ")
        
        # Memperbarui data pelanggan
        query_update = "UPDATE pelanggan SET nama = %s, nomor = %s, username = %s, password = %s WHERE id_pelanggan = %s"
        cur.execute(query_update, (nama, nomor, username, password, id_pelanggan))
        conn.commit()
        os.system('cls')
        print("Data berhasil diperbarui!")
        
        # Menampilkan data pelanggan yang telah diperbarui
        cur.execute(query, (id_pelanggan,))
        updated_data_pelanggan = cur.fetchone()
        if updated_data_pelanggan():
            print(tabulate([updated_data_pelanggan], headers=headers, tablefmt='psql'))
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

# Fungsi tambah transaksi
def tambah_transaksi(customer_id):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Tampilkan daftar jenis parfum
        cur.execute("SELECT id_parfum, nama FROM jenis_parfum")
        rows = cur.fetchall()
        nama_kolom = ["ID Parfum", "Nama Parfum"]
        print(tabulate(rows, headers=nama_kolom, tablefmt='psql'))
        jenis_parfum = input("Pilih parfum (ID): ")

        # Tampilkan daftar detail layanan dengan join
        query_detail_layanan = """
        SELECT 
            dl.id_detail, 
            dl.harga, 
            jp.nama AS jenis_paket, 
            ll.nama AS layanan_laundry
        FROM 
            detail_layanan dl
        JOIN 
            jenis_paket jp ON dl.jenis_paket_id_pencucian = jp.id_pencucian
        JOIN 
            layanan_laundry ll ON dl.layanan_laundry_id_layanan = ll.id_layanan
        ORDER BY dl.id_detail
        """
        cur.execute(query_detail_layanan)
        rows = cur.fetchall()
        nama_kolom = ["ID Detail", "Harga", "Jenis Paket", "Layanan Laundry"]
        print(tabulate(rows, headers=nama_kolom, tablefmt='psql'))
        jenis_paket = input("Pilih jenis paket (ID): ")
        
        tgl_pickup = input("Tanggal Pick-Up (YYYY-MM-DD): ")
        tgl_pengantaran = input("Tanggal Pengantaran (YYYY-MM-DD): ")
        metode_pembayaran = input("Input ID metode pembayaran (1. Cash / 2. Transfer): ")

        # Insert transaksi baru
        query = """
        INSERT INTO transaksi (
            pelanggan_id_pelanggan, jenis_parfum_id_parfum, detail_layanan_id_detail, 
            ttl_diterima, ttl_selesai, mtd_bayar_id_pembayaran, subtotal, ttl_brt
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_transaksi
        """
        subtotal = "0"  # Ganti dengan perhitungan subtotal yang sesuai
        ttl_brt = 0.0   # Ganti dengan berat total yang sesuai
        cur.execute(query, (customer_id, jenis_parfum, jenis_paket, tgl_pickup, tgl_pengantaran, metode_pembayaran, subtotal, ttl_brt))
        transaksi_id = cur.fetchone()[0]
        
        conn.commit()
        print("Transaksi berhasil ditambahkan!")

        # Tampilkan transaksi yang baru ditambahkan
        query_transaksi = """
        SELECT 
            tr.id_transaksi, 
            tr.ttl_diterima, 
            tr.ttl_selesai, 
            jp.nama AS jenis_paket, 
            ll.nama AS layanan_laundry, 
            pf.nama AS jenis_parfum, 
            mb.tipe_pembayaran, 
            tr.subtotal, 
            tr.ttl_brt
        FROM 
            transaksi tr
        JOIN 
            detail_layanan dl ON tr.detail_layanan_id_detail = dl.id_detail
        JOIN 
            jenis_paket jp ON dl.jenis_paket_id_pencucian = jp.id_pencucian
        JOIN 
            layanan_laundry ll ON dl.layanan_laundry_id_layanan = ll.id_layanan
        JOIN 
            jenis_parfum pf ON tr.jenis_parfum_id_parfum = pf.id_parfum
        JOIN 
            mtd_bayar mb ON tr.mtd_bayar_id_pembayaran = mb.id_pembayaran
        WHERE 
            tr.id_transaksi = %s
        """
        cur.execute(query_transaksi, (transaksi_id,))
        transaksi_baru = cur.fetchone()
        if transaksi_baru:
            headers = ["ID Transaksi", "Tanggal Diterima", "Tanggal Selesai", "Jenis Paket", "Layanan Laundry", "Jenis Parfum", "Metode Pembayaran", "Subtotal", "Total Berat"]
            print(tabulate([transaksi_baru], headers=headers, tablefmt='psql'))
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# Fungsi lihat history transaksi
def lihat_transaksi(customer_id):
    conn = get_connection()
    cur = conn.cursor()
    query_histori = """
        SELECT 
            tr.id_transaksi AS "ID Transaksi", 
            tr.ttl_diterima AS "Tgl Diterima", 
            tr.ttl_selesai AS "Tgl Selesai", 
            jp.nama AS "Jenis Paket", 
            ll.nama AS "Layanan Laundry", 
            pf.nama AS "Jenis Parfum", 
            mb.tipe_pembayaran AS "Metode Bayar", 
            tr.subtotal AS "Subtotal", 
            tr.ttl_brt AS "Total Berat"
        FROM 
            transaksi tr
        JOIN 
            detail_layanan dl ON tr.detail_layanan_id_detail = dl.id_detail
        JOIN 
            jenis_paket jp ON dl.jenis_paket_id_pencucian = jp.id_pencucian
        JOIN 
            layanan_laundry ll ON dl.layanan_laundry_id_layanan = ll.id_layanan
        JOIN 
            jenis_parfum pf ON tr.jenis_parfum_id_parfum = pf.id_parfum
        JOIN 
            mtd_bayar mb ON tr.mtd_bayar_id_pembayaran = mb.id_pembayaran
        JOIN
            pelanggan pl ON tr.pelanggan_id_pelanggan = pl.id_pelanggan
        WHERE
            pl.id_pelanggan = %s
        """
    cur.execute(query_histori, (customer_id,))
    transactions = cur.fetchall()
    
    if not transactions:
        print("Tidak ada transaksi yang ditemukan untuk pelanggan ini.")
        return
    
    headers = ["ID Transaksi", "Tanggal Diterima", "Tanggal Selesai", "Jenis Paket", "Layanan Laundry", "Jenis Parfum", "Metode Pembayaran", "Subtotal", "Total Berat"]
    print(tabulate(transactions, headers=headers, tablefmt='psql'))

    cur.close()
    conn.close()

# Fungsi batal transaksi
def cancel_transaction(customer_id):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Tampilkan transaksi pelanggan terlebih dahulu
        query_histori = """
            SELECT 
                tr.id_transaksi AS "ID Transaksi", 
                tr.ttl_diterima AS "Tgl Diterima", 
                tr.ttl_selesai AS "Tgl Selesai", 
                jp.nama AS "Jenis Paket", 
                ll.nama AS "Layanan Laundry", 
                pf.nama AS "Jenis Parfum", 
                mb.tipe_pembayaran AS "Metode Bayar", 
                tr.subtotal AS "Subtotal", 
                tr.ttl_brt AS "Total Berat"
            FROM 
                transaksi tr
            JOIN 
                detail_layanan dl ON tr.detail_layanan_id_detail = dl.id_detail
            JOIN 
                jenis_paket jp ON dl.jenis_paket_id_pencucian = jp.id_pencucian
            JOIN 
                layanan_laundry ll ON dl.layanan_laundry_id_layanan = ll.id_layanan
            JOIN 
                jenis_parfum pf ON tr.jenis_parfum_id_parfum = pf.id_parfum
            JOIN 
                mtd_bayar mb ON tr.mtd_bayar_id_pembayaran = mb.id_pembayaran
            JOIN
                pelanggan pl ON tr.pelanggan_id_pelanggan = pl.id_pelanggan
            WHERE
                pl.id_pelanggan = %s
            """
        cur.execute(query_histori, (customer_id,))
        transactions = cur.fetchall()

        if not transactions:
            print("Tidak ada transaksi yang ditemukan untuk pelanggan ini.")
            return

        headers = ["ID Transaksi", "Tanggal Diterima", "Tanggal Selesai", "Jenis Paket", "Layanan Laundry", "Jenis Parfum", "Metode Pembayaran", "Subtotal", "Total Berat"]
        print(tabulate(transactions, headers=headers, tablefmt='psql'))

        # Meminta input ID transaksi yang ingin dibatalkan
        transaction_id = input("Masukkan ID transaksi yang ingin dibatalkan: ")

        # Melakukan penghapusan transaksi
        query_delete = "DELETE FROM transaksi WHERE id_transaksi = %s AND pelanggan_id_pelanggan = %s"
        cur.execute(query_delete, (transaction_id, customer_id))
        if cur.rowcount > 0:
            conn.commit()
            print("Transaksi berhasil dibatalkan")
        else:
            print("ID transaksi tidak ditemukan atau tidak sesuai dengan ID pelanggan.")

    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# Fungsi Log out
def logout():
    print("Anda telah log out.")

# Main menu function
def menu_pelanggan():
    logged_in_id = None
    while True:
        print('='*100)
        print('Selamat Datang Pelanggan!'.center(100))
        print('='*100)
        
        if not logged_in_id:
            print('1. Registrasi Akun')
            print('2. Login')
        else:
            print('1. Lihat informasi akun')
            print('2. Edit informasi akun')
            print('3. Tambah transaksi baru')
            print('4. Histori Transaksi')
            print('5. Batalkan transaksi')
            print('6. Log Out')
        
        pilihan = input("Masukkan menu yang dipilih: ")
        os.system('cls' if os.name == 'nt' else 'clear')

        if pilihan == '1' and not logged_in_id:
            print('='*100)
            print('Registrasi Akun Pelanggan'.center(100))
            print('='*100)
            print('Lengkapi informasi untuk registrasi berikut ini')
            register_pelanggan()
        elif pilihan == '2' and not logged_in_id:
            print('='*100)
            print('Login Pelanggan'.center(100))
            print('='*100)
            print('Masukkan username dan password Anda') 
            logged_in_id = login_pelanggan()
        elif pilihan == '1' and logged_in_id:
            print('='*100)
            print('Informasi Akun Pelanggan'.center(100))
            print('='*100)
            lihat_data_pelanggan(logged_in_id)
        elif pilihan == '2' and logged_in_id:
            print('='*100)
            print('Edit Informasi Akun Pelanggan'.center(100))
            print('='*100)
            edit_data_pelanggan(logged_in_id)
        elif pilihan == '3' and logged_in_id:
            print('='*100)
            print('Tambah transaksi'.center(100))
            print('='*100)
            tambah_transaksi(logged_in_id)
            print("Transaksi berhasil ditambahkan!")
        elif pilihan == '4' and logged_in_id:
            print('='*100)
            print('Histori Transaksi'.center(100))
            print('='*100)
            lihat_transaksi(logged_in_id)
        elif pilihan == '5' and logged_in_id:
            print('='*100)
            print('Batalkan Transaksi'.center(100))
            print('='*100)
            cancel_transaction(logged_in_id)
        elif pilihan == '6' and logged_in_id:
            logout()
            logged_in_id = None
        else:
            print("Pilihan tidak valid, silahkan pilih menu yang tersedia")
            

# menu_pelanggan()