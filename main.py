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
