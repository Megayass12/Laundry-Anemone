import psycopg2
import datetime as dt
from tabulate import tabulate

def get_connection():
    return psycopg2.connect(
        database='Anemone Abangkuh2', 
        user='postgres', 
        password='mega1234', 
        host='localhost', 
        port='5432'
    )

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
        menuAdmin()
    else:
        print("Username atau password salah!")
        login_admin()

def lihat_pelanggan():
    conn = get_connection()
    cur = conn.cursor()
    query = """
    SELECT pel.id_pelanggan, pel.nama, pel.nomor, al.detail ||','||kel.nama||','||kec.nama||','||al.kabupaten as Alamat
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
    query = """
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
    lyn.nama AS layanan_laundry,
    t.stat_bayar
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
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Menampilkan tabel transaksi pelanggan yang belum lunas
        conn = get_connection()
        cur = conn.cursor()

        query_all_transaksi = """
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
            pg.nama AS pegawai,
            tr.stat_bayar
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
        where
            stat_bayar = 'Belum Lunas'
        """
        cur.execute(query_all_transaksi)
        all_transaksi = cur.fetchall()
        if all_transaksi:
            headers = ["ID Transaksi", "Tanggal Diterima", "Tanggal Selesai", "Jenis Paket", "Layanan Laundry", "Jenis Parfum", "Metode Pembayaran", "Subtotal", "Total Berat", "Pegawai","Status Bayar"]
            print(tabulate(all_transaksi, headers=headers, tablefmt='psql'))
        else:
            print("Tidak ada transaksi yang ditemukan.")

        # Input ID Transaksi dan total weight
        transaksi_id = input("Masukkan ID Transaksi yang ingin diedit: ")
        ttl_brt = float(input("Masukkan total berat (kg): "))

        # Update ttl_brt dan subtotal di tabel transaksi
        query_update = """
        UPDATE transaksi 
        SET 
            ttl_brt = %s, 
            subtotal = (
                SELECT (CAST(harga AS INTEGER) * %s)::VARCHAR 
                FROM detail_layanan 
                WHERE id_detail = transaksi.detail_layanan_id_detail
            ) 
        WHERE id_transaksi = %s
        """
        cur.execute(query_update, (ttl_brt, ttl_brt, transaksi_id))
        
        conn.commit()
        print("Transaksi berhasil diperbarui!")
        
        # Tampilkan transaksi yang baru diupdate
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
 
def logout():
    print("Anda telah log out.")
       
def masukadmin():
    while True:
        print('\n====Selamat Datang Admin !===== ')
        login_admin()
        break

def menuAdmin():
    while True :
        print("Lanjutkan ke menu berikutnya.")
        print('1. Lihat Data Pelanggan')
        print('2. Lihat Data Transaksi')
        print('3. Edit Data Transaksi')
        print('4. Logout')
        pilihan = input('Pilih menu 1 - 4 : ')
            
        if pilihan == '1':
            lihat_pelanggan()
        elif pilihan == '2':
            lihat_transaksi()
        elif pilihan == '3':
            edit_transaksi()
        elif pilihan == '4':
            logout()
            break
        else:
            print("Pilihan tidak valid, silakan pilih angka 1 sampai 5")

# menuAdmin()