
import socket
from pathlib import Path

# Server configuration
HOST = "server_ip"
PORT = 5050

# Step 1: Locate the folder containing JPG and MP4 files
folder_path = Path("25bcs164")

# Store the paths of files that we want to transfer
files = []

# Step 2: Find all JPG and MP4 files inside the folder
for file in folder_path.iterdir():

    # Check that the item is a file and has an allowed extension
    if file.is_file() and file.suffix.lower() in (".jpg", ".mp4"):
        files.append(file)

# Display the total number of files
print("Total Files:", len(files))

# Display each filename and its size
for file in files:
    print("Filename:", file.name)
    print("Size:", file.stat().st_size, "bytes")


# Step 3: Create a TCP socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server (TCP three-way handshake happens here)
client.connect((HOST, PORT))

# Step 4: Send the total number of files
# encode() converts the string into bytes.
# \n marks the end of this metadata field.
client.sendall(str(len(files)).encode() + b"\n")


# Step 5: Transfer each file
for file in files:

    # Convert the filename into bytes
    name_bytes = file.name.encode()

    # Calculate the filename length in bytes
    name_length = len(name_bytes)

    # Send the filename length followed by a newline delimiter
    client.sendall(str(name_length).encode() + b"\n")

    # Send the actual filename
    client.sendall(name_bytes)

    # Get the size of the current file in bytes
    size = file.stat().st_size

    # Send the file size followed by a newline delimiter
    client.sendall(str(size).encode() + b"\n")

    # Open the file in binary read mode
    with open(file, "rb") as f:

        # Read and transmit the file in chunks of 1024 bytes
        while True:

            data = f.read(1024)

            # An empty byte string means the end of the file
            if not data:
                break

            # Send the current chunk to the server
            client.sendall(data)


# Step 6: Close the TCP connection
client.close()

print("File transfer completed from client.")
