import socket
import struct
import sys
import time

from utils import wait_for, getCompactSize, checksum
from messages import prepareVersionMessage, preparePayload, prepareGetBlockMessage, unpackBlock

MSG_BLOCK_TYPE = 2
HOST = "51.158.74.86"
PORT = 18444
GENESIS_BLOCK_HASH = "3d2160a3b5dc4a9d62e7e66a295f70313ac808440ef7400d6c0772171ce973a5"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

print("Attempt to connect to node")

# Prepare Version Message
version_message = prepareVersionMessage(HOST, PORT)
payload = preparePayload(version_message, b'version')
# Send Version Message
s.send(payload)

print("Wait for the other node version")
# Received Version Message
wait_for(s, b'version')

print("Send 'verack' message")
payload = preparePayload(b'', b'verack')
s.send(payload)
wait_for(s, b'verack')

blocks_count = 0
next_hash = GENESIS_BLOCK_HASH

print("Asking for a new batch")
get_blocks_message = prepareGetBlockMessage(next_hash)
payload = preparePayload(get_blocks_message, b'getblocks')
s.send(payload)

l = 0
while l <= 1:
    # if 1 count it means it juste tell usa about a new block
    inv_message = wait_for(s, b'inv')[24:]
    l, offset = getCompactSize(inv_message[0:9])

print("l value is {}".format(l))

if l == 501:
    # There are giving us an extra block (probably the latest block discover)
    l = 500

for i in range(l):
    (type, hash) = struct.unpack('I32s', inv_message[offset+(36*i):offset+(36*(i+1))])
    # do we really need that ?
    assert(type == MSG_BLOCK_TYPE)
    if i == l-1:
        next_hash = hash[::-1].hex()

# We can send the message now
payload = preparePayload(inv_message, b'getdata')
s.send(payload)
count = l

log = ''

# Wait for 500 responses !
while count > 0:

    # Received Inv Message
    data = wait_for(s, b'block')

    if data == 0:
        print("ERROR : missing block")
        sys.exit()

    # verify data
    magic, command, m_length, chcksm = struct.unpack('4s12sI4s', data[0:24])
    if b'block' not in command:
        print("ERROR : wrong command")
        sys.exit()

    if len(data[24:]) != m_length:
        print("ERROR : Wrong length")
        sys.exit()


    block_message = data[24:]
    count -= 1

    hash = checksum(block_message[0:80])[::-1].hex()

    print("Count : {} - Block hash {}".format(blocks_count + 500 - count, hash))
    log += "----- {} -----\n".format(hash)


    txs = unpackBlock(block_message, False)

    for tx in txs:
        log += "{}\n".format(tx.hex())


print(log)