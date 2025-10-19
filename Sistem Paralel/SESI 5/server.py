# server.py
import socket
import threading
import time

# Konstanta Jaringan
HOST = '127.0.0.1' # IP lokal
PORT = 12345
FORMAT = 'utf-8'

# Struktur data untuk menyimpan koneksi dan nickname klien
# {klien_socket: nickname, ...}
klien_aktif = {} 
klien_lock = threading.Lock() # Lock untuk akses aman ke klien_aktif

def broadcast(pesan, koneksi_pengirim=None):
    """Mengirim pesan ke semua klien aktif."""
    with klien_lock:
        klien_list = list(klien_aktif.keys())
    
    for klien in klien_list:
        if klien != koneksi_pengirim:
            try:
                klien.send(pesan)
            except:
                # Jika gagal mengirim (klien terputus saat broadcast), hapus klien tersebut
                hapus_klien(klien)

def hapus_klien(klien_socket):
    """Menghapus klien dari daftar aktif dan memberitahu yang lain."""
    with klien_lock:
        if klien_socket in klien_aktif:
            nickname = klien_aktif[klien_socket]
            del klien_aktif[klien_socket]
            
            # Tutup socket
            try:
                klien_socket.close()
            except:
                pass 

            pesan_keluar = f"SERVER: {nickname} telah meninggalkan chat.".encode(FORMAT)
            print(pesan_keluar.decode(FORMAT))
            # Broadcast pesan keluar ke yang tersisa
            broadcast(pesan_keluar)

def handle_client(klien_socket, alamat):
    """Fungsi yang berjalan di thread terpisah untuk setiap klien."""
    # Langkah 1: Menerima nickname
    try:
        nickname = klien_socket.recv(1024).decode(FORMAT)
        if not nickname:
            hapus_klien(klien_socket)
            return

        with klien_lock:
            klien_aktif[klien_socket] = nickname
        
        pesan_masuk = f"SERVER: {nickname} bergabung ke chat!".encode(FORMAT)
        print(f"Koneksi baru dari {alamat[0]}:{alamat[1]} - Nickname: {nickname}")
        broadcast(pesan_masuk, klien_socket) # Broadcast ke semua kecuali pengirim

    except:
        hapus_klien(klien_socket)
        return

    # Langkah 2: Menerima dan mengirim pesan
    while True:
        try:
            pesan = klien_socket.recv(1024)
            if pesan:
                pesan_broadcast = f"<{nickname}> {pesan.decode(FORMAT)}".encode(FORMAT)
                print(pesan_broadcast.decode(FORMAT))
                broadcast(pesan_broadcast, klien_socket)
            else:
                # Koneksi terputus (klien mengirim data kosong)
                raise ConnectionResetError
                
        except (ConnectionResetError, socket.error):
            # Penanganan kesalahan koneksi
            hapus_klien(klien_socket)
            break
        except Exception as e:
            # Penanganan kesalahan umum
            print(f"Error pada klien {nickname}: {e}")
            hapus_klien(klien_socket)
            break

def start_server():
    """Memulai server dan mendengarkan koneksi."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Menghindari "Address already in use"
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    
    server.bind((HOST, PORT))
    server.listen()

    print(f"Server berjalan pada {HOST}:{PORT}")

    while True:
        try:
            # Menerima koneksi baru
            klien_socket, alamat = server.accept()
            
            # Mulai thread baru untuk klien
            thread_klien = threading.Thread(target=handle_client, args=(klien_socket, alamat))
            thread_klien.daemon = True
            thread_klien.start()
            
        except KeyboardInterrupt:
            print("\nServer dimatikan.")
            break
        except Exception as e:
            print(f"Terjadi error pada server: {e}")
            
    # Tutup semua koneksi saat server mati
    for klien in list(klien_aktif.keys()):
        hapus_klien(klien)
    server.close()

if __name__ == "__main__":
    start_server()