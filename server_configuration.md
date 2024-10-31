# Server Confiuration
git clone https://github.com/Kim-s-pirate/planner_server.git
sudo apt update
sudo add-apt-repository universe
sudo apt update
sudo apt install python3-pip
cd planner_server
pip3 install -r requirements.txt
cd ..
sudo apt install python3-venv
python3 -m venv myenv
source myenv/bin/activate

# Server SWAP Configuration
sudo dd if=/dev/zero of=/swapfile bs=128M count=16
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
sudo swapon -s
sudo vi /etc/fstab
/swapfile swap swap defaults 0 0

# Server Start
sudo lsof -t -i :1500 | xargs sudo kill -9
screen -dmS server
screen -S server -X stuff "cd ~\n"
screen -S server -X stuff "source myenv/bin/activate\n"
screen -S server -X stuff "cd planner_server/\n"
screen -S server -X stuff "python3 main.py\n"