import socket
import struct
import random

class SocketTCP:
    SYN_FLAG = 0b001
    ACK_FLAG = 0b010
    FIN_FLAG = 0b100

    header_format = "!BBB" 
    header_size = struct.calcsize(header_format)
    length_format = "!I" 

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.remote_address = None
        self.is_connected = False
        self.seq_num = 0
        self.ack_num = 0
        self.timeout = 20.0
        self.max_payload_size = 16
        self.buffer = self.header_size + self.max_payload_size
        self.sock.settimeout(self.timeout)
        self.remaining_bytes = 0
        self.leftover = b""

    def settimeout(self, sec):
        self.timeout = sec
        self.sock.settimeout(sec)
    
    def bind(self, address):
        self.sock.bind(address)
    
    def connect(self, address):
        self.remote_address = address
        self.seq_num = random.randint(0, 100)

        syn_segment = SocketTCP.create_segment(seq_num=self.seq_num, syn=True)
        self.sock.sendto(syn_segment, self.remote_address)

        while True:
            segment, addr = self.sock.recvfrom(self.buffer)
            parsed = SocketTCP.parse_segment(segment)

            if parsed["syn"] and parsed["ack"] and parsed["ack_num"] == self.seq_num + 1:
                self.remote_address = addr
                self.ack_num = parsed["seq_num"] + 1
                self.seq_num += 1
                break
        
        ack_segment = self.create_segment(seq_num=self.seq_num, ack_num=self.ack_num, ack=True)
        self.sock.sendto(ack_segment, self.remote_address)
        self.is_connected = True
    
    def accept(self):
        while True:
            segment, client_addr = self.sock.recvfrom(self.buffer)
            parsed = SocketTCP.parse_segment(segment)

            if parsed["syn"] and not parsed["ack"]:
                client_seq = parsed["seq_num"]

                new_socket = SocketTCP()
                new_socket.bind((self.sock.getsockname()[0], 0))
                new_socket.seq_num = random.randint(0, 100)
                new_socket.ack_num = client_seq + 1

                syn_ack = SocketTCP.create_segment(seq_num=new_socket.seq_num, ack_num=new_socket.ack_num, syn=True, ack=True)
                new_socket.sock.sendto(syn_ack, client_addr)

                while True:
                    ack_segment, ack_addr = new_socket.sock.recvfrom(new_socket.buffer)
                    parsed_ack = SocketTCP.parse_segment(ack_segment)

                    if parsed_ack["ack"] and parsed_ack["ack_num"] == new_socket.seq_num + 1:
                        new_socket.seq_num += 1
                        new_socket.is_connected = True
                        return new_socket, client_addr
    
    def send_stop_and_wait(self, payload, fin=False):
        segment = SocketTCP.create_segment(seq_num=self.seq_num, ack_num=self.ack_num, fin=fin, payload=payload)

        while True:
            self.sock.sendto(segment, self.remote_address)
            try:
                ack_segment, addr = self.sock.recvfrom(self.buffer)
            except socket.timeout:
                continue
            
            parsed = SocketTCP.parse_segment(ack_segment)
            if parsed["ack"] and parsed["ack_num"] == (self.seq_num + 1) % 256:
                self.seq_num = (self.seq_num + 1) % 256
                return
            continue
    
    def send(self, message):
        self.sock.settimeout(self.timeout)
        length_payload = struct.pack(self.length_format, len(message))
        self.send_stop_and_wait(length_payload)

        c = [
            message[i:i+self.max_payload_size] for i in range(0, len(message), self.max_payload_size)
        ] or [b'']

        for i, chunk in enumerate(c):
            last = (i == len(c) - 1)
            self.send_stop_and_wait(chunk, fin=last)

    def recv_stop_and_wait(self):
        while True:
            segment, addr = self.sock.recvfrom(self.buffer)
            parsed = SocketTCP.parse_segment(segment)

            if self.remote_address is None:
                self.remote_address = addr
            
            if parsed["seq_num"] == self.ack_num:
                new_ack_num = (self.ack_num + 1) % 256
                ack_segment = SocketTCP.create_segment(seq_num=self.seq_num, ack_num=new_ack_num, ack=True)
                self.sock.sendto(ack_segment, self.remote_address)
                self.ack_num = new_ack_num
                return parsed["payload"]
            else:
                ack_segment = SocketTCP.create_segment(seq_num=self.seq_num, ack_num=self.ack_num, ack=True)
                self.sock.sendto(ack_segment, self.remote_address)
                continue

    def recv(self, buff_size):
        self.sock.settimeout(self.timeout)
        if self.remaining_bytes == 0 and not self.leftover:
            length_payload = self.recv_stop_and_wait()
            self.remaining_bytes = struct.unpack(self.length_format, length_payload)[0]

        t = min(buff_size, self.remaining_bytes + len(self.leftover))
        while len(self.leftover) < t:
            payload = self.recv_stop_and_wait()
            self.remaining_bytes -= len(payload)
            self.leftover += payload
        
        r = min(len(self.leftover), buff_size)
        result = self.leftover[:r]
        self.leftover = self.leftover[r:]
        return result
                    
    @staticmethod
    def create_segment(seq_num, ack_num= 0, syn=False, ack=False, fin=False, payload=b''):
        flags = 0
        if syn:
            flags |= SocketTCP.SYN_FLAG
        if ack:
            flags |= SocketTCP.ACK_FLAG
        if fin:
            flags |= SocketTCP.FIN_FLAG

        header = struct.pack(SocketTCP.header_format, flags, seq_num & 0xFF, ack_num & 0xFF)
        return header + payload
    
    @staticmethod
    def parse_segment(segment):
        flags, seq_num, ack_num = struct.unpack(SocketTCP.header_format, segment[:SocketTCP.header_size])
        payload = segment[SocketTCP.header_size:]

        return {
            "syn": bool(flags & SocketTCP.SYN_FLAG),
            "ack": bool(flags & SocketTCP.ACK_FLAG),
            "fin": bool(flags & SocketTCP.FIN_FLAG),
            "seq_num": seq_num,
            "ack_num": ack_num,
            "payload": payload,
        }
        