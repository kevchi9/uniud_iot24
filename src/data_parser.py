import signal

shutdown = False

def signal_handler(signal, frame):
	global shutdown
	shutdown = True

def start_data_parser(r_pipe, w_pipe):

    signal.signal(signal.SIGINT, signal_handler)

    print("[Data parser has to be implemented, doing nothing.]")
    
    # TODO: parse data here

    while not shutdown:
        try:
            msg = r_pipe.recv()
            print(f"Message received: {msg}")

            # Just for test purposes
            w_pipe.send(f"Parsed data: {msg}")
        except Exception:
            print("No message to read.")

    w_pipe.close()
    print("Closing Data Parser...")