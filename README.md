# ROS GUI backend

## Requirements

 Python 3.7+ 

## Project installation

Clone the repository and install dependencies:
    
```bash
$ git clone https://github.com/supalukbenz/ros-gui-backend.git
$ cd ros-gui-backend
```
Create a virtual environment and install the required packages
```bash
$ virtualenv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

Run Flask
```bash
(venv) $ export FLASK_APP=main.py
(venv) $ flask run
```

Backend server running on [http://localhost:5000/](http://localhost:5000/)
