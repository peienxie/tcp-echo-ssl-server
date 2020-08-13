import socket
import ssl
import logging
import select
import queue

def echo_server():
    HOST, PORT = "0.0.0.0", 8787
    CERT_FILE = "cert.pem"
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(certfile=CERT_FILE)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client = None

    try:
        server.bind((HOST, PORT))
        server.listen(5)
        logging.info("mid_server is on: %s:%s" % (HOST, PORT))
    except Exception as e:
        raise

    inputs = [server, ]
    outputs = []
    messages_dict = dict()
    while inputs:
        # logging.info(f"\
        #     \ninput: {[s.getpeername() if s is not mid_server else host for s in inputs]}\
        #     \noutputs: {[s.getpeername() for s in outputs]}\
        #     \nmessages_dict: {[s.getpeername() for s in messages_dict.keys()]}")
        # logging.info("[LISTEN] Waitting for new event")
        readable, writable, exceptional = select.select(
            inputs, outputs, inputs, 1)

        for s in readable:
            if s is server:
                client, addr = s.accept()
                client = context.wrap_socket(client, server_side=True)
                client.setblocking(0)
                logging.info(f"[OPEN] connected from {addr[0]}:{addr[1]}")
                inputs.append(client)
                messages_dict[client] = queue.Queue()
            else:
                try:
                    data = s.recv(2048)
                    if data:
                        logging.info(f"[RECV] received data from {s.getpeername()}:")
                        logging.info(f"\t({len(data)}) / {data.hex()}")
                        logging.info(f"\t({len(data)}) / {data}")

                        messages_dict[client].put(data)
                        outputs.append(client)
                    else:
                        raise Exception
                except Exception:
                    logging.info(
                        f"[CLOSE] client {s.getpeername()} disconnected")
                    inputs.remove(s)
                    if s in outputs:
                        outputs.remove(s)
                    del messages_dict[s]
                    s.close()
                    

        for s in writable:
            try:
                msg = messages_dict[s].get_nowait()
            except queue.Empty as e:
                if s in outputs:
                    outputs.remove(s)
                # logging.info("[SEND] no data in queue to be sent")
            except KeyError:
                if s in outputs:
                    outputs.remove(s)
            else:
                s.send(msg)
                logging.info(f"[SEND] sent data to {s.getpeername()}:")
                logging.info(f"\t({len(data)}) / {msg.hex()}")
                logging.info(f"\t({len(data)}) / {msg}")

        for s in exceptional:
            logging.warning(
                f"[EXCEPTION] exception occured on {s.getpeername()}")
            inputs.remove(s)
            if s in outputs:
                outputs.remove(s)
            del messages_dict[s]
            s.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    echo_server()