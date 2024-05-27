import psycopg2
import pyfiglet
import datetime as dt
from tabulate import tabulate

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

def login_admin():
    conn = get_connection()
    cur = conn.cursor()
    username = input("Username: ")
    password = input("Password: ")
    query = "SELECT * FROM pegawai WHERE username = %s AND password = %s"
    cur.execute(query, (username, password))
    admin = cur.fetchone()
    cur.close()
    conn.close()
    if admin:
        print("Login berhasil!")
        return admin
    else:
        print("Username atau password salah!")
        login_admin()

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

def edit_data_pelanggan():
    conn = get_connection()
    cur = conn.cursor()

    query = """
    SELECT pel.id_pelanggan, pel.nama, pel.nomor, pel.username, pel.password, al.detail ||','||kel.nama||','||kec.nama||','||al.kabupaten as Alamat
    from pelanggan pel
    join alamat al on al.id_rumah = pel.alamat_id_rumah 
    join kecamatan kec ON kec.id_kecamatan = al.kecamatan_id_kecamatan
    join kelurahan kel ON kel.id_kelurahan = al.kelurahan_id_kelurahan"""
    cur.execute(query)
    pelanggan = cur.fetchall()
    col_names = [desc[0] for desc in cur.description]
    print(tabulate(pelanggan, headers=col_names, tablefmt="pretty"))

    pelanggan_id = input("Masukkan ID customer yang ingin diedit: ")
    
    nama = input("Nama baru: ")
    nomor = input("Nomor baru: ")
    # alamat = input("Alamat baru: ")
    query = "UPDATE pelanggan SET nama = %s, nomor = %s WHERE id_pelanggan = %s"
    cur.execute(query, (nama, nomor, pelanggan_id))
    conn.commit()
    cur.close()
    conn.close()
    print("Data customer berhasil diperbarui!")

def lihat_transaksi():
    conn = get_connection()
    cur = conn.cursor()
    query = query = """
SELECT 
    t.id_transaksi,
    t.ttl_diterima, 
    t.ttl_selesai, 
    t.ttl_brt, 
    t.subtotal, 
    t.catatan, 
    p.nama AS nama_pelanggan, 
    pe.nama AS nama_pegawai, 
    mtd.tipe_pembayaran, 
    prfm.nama AS nama_parfum, 
    dtl.harga, 
    pkt.nama AS paket_laundry, 
    lyn.nama AS layanan_laundry
FROM 
    transaksi t
JOIN 
    pelanggan p ON (p.id_pelanggan = t.pelanggan_id_pelanggan)
JOIN 
    pegawai pe ON (pe.id_pegawai = t.pegawai_id_pegawai)
JOIN 
    mtd_bayar mtd ON (mtd.id_pembayaran = t.mtd_bayar_id_pembayaran)
JOIN 
    jenis_parfum prfm ON (prfm.id_parfum = t.jenis_parfum_id_parfum)
JOIN 
    detail_layanan dtl ON (dtl.id_detail = t.detail_layanan_id_detail)
JOIN 
    jenis_paket pkt ON (pkt.id_pencucian = dtl.jenis_paket_id_pencucian)
JOIN 
    layanan_laundry lyn ON (lyn.id_layanan = dtl.layanan_laundry_id_layanan)
order by id_pelanggan asc
"""
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

def edit_transaksi():
    transaction_id = input("Masukkan ID transaksi yang ingin diedit: ")
    conn = get_connection()
    cur = conn.cursor()
    berat = float(input("Masukkan berat baru: "))
    query = "UPDATE transaksi SET ttl_brt = %s WHERE id_transaksi = %s"
    cur.execute(query, (berat, transaction_id))
    conn.commit()
    cur.close()
    conn.close()
    print("Data transaksi berhasil diperbarui!")
 
def logout():
    print("Anda telah log out.")
       
def masukadmin():
    while True:
        print('\n Selamat Datang Admin!')
        login_admin()
        break

def menuAdmin():
    while True :
        print_large_text('\nSelamat Datang Admin ! ')
        print("Lanjutkan ke menu berikutnya.")
        print('1. Lihat Data Pelanggan')
        print('2. Edit Data Pelanggan')
        print('3. Lihat Data Transaksi')
        print('4. Edit Data Transaksi')
        print('5. Logout')
        pilihan = input('Pilih menu 1 - 5 : ')
            
        if pilihan == '1':
            lihat_pelanggan()
        elif pilihan == '2':
            edit_data_pelanggan()
        elif pilihan == '3':
            lihat_transaksi()
        elif pilihan == '4':
            edit_transaksi()
        elif pilihan == '5':
            logout()
            break
        else:
            print("Pilihan tidak valid, silakan pilih angka 1 sampai 5")