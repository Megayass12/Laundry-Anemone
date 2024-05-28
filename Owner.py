import psycopg2
import pyfiglet
def get_connection():
    return psycopg2.connect(
        database='Anemone Abangkuh', 
        user='postgres', 
        password='mega1234', 
        host='localhost', 
        port='5432'
    )

def print_large_text(text):
    ascii_art = pyfiglet.figlet_format(text)
    lines = ascii_art.split("\n")
    max_length = max(len(line) for line in lines)
    border = "+" + "-"*(max_length + 2) + "+"
    
    print(border)
    for line in lines:
        print("| " + line.ljust(max_length) + " |")
    print(border)

# Fungsi login owner
def login_owner():
    conn = get_connection()
    cur = conn.cursor()
    username = input('Masukkan username: ')
    password = input('Masukkan password: ')
    query = 'SELECT * FROM pegawai WHERE username = %s AND password = %s'
    cur.execute(query, (username, password))
    login_owner = cur.fetchone()
    cur.close()
    conn.close()
    if login_owner:
        print("Login berhasil!")
        menuowner()
    else:
        print("Username atau password salah!")
        return None

# Fungsi lihat data pelanggan
def lihat_pelanggan():
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM pelanggan"
    cur.execute(query)
    pelanggan = cur.fetchall()
    cur.close()
    conn.close()
    for i in pelanggan:
        print(i)

# Fungsi tambah akun admin
def tambah_pegawai():
    conn = get_connection()
    cur = conn.cursor()
    nama = input('Masukkan nama admin : ')
    nomor = input('Masukkan nomor admin : ')
    jabatan = input('Masukkan jabatan (owner/karyawan/admin/kurir) : ')
    alamat = input('Masukkan alamat : ')
    pw = input('Masukkan password: ')
    query = 'INSERT INTO pegawai (nama, nomor, jabatan, alamat, password) VALUES (%s, %s, %s, %s, %s)'
    cur.execute(query, (nama, nomor, jabatan, alamat, pw))
    conn.commit()
    cur.close()
    conn.close()
    print('Data admin berhasil ditambahkan')

# Fungsi lihat seluruh transaksi
def lihat_transaksi():
    conn = get_connection()
    cur = conn.cursor()
    query = '''
    select t.ttl_diterima, t.ttl_selesai, t.ttl_brt, t.subtotal, t.catatan, 
    p.nama as nama_pelanggan, pe.nama as nama_pegawai, mtd.tipe_pembayaran, prfm.nama as nama_parfum, 
    dtl.harga, pkt.nama as paket_laundry, lyn.nama as layanan_laundry from transaksi t 
    join pelanggan p on (p.id_pelanggan = t.pelanggan_id_pelanggan) 
    join pegawai pe on (pe.id_pegawai = t.pegawai_id_pegawai) 
    join mtd_bayar mtd on (mtd.id_pembayaran = t.mtd_bayar_id_pembayaran) 
    join jenis_parfum prfm on (prfm.id_parfum = t.jenis_parfum_id_parfum) 
    join detail_layanan dtl on (dtl.id_detail = t.detail_layanan_id_detail) 
    join jenis_paket pkt on (pkt.id_pencucian = dtl.jenis_paket_id_pencucian)
    join layanan_laundry lyn on (lyn.id_layanan = dtl.layanan_laundry_id_layanan)'''
    cur.execute(query)
    transaksi = cur.fetchall()
    cur.close()
    conn.close()
    for transaction in transaksi:
        print(transaction)

# Fungsi lihat data pegawai
def lihat_pegawai():
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM pegawai"
    cur.execute(query)
    pegawai = cur.fetchall()
    cur.close()
    conn.close()
    for i in pegawai:
        print(i)

# Fungsi logout
def logout():
    print("Anda telah log out")

# Fungsi menu utama
def masukowner():
    while True:
        print_large_text('\nSelamat Datang Owner !')
        login_owner()
        break

# Fungsi menu owner
def menuowner():
    while True:
        print('1. Lihat Data Customer')
        print('2. Tambahkan Akun Admin Baru')
        print('3. Lihat Data Transaksi')
        print('4. Log Out')
        pilihan = input("Masukkan menu yang dipilih:")


        if pilihan == '1':
            lihat_pelanggan()
        elif pilihan == '2':
            tambah_pegawai()
        elif pilihan == '3':
            lihat_transaksi()
        elif pilihan == '4':
            logout()
            break
        else:
            print("Pilihan tidak valid, silahkan pilih menu yang tersedia")
