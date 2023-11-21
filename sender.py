import json
import base64
from socket import socket, AF_INET, SOCK_DGRAM, error as socket_error, timeout
import argparse
import sys
from utils import MAX_PAYLOAD, checksum, not_corrupted

class Sender:
    # TODO: Place States

    # Initiate Receiver
    # (host, port) will be used to create UDP Server Socket
    # The server socket will be receiving information from new_udpl that
    # is reading from sender_skeleton.py
    # (dest_host, dest_port) will create a client socket
    # to connect ACK/NAK to receive.py
    # Initialize your state/variables

    def __init__(self, args):
        # How to access the variables withing args...
        self.host = args.host
        self.port = args.port
        self.dest_host = args.dest_host
        self.dest_port = args.dest_port
        self.socket = None
        self.timeout = args.timeout
        self.seq = 0
        self.buffer = []
        self.image_file = args.image_file  # Added image_file attribute

    # Run a while loop that will change status depending on FIN, etc.
    def start(self):
        try:
            self.socket = socket(AF_INET, SOCK_DGRAM)
        except socket_error:
            print('Failed to create client socket')
            sys.exit()
        try:
            self.socket.bind((self.host, self.port))
        except socket_error as msg:
            print('Bind failed. Error Code: ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()
        try:
            with open(self.image_file, 'rb') as inf:  # OPEN THE FILE
                debug_index = 0
                current_payload = inf.read(MAX_PAYLOAD)

                while len(current_payload) > 0:
                    is_fin = len(current_payload) < MAX_PAYLOAD
                    image_data = base64.b64encode(current_payload).decode('utf-8') # read the image data
                    self.buffer.append(self.make_packet(image_data, self.seq, is_fin=is_fin, index=debug_index))
                    current_payload = inf.read(MAX_PAYLOAD)
                    self.seq = 1 - self.seq
                    debug_index += 1

                self.seq = 0
                index = 0
                while index < len(self.buffer):
                    try:
                        while True:
                            print("[INFO]: Transmitting No.{} packet...".format(index))
                            is_send = self.outbound(self.buffer[index])
                            if is_send:
                                break
                        self.socket.settimeout(self.timeout)

                        # receive data from client (data, addr)
                        while True:
                            is_received = self.inbound()
                            if is_received:
                                self.seq = 1 - self.seq # alternating bit
                                break
                        # print('Server reply : ' + reply.decode())
                    except timeout:
                        print("Timeout occurs! Retransmitting...")
                        self.socket.settimeout(None)
                        continue
                    except socket_error as msg:
                        print('Error Code: ' + str(msg[0]) + ' Message ' + msg[1])
                        sys.exit()
                    index += 1
        except KeyboardInterrupt:
            self.socket.close()
            sys.exit()

        # raise NotImplementedError

    # Read inbound packet from udpl that is connected to receiver
    def inbound(self):
        payload, addr = self.socket.recvfrom(2048)
        print("Sender received ACK!")
        if not_corrupted(payload, is_from_sender=False):
            load_json = json.loads(payload) # guarantee to be decodable
            ack = load_json["acknowledgement_number"]
            if ack == self.seq:
                return True
            else:
                print("*** ACK not equal to seq! ***")
                return False
        else:
            print("*** Data corrupted! ***")
            return False
        # raise NotImplementedError

    # setup output state
    # read input from stdin for payload data
    def outbound(self, pkt):
        sndpket = pkt
        self.socket.sendto(sndpket.encode(), (self.dest_host, self.dest_port))
        return True
        # raise NotImplementedError

    # Call this function to create packet
    def make_packet(self, data, seq, is_fin=False, index=0):
        packet = {
            "FIN": int(is_fin),
            "sequence_number": seq,
            "data": data,
            "internet_checksum": self.get_checksum(data),
            "index": index
        }

        packet = json.dumps(packet)
        return packet

    def get_checksum(self, packet):
        internet_checksum = checksum(packet)
        return internet_checksum

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', dest='host', action='store', required=True, type=str)
    parser.add_argument('--port', dest='port', action='store', required=True, type=int)
    parser.add_argument('--dest_host', dest='dest_host', action='store', required=True, type=str)
    parser.add_argument('--dest_port', dest='dest_port', action='store', required=True, type=int)
    parser.add_argument('--timeout', dest='timeout', action='store', required=True, type=int)
    parser.add_argument('--image_file', dest='image_file', action='store', required=True, type=str)  # Added image_file argument
    args = parser.parse_args()

    sender = Sender(args)
    sender.start()

if __name__ == "__main__":
    main()
