import socket
import struct

class SocketTCP:
    SYN_FLAG = 0b001
    ACK_FLAG = 0b010
    FIN_FLAG = 0b100

    header_format = "!BB" 
    header_size = struct.calcsize(header_format)

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.remote_address = None
        self.is_connected = False
        self.seq_num = 0
        self.timeout = 1.0
        self.max_payload_size = 16
        self.buffer = self.header_size + self.max_payload_size

    def settimeout(self, sec):
        self.timeout = sec
        self.sock.settimeout(sec)

    @staticmethod
    def create_segment(seq_num, syn=False, ack=False, fin=False, payload=b''):
        flags = 0
        if syn:
            flags |= SocketTCP.SYN_FLAG
        if ack:
            flags |= SocketTCP.ACK_FLAG
        if fin:
            flags |= SocketTCP.FIN_FLAG

        header = struct.pack(SocketTCP.header_format, flags, seq_num & 0xFF)
        return header + payload
    
    @staticmethod
    def parse_segment(segment):
        flags, seq_num = struct.unpack(SocketTCP.header_format, segment[:SocketTCP.header_size])
        payload = segment[SocketTCP.header_size:]

        return {
            "syn": bool(flags & SocketTCP.SYN_FLAG),
            "ack": bool(flags & SocketTCP.ACK_FLAG),
            "fin": bool(flags & SocketTCP.FIN_FLAG),
            "seq_num": seq_num,
            "payload": payload,
        }
        