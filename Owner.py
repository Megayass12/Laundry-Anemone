import psycopg2
import datetime as dt
from tabulate import tabulate
import os

def get_connection():
    return psycopg2.connect(
        database='anemonev6', 
        user='postgres', 
        password='321', 
        host='localhost', 
        port='5432'
    )

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
    os.system('cls' if os.name == 'nt' else 'clear')
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
    query = """
    SELECT pel.id_pelanggan, pel.nama, pel.nomor, pel.username, pel.password, al.detail ||','||kel.nama||','||kec.nama||','||al.kabupaten as Alamat
    from pelanggan pel
    join alamat al on al.id_rumah = pel.alamat_id_rumah 
    join kecamatan kec ON kec.id_kecamatan = al.kecamatan_id_kecamatan
    join kelurahan kel ON kel.id_kelurahan = al.kelurahan_id_kelurahan
    order by id_pelanggan asc"""
    cur.execute(query)
    pelanggan = cur.fetchall()
    col_names = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    # for i in pelanggan:
    print(tabulate(pelanggan, headers=col_names, tablefmt="pretty"))

# Fungsi tambah akun admin
def tambah_pegawai():
    conn = get_connection()
    cur = conn.cursor()
    nama = input('Masukkan nama admin : ')
    nomor = input('Masukkan nomor admin : ')
    jabatan = input('Masukkan jabatan (owner/karyawan/admin/kurir) : ')
    username = input('Masukkan username pegawai: ')
    pw = input('Masukkan password: ')
    query = 'INSERT INTO pegawai (nama, nomor, jabatan, username, password) VALUES (%s, %s, %s, %s, %s)'
    cur.execute(query, (nama, nomor, jabatan, username, pw))
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
    col_names = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    
    formatted_transaksi = []
    for transaction in transaksi:
        formatted_transaction = tuple(
            elem.strftime("%Y-%m-%d") 
            if isinstance(elem, dt.date) 
            else elem
            for elem in transaction
        )
        formatted_transaksi.append(formatted_transaction)

    print(tabulate(formatted_transaksi, headers=col_names, tablefmt="pretty"))

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
        print('='*100)
        print('====Login Owner !===='.center(100))
        print('='*100)
        login_owner()
        break

# Fungsi menu owner
def menuowner():
    while True:
        print('='*100)
        print('Selamat Datang Owner!'.center(100))
        print('='*100)
        print('1. Lihat Data Customer')
        print('2. Tambahkan Akun Admin Baru')
        print('3. Lihat Data Transaksi')
        print('4. Log Out')
        pilihan = input("Masukkan menu yang dipilih:")
        os.system('cls' if os.name == 'nt' else 'clear')

        if pilihan == '1':
            print('='*150)
            print('Data Customer'.center(150))
            print('='*150)
            lihat_pelanggan()
        elif pilihan == '2':
            print('='*150)
            print('Tambahkan Akun Pegawai'.center(150))
            print('='*150)
            tambah_pegawai()
        elif pilihan == '3':
            print('='*190)
            print('Data Transaksi'.center(190))
            print('='*190)
            lihat_transaksi()
        elif pilihan == '4':
            logout()
            break
        else:
            print("Pilihan tidak valid, silahkan pilih menu yang tersedia")

# menuowner()
