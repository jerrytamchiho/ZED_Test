DISPLAY=:0 /usr/local/zed/tools/ZED_Explorer &

if [ ! -f /tmp/auto_record.lock ]; then
    python3 /home/username/auto_record.py &
    touch /tmp/auto_record.lock
fi
