import time
import Network
import argparse
from time import sleep
import hashlib


class Packet:
    # the number of bytes used to store packet length
    seq_num_S_length = 10
    length_S_length = 10
    # length of md5 checksum in hex
    checksum_length = 32
    timer = 4

    def __init__(self, seq_num, msg_S):
        self.seq_num = seq_num
        self.msg_S = msg_S

    @classmethod
    def from_byte_S(cls, byte_S):
        if cls.corrupt(byte_S):
            raise RuntimeError("Corrupt")
        # extract the fields
        seq_num = int(
            byte_S[cls.length_S_length: cls.length_S_length + cls.seq_num_S_length])
        msg_S = byte_S[cls.length_S_length +
                       cls.seq_num_S_length + cls.checksum_length:]
        return cls(seq_num, msg_S)

    def get_byte_S(self):
        # convert sequence number of a byte field of seq_num_S_length bytes
        seq_num_S = str(self.seq_num).zfill(self.seq_num_S_length)
        # convert length to a byte field of length_S_length bytes
        length_S = str(
            self.length_S_length
            + len(seq_num_S)
            + self.checksum_length
            + len(self.msg_S)
        ).zfill(self.length_S_length)
        # compute the checksum
        checksum = hashlib.md5(
            (length_S + seq_num_S + self.msg_S).encode("utf-8"))
        checksum_S = checksum.hexdigest()
        # compile into a string
        return length_S + seq_num_S + checksum_S + self.msg_S

    @staticmethod
    def corrupt(byte_S):
        # extract the fields
        length_S = byte_S[0: Packet.length_S_length]
        seq_num_S = byte_S[
            Packet.length_S_length: Packet.seq_num_S_length + Packet.seq_num_S_length
        ]
        checksum_S = byte_S[
            Packet.seq_num_S_length
            + Packet.seq_num_S_length: Packet.seq_num_S_length
            + Packet.length_S_length
            + Packet.checksum_length
        ]
        msg_S = byte_S[
            Packet.seq_num_S_length + Packet.seq_num_S_length + Packet.checksum_length:
        ]

        # compute the checksum locally
        checksum = hashlib.md5(
            str(length_S + seq_num_S + msg_S).encode("utf-8"))
        computed_checksum_S = checksum.hexdigest()
        # and check if the same
        return checksum_S != computed_checksum_S


class RDT:
    # latest sequence number used in a packet
    seq_num = 1
    my_seq_num = 0

    # buffer of bytes read from network
    byte_buffer = ""
    timeout_duration = 2

    def __init__(self, role_S, receiver_S, port):
        self.network = Network.NetworkLayer(role_S, receiver_S, port)

    def disconnect(self):
        self.network.disconnect()

    def rdt_1_0_send(self, msg_S):
        p = Packet(self.seq_num, msg_S)
        print(p)
        self.seq_num += 1
        self.network.udt_send(p.get_byte_S())

    def rdt_1_0_receive(self):
        ret_S = None
        byte_S = self.network.udt_receive()
        self.byte_buffer += byte_S
        # keep extracting packets
        while True:
            # check if we have received enough bytes
            if len(self.byte_buffer) < Packet.length_S_length:
                return ret_S  # not enough bytes to read packet length
            # extract length of packet
            length = int(self.byte_buffer[: Packet.length_S_length])
            if len(self.byte_buffer) < length:
                return ret_S  # not enough bytes to read the whole packet
            # create packet from buffer content and add to return string
            p = Packet.from_byte_S(self.byte_buffer[0:length])
            ret_S = p.msg_S if (ret_S is None) else ret_S + p.msg_S
            # remove the packet bytes from the buffer
            self.byte_buffer = self.byte_buffer[length:]
            # if this was the last packet, will return on the next iteration



    def rdt_3_0_send(self, msg_S):
        while True:
            send_packet = Packet(self.seq_num, msg_S)
            self.network.udt_send(send_packet.get_byte_S())
            print(f"Send message {self.seq_num}")

            start_time = time.time()
            while time.time() - start_time < self.timeout_duration:
                ack_packet = self.network.udt_receive()
                if ack_packet:
                    try:
                        received_ack = Packet.from_byte_S(ack_packet)
                        if received_ack.seq_num == self.seq_num:
                            print(
                                f"Receive ACK {received_ack.seq_num}. Message successfully sent!")
                            self.seq_num = 1 - self.seq_num
                            return
                        else:
                            print(
                                f"Receive ACK {received_ack.seq_num}. Resend message {self.seq_num}")
                            time.sleep(0.5)
                    except RuntimeError:
                        print(
                            f"Corruption detected in ACK. Resend message {self.seq_num}")
                        break

            if time.time() - start_time >= self.timeout_duration:
                print(f"Timeout! Resend message {self.seq_num}")



    def rdt_3_0_receive(self):
        while True:
            received_byte_S = self.network.udt_receive()
            if received_byte_S:
                try:
                    received_packet = Packet.from_byte_S(received_byte_S)

                    if received_packet.seq_num == self.seq_num:
                        print(
                            f"Receive message {received_packet.seq_num}. Send ACK {received_packet.seq_num}")
                        send_ack_packet = Packet(
                            received_packet.seq_num, "ACK")
                        self.network.udt_send(send_ack_packet.get_byte_S())
                        self.seq_num = 1 - self.seq_num
                        return received_packet.msg_S
                    else:
                        print(
                            f"Duplicate message {received_packet.seq_num}. Send ACK {1 - received_packet.seq_num}")
                        send_ack_packet = Packet(
                            1 - received_packet.seq_num, "ACK")
                        self.network.udt_send(send_ack_packet.get_byte_S())

                except RuntimeError:
                    print(f"Corruption detected! Send ACK {1 - self.seq_num}")
                    send_ack_packet = Packet(1 - self.seq_num, "ACK")
                    self.network.udt_send(send_ack_packet.get_byte_S())



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RDT implementation.")
    parser.add_argument(
        "role",
        help="Role is either sender or receiver.",
        choices=["sender", "receiver"],
    )
    parser.add_argument("receiver", help="receiver.")
    parser.add_argument("port", help="Port.", type=int)
    args = parser.parse_args()

    rdt = RDT(args.role, args.receiver, args.port)
    if args.role == "sender":
        rdt.rdt_1_0_send("MSG_FROM_SENDER")
        sleep(2)
        print(rdt.rdt_1_0_receive())
        rdt.disconnect()

    else:
        sleep(1)
        print(rdt.rdt_1_0_receive())
        rdt.rdt_1_0_send("MSG_FROM_RECEIVER")
        rdt.disconnect()
