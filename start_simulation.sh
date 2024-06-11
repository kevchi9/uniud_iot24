#!/bin/bash

FILES=("source_data/gps_to_serial.txt" "source_data/electrics_to_serial.txt" "source_data/imu_to_serial.txt")
PORTS=("mypty/ptySENS1" "mypty/ptySENS2" "mypty/ptySENS3")

# Check if all files and ports exist
for i in "${!FILES[@]}"; do
  file="${FILES[$i]}"
  port="${PORTS[$i]}"

  if [ ! -f "$file" ]; then
    echo "Error: Input file $file does not exist."
    exit 1
  fi

  if [ ! -c "$port" ]; then
    echo "Error: Serial port $port does not exist."
    exit 1
  fi
done

# Create file descriptors for all input files
exec {fd0}<>${FILES[0]}
exec {fd1}<>${FILES[1]}
exec {fd2}<>${FILES[2]}

# File descriptor array
fds=($fd0 $fd1 $fd2)

# Loop to write one line at a time to each corresponding serial port
while :; do
  done_reading=true
  for i in "${!fds[@]}"; do
    fd=${fds[$i]}
    port="${PORTS[$i]}"
    if read -u "$fd" -r line; then
      echo "$line" > "$port"
      done_reading=false
      sleep 0.015  # Sleep for 50 milliseconds
    fi
  done
  if $done_reading; then
    break
  fi
done

# Close file descriptors
exec {fd0}>&-
exec {fd1}>&-
exec {fd2}>&-
