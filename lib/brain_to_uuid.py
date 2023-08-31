
import base64
from uuid import UUID

def decode_base64(data):
    # Add padding if necessary
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)
    return base64.urlsafe_b64decode(data)

def reorder_bytes(binary_data):
    # UUID format: 8-4-4-4-12 bytes
    parts = [
        binary_data[0:4][::-1],  # First 4 bytes reversed
        binary_data[4:6][::-1],  # Next 2 bytes reversed
        binary_data[6:8][::-1],  # Next 2 bytes reversed
        binary_data[8:10],       # Next 2 bytes as is
        binary_data[10:]         # Last 6 bytes as is
    ]
    return b''.join(parts)

def brain_to_uuid(brain_link):
    # Remove the "brain://" prefix if it exists
    if brain_link.startswith("brain://"):
        brain_link = brain_link[8:]
    # Decode Base64 to binary blob
    decoded_data = decode_base64(brain_link)
    # Reorder bytes and convert to UUID
    reordered_data = reorder_bytes(decoded_data)
    return str(UUID(bytes=reordered_data))

# Example usage:
if __name__ == "__main__":
    sample_links = {
        "Rene": "brain://iPI0X95R216mhlfUvsqAzg",
        "Christina of Sweden": "brain://J3UvitubjFSAx2LhR8sMpg"
    }
    for name, link in sample_links.items():
        print(f"{name}: {brain_to_uuid(link)}")

# Usage example:
#import sys
#sys.path.append('./lib/')
# from brain_to_uuid import brain_to_uuid

# sample_links = {
#    "Rene": "brain://iPI0X95R216mhlfUvsqAzg",
#    "Christina of Sweden": "brain://J3UvitubjFSAx2LhR8sMpg"
#}

#for name, link in sample_links.items():
#    print(f"{name}: {brain_to_uuid(link)}")