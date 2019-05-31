echo "Starting deployment"

scp -i ~/.ssh/id_rsa * pi@192.168.0.100:/home/pi/SPARC-FMS

echo "Files copied"

echo "Restarting server..."

ssh pi@192.168.0.100 'tmux kill-session -t 0 && sudo pkill python3 && tmux new-session "cd SERVER; sudo python3 server.py; read;"'

echo "Done."