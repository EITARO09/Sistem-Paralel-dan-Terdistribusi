# client.py
import socket
import threading
import sys
import time

# Konstanta Jaringan
HOST = '127.0.0.1' 
PORT = 12345
FORMAT = 'utf-8'

def receive_messages(klien_socket):
    """Thread terpisah untuk terus menerima pesan dari server."""
    while True:
        try:
            pesan = klien_socket.recv(1024).decode(FORMAT)
            if pesan:
                # Membersihkan baris input yang sedang diketik
                sys.stdout.write('\r' + ' ' * 80 + '\r') 
                sys.stdout.flush()
                print(pesan)
                sys.stdout.write("Anda: ")
                sys.stdout.flush()
            else:
                # Server menutup koneksi atau mengirim data kosong
                print("\nSERVER: Koneksi terputus. Menutup klien...")
                klien_socket.close()
                sys.exit(0)
                
        # Penanganan Koneksi Terputus
        except (ConnectionResetError, ConnectionAbortedError, socket.error):
            print("\nSERVER: Koneksi terputus. Menutup klien...")
            klien_socket.close()
            sys.exit(0)
        except Exception as e:
            print(f"\nTerjadi kesalahan tidak terduga: {e}. Menutup klien...")
            klien_socket.close()
            sys.exit(0)

def start_client():
    """Memulai klien dan menghubungkan ke server."""
    nickname = input("Masukkan nickname Anda: ")
    
    klien = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        klien.connect((HOST, PORT))
        print(f"Terhubung ke server {HOST}:{PORT}. Ketik 'exit' untuk keluar.")
    except socket.error as e:
        print(f"Gagal terhubung ke server {HOST}:{PORT}: {e}")
        return

    # Kirim nickname segera setelah terhubung
    klien.send(nickname.encode(FORMAT))

    # Mulai thread penerima pesan
    thread_terima = threading.Thread(target=receive_messages, args=(klien,))
    thread_terima.daemon = True
    thread_terima.start()

    # Logika pengiriman pesan (di thread utama)
    while True:
        try:
            pesan_input = input("Anda: ")
            
            if pesan_input.lower() == 'exit':
                print("Keluar dari chat...")
                break
                
            pesan_terkirim = pesan_input.encode(FORMAT)
            klien.send(pesan_terkirim)
            
        except EOFError:
            # Ditekan Ctrl+D (Linux/macOS) atau sejenisnya
            print("\nKlien keluar.")
            break
        except Exception as e:
            # Gagal mengirim (mungkin koneksi sudah terputus)
            print(f"Gagal mengirim pesan: {e}")
            break

    klien.close()

if __name__ == "__main__":
    start_client()