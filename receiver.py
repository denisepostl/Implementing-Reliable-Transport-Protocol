import json
from socket import socket, AF_INET, SOCK_DGRAM, error as socket_error
import argparse
import sys
import base64
from utils import MAX_PAYLOAD, OUTPUT_FILE, checksum, not_corrupted

class Receiver:
    # TODO: Place States

    # Initiate Receiver
    # (host, port) will be used to create UDP Server Socket
    # The server socket will be receiving information from new_udpl that
    # is reading from sender_skeleton.py
    # (dest_host, dest_port) will create a client socket
    # to connect ACK/NAK to sender_skeleton.py
    # Initialize your state/variables
    def __init__(self, args):
        # How to access the variables within args...
        self.host = args.host
        self.port = args.port
        self.dest_host = args.dest_host
        self.dest_port = args.dest_port
        self.socket = None
        self.ack = 0
        self.recv_seq = 0
        self.FIN = 0
        self.output_file = open(OUTPUT_FILE, mode='wb') # output file
        # raise NotImplementedError

    # Run a while loop that will change status depending on FIN flag
    def start(self):
        try:
            self.socket = socket(AF_INET, SOCK_DGRAM)
        except socket_error as msg:
            print('Failed to create socket. Error Code: ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()

        try:
            self.socket.bind((self.host, self.port))
        except socket_error as msg:
            print('Bind failed. Error Code: ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()
        print("Server socket created and bind to host {} and port {}!".format(self.host, self.port))

        try:
            while True:
                # for receiver, it will send packets no matter in what situation
                no_error = self.inbound() # data will be delivered if no pronblem
                self.outbound(self.make_packet())
                if no_error:
                    self.ack = 1 - self.ack # alternating bit

                if self.FIN == 1:
                    print("*** FIN received, closing the server......")
                    self.output_file.close()
                    raise KeyboardInterrupt
        except KeyboardInterrupt:
            self.socket.close()
            sys.exit()

    # Create your outbound packet to send to sender_skeleton.py
    # Refer to this:
    # https://www.binarytides.com/programming-udp-sockets-in-python/
    def outbound(self, pkt):
        sndpket = pkt.encode()
        self.socket.sendto(sndpket, (self.dest_host, self.dest_port))
        return True
    


    # TODO: This method is called when receive.py gets a packet from sender_skeleton.py
    # Check for the following
    # 1- Is the checksum correct?
    # 2- Check sequence number/ACK number
    # 3- Check if sender_skeleton.py wants to terminate
    
    # Refer to this:
    # https://www.binarytides.com/programming-udp-sockets-in-python/
    def inbound(self):
        print("-------Received packets from sender-----------")
        payload, addr = self.socket.recvfrom(2048)
        if not_corrupted(payload, is_from_sender=True):
            load_json = json.loads(payload)
            seq = load_json["sequence_number"]
            self.recv_seq = seq
            index = load_json["index"]
            print("[INFO]: Packet index at", index)
            if seq == self.ack:
                data = base64.b64decode(load_json["data"])
                print(data)
                self.deliver_data(data)
                if load_json["FIN"] == 1:
                    self.FIN = 1
                return True
            else:
                print("*** seq not equal to ack in server! ***")
                return False
        else:
            print("*** data corrupted! ***")
            return False

    def make_packet(self):
        recv_seq = self.recv_seq
        packet = {
            "acknowledgement_number": recv_seq,
            "internet_checksum": self.get_checksum(recv_seq)
        }
        packet = json.dumps(packet)
        return packet

    def get_checksum(self, packet):
        internet_checksum = checksum(packet)
        return internet_checksum

    def deliver_data(self, data):
        self.output_file.write(data)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', dest='host', action='store', required=True, type=str)
    parser.add_argument('--port', dest='port', action='store', required=True, type=int)
    parser.add_argument('--dest_host', dest='dest_host', action='store', required=True, type=str)
    parser.add_argument('--dest_port', dest='dest_port', action='store', required=True, type=int)
    args = parser.parse_args()

    receiver = Receiver(args)
    receiver.start()

if __name__ == "__main__":
    main()
