import psycopg2
import os
from tabulate import tabulate

# Register
# Login
# Lihat data akun customer
# Edit data customer
# Tambah transaksi baru
# Lihat data transaksi
# Cancel transaksi
# Logout

#Integrasi database
def get_connection():
    return psycopg2.connect(
        database='Anemone Abangkuh', 
        user='postgres', 
        password='mega1234', 
        host='localhost', 
        port='5432'
    )

#Registrasi pelanggan
def register_pelanggan():
    conn = get_connection()
    cur = conn.cursor()
    nama = input("Nama: ")
    nomor = input("Masukkan nomor hp: ")
    username = input("Username: ")
    password = input("Password: ")
    # alamat = input("Detail alamat(Nama jalan, bangunan, dsb): ")
    # kecamatan = input("Kecamatan: ")
    # kelurahan = input("Kelurahan: ")
    query = "INSERT INTO pelanggan (nama, nomor, username, password) VALUES (%s, %s, %s, %s)"
    cur.execute(query, (nama, nomor, username, password))
    conn.commit()
    cur.close()
    conn.close()

#Login pelanggan
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
        return pelanggan
    else:
        print("Username atau password salah!")
        return None

#Lihat data akunnya sendiri
def lihat_data_pelanggan(id_pelanggan):
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM pelanggan WHERE id_pelanggan = %s"
    cur.execute(query, (id_pelanggan))
    pelanggan = cur.fetchone()
    cur.close()
    conn.close()
    print(pelanggan)

#Edit data akunnya sendiri
def edit_data_pelanggan(id_pelanggan):
    conn = get_connection()
    cur = conn.cursor()
    nama = input("Nama baru: ")
    nomor = input("Nomor hp baru: ")
    username = input("Username baru: ")
    password = input("Password baru: ")
    query_update = "UPDATE pelanggan SET nama = %s, nomor = %s, username = %s, password = %s"
    cur.execute(query_update, (nama, nomor, username, password))
    conn.commit()
    query_tampilkan = "SELECT * FROM pelanggan WHERE id = %s"
    cur.execute(query_tampilkan, id_pelanggan)
    update_pelanggan = cur.fetchone()
    print("Data berhasil diperbarui!")
    print("Data pelanggan terbaru:")
    print(f"ID: {update_pelanggan[0]}")
    print(f"Nama: {update_pelanggan[1]}")
    print(f"Nomor hp: {update_pelanggan[2]}")
    print(f"Username: {update_pelanggan[3]}")
    print(f"Password: {update_pelanggan[4]}")
    cur.close()
    conn.close()
    print("Data berhasil diperbarui!")

#Fungsi tambah trasnsaki baru (masih error)
def tambah_transaksi(customer_id):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        # Ambil dan tampilkan daftar parfum
        cur.execute("SELECT * FROM jenis_parfum")
        rows = cur.fetchall()
        nama_kolom = [desc[0] for desc in cur.description]
        print(tabulate(rows, headers=nama_kolom, tablefmt='psql'))
        jenis_parfum = input("Pilih parfum: ")

        cur.execute("SELECT * FROM detail_layanan")
        rows = cur.fetchall()
        nama_kolom = [desc[0] for desc in cur.description]
        print(tabulate(rows, headers=nama_kolom, tablefmt='psql'))
        jenis_paket = input("Pilih jenis paket: ")
        tgl_pickup = input("Tanggal Pick-Up (YYYY-MM-DD): ")
        tgl_pengantaran = input("Tanggal Pengantaran (YYYY-MM-DD): ")
        metode_pembayaran = input("Input id metode pembayaran (1. Cash/2. Transfer): ")

        # Query untuk memasukkan data transaksi
        query = """
        INSERT INTO transaksi (
            jenis_parfum, detail_layanan, ttl_diterima, ttl_selesai, mtd_bayar_id_pembayaran
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        cur.execute(query, (jenis_parfum, jenis_paket, tgl_pickup, tgl_pengantaran, metode_pembayaran))

        conn.commit()
        print("Transaksi berhasil ditambahkan!")

    finally:
        cur.close()
        conn.close()

#History transaksi
def lihat_transaksi(customer_id):
    conn = get_connection()
    cur = conn.cursor()
    query = "select pg.id_pelanggan, tr.ttl_selesai, tr.subtotal, byr.tipe_pembayaran from transaksi tr join pelanggan pg on (tr.id_transaksi = pg.id_pelanggan) join mtd_bayar byr on (tr.id_transaksi = byr.id_pembayaran)"
    cur.execute(query, (customer_id,))
    transactions = cur.fetchall()
    cur.close()
    conn.close()
    for transaction in transactions:
        print(transaction)

# Fungsi batalkan transaksi
def cancel_transaction(transaction_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
SELECT 
    pl.id_pelanggan, 
    tr.id_transaksi, 
    tr.ttl_diterima, 
    tr.ttl_selesai, 
    pk.nama AS "Nama Layanan", 
    ll.nama AS "Nama Paket"
FROM 
    transaksi tr
JOIN 
    pelanggan pl ON (tr.id_transaksi = pl.id_pelanggan)
JOIN 
    detail_layanan ly ON (ly.id_detail = tr.id_transaksi)
JOIN 
    jenis_paket pk ON (pk.id_pencucian = tr.id_transaksi)
JOIN 
    layanan_laundry ll ON (ll.id_layanan = tr.id_transaksi)
""", (transaction_id,))
    rows = cur.fetchall()
    nama_kolom = [desc[0] for desc in cur.description]
    print(tabulate(rows, headers=nama_kolom, tablefmt='psql'))
    id_hapus = input("Masukkan id transaksi yang ingin dibatalkan: ")
    if not id_hapus.isdigit():
        print("ID transaksi harus berupa angka.")
        return
    query = "DELETE FROM transaksi where id_transaksi=%s"
    cur.execute(query, (id_hapus,))
    conn.commit()
    print("Transaksi berhasil dibatalkan")
    cur.close()
    conn.close()

# Fungsi log out
def logout():
    print("Anda telah log out.")

# Fungsi menu utama
def menu_pelanggan():
    while True:
        print('='*100)
        print('Selamat Datang Pelanggan!'.center(100))
        print('='*100)
        print('Silahkan Login terlebih dulu')
        print('1. Registrasi Akun')
        print('2. Login')
        print('3. Lihat informasi akun')
        print('4. Edit informasi akun')
        print('5. Tambah transaksi baru')
        print('6. Histori Transaksi')
        print('7. Batalkan transaksi')
        print('8. Log Out')
        pilihan = input("Masukkan menu yang dipilih:")
        os.system('cls')

        if pilihan == '1':
            print('='*100)
            print('Registrasi Akun Pelanggan'.center(100))
            print('='*100)
            print('Lengkapi informasi registrasi berikut ini')
            if register_pelanggan():
                print("Registrasi akun anda berhasil!")
            else:
                print("Registrasi gagal, pastikan memasukkan data yang sesuai")
        elif pilihan == '2':
            print('='*100)
            print('Login Pelanggan'.center(100))
            print('='*100)
            print('Mausukkan username dan password') 
            login_pelanggan()
        elif pilihan == '3': ####muncul none saat id pelanggan dimasukkan buat nampilkan informasi akunnya
            print('='*100)
            print('Informasi Akun Pelanggan'.center(100))
            print('='*100)
            id_pelanggan = input("Masukkan id pelanggan: ")
            lihat_data_pelanggan(id_pelanggan)
            data_pelanggan = lihat_data_pelanggan(f'{id_pelanggan}')
            os.system('cls')
            print(f'{data_pelanggan}')
        elif pilihan == '4': #masih error
            print('='*100)
            print('Edit Informasi Akun Pelanggan'.center(100))
            print('='*100)
            id_edit = input("Masukkan id yang ingin diedit:")
            edit_data_pelanggan(id_edit)
        elif pilihan == '5': #masih error
            print('='*100)
            print('Tambah transaksi'.center(100))
            print('='*100)
            id_tambah = input("Masukkan id pelanggan: ")
            try:
                customer_id = int(id_tambah)
                tambah_transaksi(customer_id)
            except ValueError:
                print("Id Pelanggan harus berupa angka")
        elif pilihan == '6': ##############
            lihat_transaksi
        elif pilihan == '7': 
            id_transaksi = input("Masukkan ID transaksi yang ingin dibatalkan: ")
            cancel_transaction(id_transaksi)
        elif pilihan == '8':
            logout()
            break
        else:
            print("Pilihan tidak valid, silahkan pilih menu yang tersedia")

# menu_pelanggan()
