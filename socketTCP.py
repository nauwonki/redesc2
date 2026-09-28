import socket
import struct
import random
import time
import sys

class SocketTCP:
    SYN_FLAG = 0b001
    ACK_FLAG = 0b010
    FIN_FLAG = 0b100

    header_format = "!BBB" 
    header_size = struct.calcsize(header_format)
    length_format = "!I" 

    def __init__(self, debug=False):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.remote_address = None
        self.is_connected = False
        self.seq_num = 0
        self.ack_num = 0
        self.timeout = 10.0
        self.max_payload_size = 16
        self.buffer = self.header_size + self.max_payload_size
        self.sock.settimeout(self.timeout)
        self.remaining_bytes = 0
        self.leftover = b""
        self.pending_segment = None
        self.debug = debug
        self._t0 = time.time()

    def _log(self, tag, msg):
        if self.debug:
            t = time.time() - self._t0
            print(f"[{t:7.3f}s][{tag}] {msg}", file=sys.stderr)

    def settimeout(self, sec):
        self.timeout = sec
        self.sock.settimeout(sec)
    
    def bind(self, address):
        self.sock.bind(address)
    
    def connect(self, address):
        self.remote_address = address
        self.seq_num = random.randint(0, 100)
        self.sock.settimeout(self.timeout)

        syn_segment = SocketTCP.create_segment(seq_num=self.seq_num, syn=True)
        expected_ack = (self.seq_num + 1) % 256

        self._log("connect", f"enviando SYN seq={self.seq_num}")

        while True:
            self.sock.sendto(syn_segment, self.remote_address)
            try:
                segment, addr = self.sock.recvfrom(self.buffer)
            except socket.timeout:
                self._log("connect", "timeout esperando SYN+ACK")
                continue
            parsed = SocketTCP.parse_segment(segment)
            if parsed["syn"] and parsed["ack"] and parsed["ack_num"] == expected_ack:
                self.remote_address = addr
                self.ack_num = (parsed["seq_num"] + 1) % 256
                self.seq_num = expected_ack
                self._log("connect", f"SYN+ACK recibido seq={parsed['seq_num']}")
                break
            self._log("connect", "segmento inesperado, ignore")
        
        ack_segment = self.create_segment(seq_num=self.seq_num, ack_num=self.ack_num, ack=True)
        self.sock.sendto(ack_segment, self.remote_address)
        self.is_connected = True
        self._log("connect", "handshake completo")
    
    def accept(self):
        self.sock.settimeout(self.timeout)
        while True:
            try:
                segment, client_addr = self.sock.recvfrom(self.buffer)
            except socket.timeout:
                continue
            parsed = SocketTCP.parse_segment(segment)

            if parsed["syn"] and not parsed["ack"]:
                client_seq = parsed["seq_num"]

                new_socket = SocketTCP(debug=self.debug)
                new_socket.bind((self.sock.getsockname()[0], 0))
                new_socket.remote_address = client_addr
                new_socket.seq_num = random.randint(0, 100)
                new_socket.ack_num = (client_seq + 1) % 256
                new_socket.settimeout(self.timeout)
                
                syn_ack = SocketTCP.create_segment(seq_num=new_socket.seq_num, ack_num=new_socket.ack_num, syn=True, ack=True)
                expected_ack = (new_socket.seq_num + 1) % 256
                new_socket._log("accept", f"SYN recibido {client_addr}, enviando SYN+ACK")

                while True:
                    new_socket.sock.sendto(syn_ack, client_addr)
                    try:
                        reply, addr = new_socket.sock.recvfrom(new_socket.buffer)
                    except socket.timeout:
                        new_socket._log("accept", "timeout esperando ACK")
                        continue
                    parsed_ack = SocketTCP.parse_segment(reply)
                    if parsed_ack["ack"] and not parsed_ack["syn"] and parsed_ack["ack_num"] == expected_ack:
                        new_socket.seq_num = expected_ack
                        new_socket.is_connected = True
                        new_socket._log("accept", "ACK handshake recibido")
                        return new_socket, client_addr
                    if parsed_ack["seq_num"] == new_socket.ack_num:
                        new_socket.seq_num = expected_ack
                        new_socket.is_connected = True
                        new_socket.pending_segment = reply
                        new_socket._log("accept", "Caso borde: ACK perdido, datos recibidos")
                        return new_socket, client_addr
                    new_socket._log("accept", "segmento inesperado, ignore")
    
    def send_stop_and_wait(self, payload, fin=False):
        segment = SocketTCP.create_segment(seq_num=self.seq_num, ack_num=self.ack_num, fin=fin, payload=payload)
        expected_ack_num = (self.seq_num + len(payload)) % 256
        while True:
            self.sock.sendto(segment, self.remote_address)
            self._log("send", f"segmento enviado seq={self.seq_num} len={len(payload)}")
            try:
                ack_segment, addr = self.sock.recvfrom(self.buffer)
            except socket.timeout:
                self._log("send", f"TIMEOUT esperando ACK seq={self.seq_num}")
                continue
            
            parsed = SocketTCP.parse_segment(ack_segment)
            if parsed["ack"] and parsed["ack_num"] == expected_ack_num:
                self._log("send", f"ACK {expected_ack_num} recibido OK")
                self.seq_num = expected_ack_num
                return
            self._log("send", f"ACK inesperado, ignore")
            continue
    
    def send(self, message):
        self.sock.settimeout(self.timeout)
        length_payload = struct.pack(self.length_format, len(message))
        self.send_stop_and_wait(length_payload)

        c = [
            message[i:i+self.max_payload_size] for i in range(0, len(message), self.max_payload_size)
        ] or [b'']

        for i in c:
            self.send_stop_and_wait(i)

    def recv_stop_and_wait(self):
        self.sock.settimeout(self.timeout)
        while True:
            if self.pending_segment is not None:
                segment = self.pending_segment
                self.pending_segment = None
                self._log("recv", "usando segmento pendiente")
            else:
                try:
                    segment, addr = self.sock.recvfrom(self.buffer)
                except socket.timeout:
                    continue
                if self.remote_address is None:
                    self.remote_address = addr
            
            parsed = SocketTCP.parse_segment(segment)
            
            if parsed["seq_num"] == self.ack_num:
                new_ack_num = (self.ack_num + len(parsed["payload"])) % 256
                ack_segment = SocketTCP.create_segment(seq_num=self.seq_num, ack_num=new_ack_num, ack=True)
                self.sock.sendto(ack_segment, self.remote_address)
                self._log("recv", f"segmento OK seq={parsed['seq_num']} len={len(parsed['payload'])} ACK {new_ack_num}")
                self.ack_num = new_ack_num
                return parsed["payload"]
            else:
                ack_segment = SocketTCP.create_segment(seq_num=self.seq_num, ack_num=self.ack_num, ack=True)
                self.sock.sendto(ack_segment, self.remote_address)
                self._log("recv", f"Duplicado (seq={parsed['seq_num']}) esperado={self.ack_num}")
                continue

    def recv(self, buff_size):
        self.sock.settimeout(self.timeout)
        if self.remaining_bytes == 0 and not self.leftover:
            length_payload = self.recv_stop_and_wait()
            self.remaining_bytes = struct.unpack(self.length_format, length_payload)[0]
            self._log("recv", f"largo de mensaje: {self.remaining_bytes} bytes")

        t = min(buff_size, self.remaining_bytes + len(self.leftover))
        while len(self.leftover) < t:
            payload = self.recv_stop_and_wait()
            self.remaining_bytes -= len(payload)
            self.leftover += payload
        
        r = min(len(self.leftover), buff_size)
        result = self.leftover[:r]
        self.leftover = self.leftover[r:]
        self._log("recv", f"recv() retorna {len(result)} bytes (quedan {len(self.leftover)}, y {self.remaining_bytes} por llegar)")
        return result
    
    def close(self):
        self.sock.settimeout(self.timeout)
        fin_segment = SocketTCP.create_segment(seq_num=self.seq_num, ack_num=self.ack_num, fin=True)
        expected_ack_num = (self.seq_num + 1) % 256

        max_timeout = 3
        timeouts = 0
        received_finack = False
        parsed = None

        while timeouts < max_timeout:
            self.sock.sendto(fin_segment, self.remote_address)
            self._log("close", f"FIN enviado (intentos: {timeouts + 1}/{max_timeout})")
            try:
                segment, addr = self.sock.recvfrom(self.buffer)
            except socket.timeout:
                timeouts += 1
                self._log("close", f"timeout num:{timeouts} esperando FIN+ACK")
                continue
            parsed = SocketTCP.parse_segment(segment)
            if parsed["fin"] and parsed["ack"] and parsed["ack_num"] == expected_ack_num:
                received_finack = True
                self._log("close", "FIN+ACK recibido")
                break
        if received_finack:
            self.ack_num = (parsed["seq_num"] + 1) % 256
            self.seq_num = (self.seq_num + 1) % 256
            final_ack_segment = SocketTCP.create_segment(seq_num=self.seq_num, ack_num=self.ack_num, ack=True)
            for _ in range(3):
                self.sock.sendto(final_ack_segment, self.remote_address)
                self._log("close", f"ACK reenviado")
                time.sleep(self.timeout)
        else:
            self._log("close", "3 timeouts")

        self.is_connected = False
        self.sock.close()
        self._log("close", "socket cerrado")

    def recv_close(self):
        self.sock.settimeout(self.timeout)
        while True:
            try:
                segment, addr = self.sock.recvfrom(self.buffer)
            except socket.timeout:
                continue
            parsed = SocketTCP.parse_segment(segment)
            if parsed["fin"]:
                if self.remote_address is None:
                    self.remote_address = addr
                self.ack_num = (parsed["seq_num"] + 1) % 256
                self._log("recv_close", "FIN recibido")
                break
        
        finack_segment = SocketTCP.create_segment(seq_num=self.seq_num, ack_num=self.ack_num, fin=True, ack=True)
        expected_fin_num = (self.seq_num + 1) % 256

        max_timeout = 3
        timeouts = 0
        received_ack = False

        while timeouts < max_timeout:
            self.sock.sendto(finack_segment, self.remote_address)
            self._log("recv_close", f"FIN+ACK enviado (intento {timeouts + 1}/{max_timeout})")
            try:
                segment, addr = self.sock.recvfrom(self.buffer)
            except socket.timeout:
                timeouts += 1
                self._log("recv_close", f"timeout num:{timeouts}")
                continue
            parsed = SocketTCP.parse_segment(segment)
            if parsed["ack"] and not parsed["fin"] and parsed["ack_num"] == expected_fin_num:
                self.seq_num = expected_fin_num
                received_ack = True
                self._log("recv_close", "ACK final recibido")
                break
        if not received_ack:
            self._log("recv_close", "3 timeouts")
        self.is_connected = False
        self.sock.close()
        self._log("recv_close", "socket cerrado")
                    
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
        