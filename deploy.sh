echo "Starting deployment"

scp -i ~/.ssh/id_rsa -r SERVER/* pi@192.168.0.100:/home/pi/SPARC-FMS/SERVER

echo "Files copied"

echo "Restarting server..."

ssh pi@192.168.0.100 'tmux kill-server; sudo pkill python3; tmux new-session -d "cd SPARC-FMS/SERVER; sudo python3 server.py; read;"'

echo "Done."