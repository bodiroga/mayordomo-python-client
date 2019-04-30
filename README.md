# Mayordomo python client

## Installation steps (WIP)

### Install dependencies
sudo apt install -y git swig3.0 python-pyaudio python3-pyaudio libatlas-base-dev libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev virtualenv

### Clone the repository
git clone https://github.com/bodiroga/mayordomo-python-client.git
cd mayordomo-python-client

### Create a virtual environment and make use of it
virtualenv env
source env/bin/activate

### Install python dependencies
pip install -r requirements.txt

