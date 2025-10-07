import socket

HOST = '127.0.0.1'  # localhost
PORT = 65432        # port bebas (di atas 1024)

# Buat socket TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind ke alamat dan port
server_socket.bind((HOST, PORT))

# Listen max 1 client
server_socket.listen(1)
print(f"Server berjalan di {HOST}:{PORT}, menunggu koneksi...")

# Terima koneksi
conn, addr = server_socket.accept()
print(f"Terhubung dengan {addr}")

while True:
    data = conn.recv(1024)  # max 1024 byte
    if not data:
        break
    pesan = data.decode()
    print(f"Pesan dari client: {pesan}")

    # Balas ke client
    balasan = "Pesan diterima: " + pesan
    conn.sendall(balasan.encode())

# Tutup koneksi
conn.close()
server_socket.close()
