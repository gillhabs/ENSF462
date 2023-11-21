import argparse
import RDT
import time

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Uppercase conversion receiver.")
    parser.add_argument("port", help="Port.", type=int)
    args = parser.parse_args()

    rdt = RDT.RDT("receiver", None, args.port)
    
    while True:
        msg_S = rdt.rdt_3_0_receive()
        if msg_S == "None":
            break

        print("Received: %s\n" % msg_S)

    rdt.disconnect()
