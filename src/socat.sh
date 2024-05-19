#! /bin/bash
trap terminate SIGINT

terminate() {
    pkill -SIGINT -P $$
    exit
}

socat -d -d pty,raw,echo=0,link=/dev/mypty/ptySENS1 pty,raw,echo=0,link=/dev/mypty/ptySENS1_V &
socat -d -d pty,raw,echo=0,link=/dev/mypty/ptySENS2 pty,raw,echo=0,link=/dev/mypty/ptySENS2_V &
socat -d -d pty,raw,echo=0,link=/dev/mypty/ptySENS3 pty,raw,echo=0,link=/dev/mypty/ptySENS3_V &

wait