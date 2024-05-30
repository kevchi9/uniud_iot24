#! /bin/bash
trap terminate SIGINT

terminate() {
    pkill -SIGINT -P $$
    exit
}

socat -d -d pty,raw,echo=0,link=../mypty/ptySENS1 pty,raw,echo=0,link=../mypty/ptySENS1_V &>>../socat.log &
socat -d -d pty,raw,echo=0,link=../mypty/ptySENS2 pty,raw,echo=0,link=../mypty/ptySENS2_V &>>../socat.log &
socat -d -d pty,raw,echo=0,link=../mypty/ptySENS3 pty,raw,echo=0,link=../mypty/ptySENS3_V &>>../socat.log &

wait