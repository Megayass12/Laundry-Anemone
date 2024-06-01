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
        
        # Display available perfumes
        cur.execute("SELECT id_parfum, nama FROM jenis_parfum")
        rows = cur.fetchall()
        nama_kolom = ["ID Parfum", "Nama Parfum"]
        print(tabulate(rows, headers=nama_kolom, tablefmt='psql'))
        jenis_parfum = input("Pilih parfum (ID): ")

        # Display available service details
        query_detail_layanan = """
        SELECT 
            dl.id_detail, 
            dl.harga, 
            jp.nama AS jenis_paket, 
            ll.nama AS layanan_laundry, ll.waktu as Waktu
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
        nama_kolom = ["ID Detail", "Harga", "Jenis Paket", "Layanan Laundry","Waktu"]
        print(tabulate(rows, headers=nama_kolom, tablefmt='psql'))
        jenis_paket = input("Pilih jenis paket (ID): ")
        
        tgl_pickup = input("Tanggal Pick-Up (YYYY-MM-DD): ")
        tgl_pengantaran = input("Tanggal Pengantaran (YYYY-MM-DD): ")

        # Display available payment methods
        # cur.execute("SELECT id_pembayaran, tipe_pembayaran FROM mtd_bayar")
        # rows = cur.fetchall()
        # nama_kolom = ["ID Pembayaran", "Tipe Pembayaran"]
        # print(tabulate(rows, headers=nama_kolom, tablefmt='psql'))
        metode = [
            ["1","Cash"],
            ["2", "Transfer"]
        ]
        print(tabulate(metode, headers=["Id", "Metode"], tablefmt="grid"))
        metode_pembayaran = input("Pilih metode pembayaran (ID): ")

        # Display available employees
        # cur.execute("SELECT id_pegawai, nama FROM pegawai Where jabatan = 'Admin'")
        # rows = cur.fetchall()
        # nama_kolom = ["ID Pegawai", "Nama Pegawai"]
        # print(tabulate(rows, headers=nama_kolom, tablefmt='psql'))
        # pegawai_id = input("Pilih pegawai kasir (ID): ")

        # Insert new transaction
        query = """
        INSERT INTO transaksi (
            pelanggan_id_pelanggan, jenis_parfum_id_parfum, detail_layanan_id_detail, 
            ttl_diterima, ttl_selesai, mtd_bayar_id_pembayaran, subtotal, ttl_brt, pegawai_id_pegawai
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_transaksi
        """
        subtotal = 0  # Replace with appropriate subtotal calculation
        ttl_brt = 0.0  # Replace with appropriate total weight calculation
        cur.execute(query, (customer_id, jenis_parfum, jenis_paket, tgl_pickup, tgl_pengantaran, metode_pembayaran, subtotal, ttl_brt))
        transaksi_id = cur.fetchone()[0]
        
        conn.commit()
        print("Transaksi berhasil ditambahkan!")

        # Display the newly added transaction
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
            tr.ttl_brt, 
            pg.nama AS pegawai
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
            pegawai pg ON tr.pegawai_id_pegawai = pg.id_pegawai
        WHERE 
            tr.id_transaksi = %s
        """
        cur.execute(query_transaksi, (transaksi_id,))
        transaksi_baru = cur.fetchone()
        if transaksi_baru:
            headers = ["ID Transaksi", "Tanggal Diterima", "Tanggal Selesai", "Jenis Paket", "Layanan Laundry", "Jenis Parfum", "Metode Pembayaran", "Subtotal", "Total Berat", "Pegawai"]
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
            tr.ttl_brt AS "Total Berat",
            tr.stat_bayar as "status pembayaran"
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
            pl.id_pelanggan = %s and stat_bayar = 'Lunas'
        """
    cur.execute(query_histori, (customer_id,))
    transactions = cur.fetchall()
    
    if not transactions:
        print("Tidak ada transaksi yang ditemukan untuk pelanggan ini.")
        return
    
    headers = ["ID Transaksi", "Tanggal Diterima", "Tanggal Selesai", "Jenis Paket", "Layanan Laundry", "Jenis Parfum", "Metode Pembayaran", "Subtotal", "Total Berat","status"]
    print(tabulate(transactions, headers=headers, tablefmt='psql'))

    cur.close()
    conn.close()

def bayar_transaksi(customer_id):
    conn = None
    cur = None
    try:
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
            tr.ttl_brt AS "Total Berat",
            tr.stat_bayar as "status pembayaran"
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
            pl.id_pelanggan = %s and stat_bayar is null
        """
        cur.execute(query_histori, (customer_id,))
        transactions = cur.fetchall()
        
        if not transactions:
            print("Tidak ada transaksi yang ditemukan untuk pelanggan ini.")
            return
        
        headers = ["ID Transaksi", "Tanggal Diterima", "Tanggal Selesai", "Jenis Paket", "Layanan Laundry", "Jenis Parfum", "Metode Pembayaran", "Subtotal", "Total Berat","status"]
        print(tabulate(transactions, headers=headers, tablefmt='psql'))
            
        # Input the transaction ID
        transaksi_id = input("Masukkan ID transaksi yang hendak dibayar: ")

        # Fetch the transaction details
        query = """
        SELECT 
            tr.id_transaksi, 
            tr.subtotal, 
            tr.ttl_brt
        FROM 
            transaksi tr
        WHERE 
            tr.id_transaksi = %s
        """
        cur.execute(query, (transaksi_id,))
        transaksi = cur.fetchone()
        
        if not transaksi:
            print(f"Transaksi dengan ID {transaksi_id} tidak ditemukan.")
            return
        
        id_transaksi, subtotal, total_berat = transaksi
        print(f"Subtotal: {subtotal}, Total Berat: {total_berat}")
        
        # Display available payment methods
        cur.execute("SELECT id_pembayaran, tipe_pembayaran FROM mtd_bayar")
        rows = cur.fetchall()
        nama_kolom = ["ID Pembayaran", "Tipe Pembayaran"]
        print(tabulate(rows, headers=nama_kolom, tablefmt='psql'))
        metode_pembayaran = input("Pilih metode pembayaran (ID): ")
        
        # Process payment based on the chosen method
        if metode_pembayaran == '1':  # Assuming '1' is for cash
            amount_due = float(input("Masukkan nominal yang harus dibayar: "))
            subtotal = float(subtotal)
            if amount_due == subtotal:
                confirm = input(f"Konfirmasi pembayaran sebesar {amount_due} (yes/no): ")
                if confirm.lower() == 'yes':
                    query = """
                    UPDATE transaksi
                    SET 
                        status_pembayaran = 'Lunas',
                        mtd_bayar_id_pembayaran = %s
                    WHERE 
                        id_transaksi = %s
                    """
                    cur.execute(query, (metode_pembayaran, id_transaksi))
                    conn.commit()
                    print("Pembayaran berhasil diproses.")
                else:
                    print("Pembayaran dibatalkan.")
            elif amount_due > subtotal:
                change = amount_due - subtotal
                confirm = input(f"Nominal yang dibayar melebihi subtotal. Kembalian: {change}. Konfirmasi pembayaran (yes/no): ")
                if confirm.lower() == 'yes':
                    query = """
                    UPDATE transaksi
                    SET 
                        stat_bayar = 'Lunas',
                        mtd_bayar_id_pembayaran = %s
                    WHERE 
                        id_transaksi = %s
                    """
                    cur.execute(query, (metode_pembayaran, id_transaksi))
                    conn.commit()
                    print(f"Pembayaran berhasil diproses. Kembalian: {change}.")
                else:
                    print("Pembayaran dibatalkan.")
            else:
                print("Nominal yang dimasukkan kurang dari subtotal. Transaksi gagal.")
        elif metode_pembayaran == '2':  # Assuming '2' is for transfer
            rekening_number = input("Masukkan nomor rekening Anda: ")
            confirm = input(f"Konfirmasi pembayaran dengan nomor rekening {rekening_number} (yes/no): ")
            if confirm.lower() == 'yes':
                query = """
                UPDATE transaksi
                SET 
                    stat_bayar = 'Lunas',
                    mtd_bayar_id_pembayaran = %s
                WHERE 
                    id_transaksi = %s
                """
                cur.execute(query, (metode_pembayaran, id_transaksi))
                conn.commit()
                print("Pembayaran berhasil diproses.")
            else:
                print("Pembayaran dibatalkan.")
        else:
            print("Metode pembayaran tidak valid.")
            
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
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
            tr.ttl_brt AS "Total Berat",
            tr.stat_bayar as "status pembayaran"
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
            pl.id_pelanggan = %s and stat_bayar is null
        """
        cur.execute(query_histori, (customer_id,))
        transactions = cur.fetchall()
        
        if not transactions:
            print("Tidak ada transaksi yang ditemukan untuk pelanggan ini.")
            return
        
        headers = ["ID Transaksi", "Tanggal Diterima", "Tanggal Selesai", "Jenis Paket", "Layanan Laundry", "Jenis Parfum", "Metode Pembayaran", "Subtotal", "Total Berat","status"]
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

# fungsi konfirmasi Transaksi
def proses_pembayaran(customer_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        transaksi_id = input("Masukkan ID Transaksi: ")
        metode_pembayaran = input("Pilih metode pembayaran (1. Cash / 2. Transfer): ")

        # Ambil detail transaksi
        cur.execute("""
            SELECT t.id_transaksi, t.subtotal FROM transaksi t 
            WHERE t.id_transaksi = %s AND t.pelanggan_id_pelanggan = %s
        """, (transaksi_id, customer_id))
        transaksi = cur.fetchone()
        if not transaksi:
            print("Transaksi tidak ditemukan atau bukan milik Anda.")
            return

        id_transaksi, subtotal = transaksi

        if metode_pembayaran == '1':  # Cash
            nominal = (input("Masukkan nominal pembayaran: "))
            if nominal < (subtotal):
                print("Nominal tidak mencukupi.")
                return
            else:
                kembalian = nominal - (subtotal)
                print(f"Pembayaran berhasil. Kembalian Anda: {kembalian}")

                # Insert into cash
                cur.execute("""
                    INSERT INTO cash (id_pembayaran, nominal, kembalian)
                    VALUES (%s, %s, %s)
                """, (id_transaksi, str(nominal), str(kembalian)))

        elif metode_pembayaran == '2':  # Transfer
            no_rekening = input("Masukkan nomor rekening: ")
            print("Pembayaran via transfer berhasil.")

            # Insert into transfer
            cur.execute("""
                INSERT INTO transfer (id_pembayaran, no_rek)
                VALUES (%s, %s)
            """, (id_transaksi, no_rekening))

        else:
            print("Metode pembayaran tidak valid.")
            return
        
        # Update status pembayaran di database
        cur.execute("""
            UPDATE transaksi SET status_pembayaran = %s 
            WHERE id_transaksi = %s
        """, ('Lunas', id_transaksi))
        conn.commit()
        print("Transaksi berhasil diperbarui!")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cur.close()
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
            print('6. Pembayaran Transaksi')
            print('7. Log Out')
        
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
            print('='*100)
            print('Pembayaran Transaksi'.center(100))
            print('='*100)
            bayar_transaksi(logged_in_id)
        elif pilihan == '7' and logged_in_id:
            logout()
            break
        else:
            print("Pilihan tidak valid, silahkan pilih menu yang tersedia")