import admin as ad
import owner as ow
import pelanggan as pel
from tabulate import tabulate



def main():
    while True:
        print('='*100)
        print('==== Welcome to Anemone Laundry!==== '.center(100))
        print('='*100)
        print('1. Masuk sebagai owner') # Register
        print('2. Masuk sebagai admin') # Login
        print('3. Masuk sebagai pelanggan')
        masuk = input(f'Pilih opsi di atas : ')
        
        if masuk == '1':
            ow.masukowner()  #jgn lupa kurung hehe
        elif masuk == '2':
            ad.masukadmin()
        elif masuk == '3':
            pel.menu_pelanggan()
        else:
            print("Pilihan tidak valid, silakan pilih angka 1 sampai 3")
if __name__ == '__main__':
    main()
