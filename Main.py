import Admin as ad
import Owner as ow
import Customer as pel

import pyfiglet
from tabulate import tabulate

def text_besar(text):
    ascii_art = pyfiglet.figlet_format(text)
    lines = ascii_art.split("\n")
    max_length = max(len(line) for line in lines)
    border = "+" + "-"*(max_length + 2) + "+"
    
    print(border)
    for line in lines:
        print("| " + line.ljust(max_length) + " |")
    print(border)

def main():
    while True:
        text_besar('\nWelcome to Anemone Laundry! ')
        print('1. Masuk sebagai owner') # Register
        print('2. Masuk sebagai admin') # Login
        print('3. Masuk sebagai customer')
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