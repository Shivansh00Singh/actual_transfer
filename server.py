
import socket
from pathlib import Path

HOST = "ip"
PORT = 5050

# Maximum number of bytes received in one chunk
BUFFER_SIZE = 1024

# Folder where received files will be stored
OUTPUT_FOLDER = Path("received_files")


# Receive metadata until a newline character is encountered
def receive_until_newline(conn):
    data = b""

    while True:
        byte = conn.recv(1)

        # Detect unexpected client disconnection
        if not byte:
            raise ConnectionError("Client disconnected unexpectedly")

        # Newline marks the end of metadata
        if byte == b"\n":
            break

        data += byte

    return data


# Receive exactly the requested number of bytes
def receive_exact(conn, size):
    data = b""

    while len(data) < size:
        chunk = conn.recv(size - len(data))

        if not chunk:
            raise ConnectionError("Client disconnected unexpectedly")

        data += chunk

    return data


# Create the output directory if it doesn't exist
OUTPUT_FOLDER.mkdir(exist_ok=True)

# Create a TCP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the IP address and port
server.bind((HOST, PORT))

# Start listening for incoming connections
server.listen(1)

print("SERVER IS LISTENING...")

try:
    # Accept one incoming client connection
    conn, addr = server.accept()

    with conn:
        print("CONNECTED TO:", addr)

        # Receive the total number of files
        total_files = int(receive_until_newline(conn))

        print("TOTAL FILES:", total_files)

        # Receive each file
        for i in range(total_files):

            print(f"\nReceiving file {i + 1}/{total_files}")

            # Receive filename length
            name_length = int(receive_until_newline(conn))

            # Receive exactly name_length bytes
            name_bytes = receive_exact(conn, name_length)

            # Convert filename bytes into a string
            filename = name_bytes.decode("utf-8")

            # Keep only the filename, not any directory path
            filename = Path(filename).name

            # Receive file size
            file_size = int(receive_until_newline(conn))

            print("Filename:", filename)
            print("File size:", file_size, "bytes")

            # Create the destination file
            output_path = OUTPUT_FOLDER / filename

            # Receive file contents in chunks
            remaining = file_size

            with open(output_path, "wb") as file:

                while remaining > 0:

                    chunk = conn.recv(min(BUFFER_SIZE, remaining))

                    if not chunk:
                        raise ConnectionError(
                            "Client disconnected during file transfer"
                        )

                    file.write(chunk)
                    remaining -= len(chunk)

            print("Successfully received:", filename)

    print("\nALL FILES RECEIVED SUCCESSFULLY!")

except (ConnectionError, ValueError, OSError) as error:
    print("TRANSFER ERROR:", error)

finally:
    server.close()
    print("SERVER CLOSED.")
