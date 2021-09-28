from flask import Flask, request, jsonify, Blueprint
import paramiko
import time
from flask_cors import CORS, cross_origin
import sys

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


def connect_ssh(username, password, ip, port):
    ssh.connect(ip, username=username, password=password,
                allow_agent=False, look_for_keys=False)


@app.route('/connect', methods=['POST'])
@cross_origin()
def connection():
    req = request.json
    username = req['username']
    password = req['password']
    ip = req['ip']
    port = req['port']
    kill_screen_command = 'killall screen'
    screen_command = 'screen -S rosbridge'
    ros_command = 'export ROS_HOSTNAME={} && export ROS_MASTER_URI=http://{}:11311 && roslaunch rosbridge_server rosbridge_websocket.launch port:={}'.format(
        ip, ip, port)
    ros_output = 'started at ws://0.0.0.0:{}'.format(
        port)
    try:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password,
                    allow_agent=False, look_for_keys=False)
        channel = ssh.get_transport().open_session()
        channel.get_pty()
        channel.invoke_shell()
        channel.sendall('{}\n'.format(screen_command))
        channel.sendall('{}\n'.format(ros_command))

        while True:
            msg = channel.recv(1024)
            print(msg, flush=True)
            if not msg:
                ssh.close()
                break
            if ros_output in str(msg):
                break
        return 'Connect to {}'.format(ip), 200
    except TimeoutError as ex:
        # times out on OS X, localhost
        return "TimeoutException: SSH connection fails.", 401
    except paramiko.AuthenticationException as e:
        return "{} please verify your credentials".format(e), 401
    except paramiko.SSHException as e:
        return "{} invalid Username/Password for {}".format(e, ip), 401
    except paramiko.BadHostKeyException as e:
        return "Unable to verify server's host key: {}".format(e), 401


@app.route('/command', methods=['POST'])
@cross_origin()
def runningCommand():
    req = request.json
    command = req['command']
    screen_name = req['screen_name']
    username = req['username']
    password = req['password']
    ip = req['ip']
    port = req['port']
    # ros_command = 'export ROS_HOSTNAME={} && export ROS_MASTER_URI=http://{}:11311 && {}'.format(
    #     ip, ip, command)
    screen_command = 'screen -S {}'.format(screen_name)
    ros_command = 'export ROS_HOSTNAME={} && export ROS_MASTER_URI=http://{}:11311 && {}'.format(
        ip, ip, command)
    ros_output = 'Calibration End'
    try:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password,
                    allow_agent=False, look_for_keys=False)
        channel = ssh.get_transport().open_session()
        channel.get_pty()
        channel.invoke_shell()
        channel.sendall('{}\n'.format(screen_command))
        channel.sendall('{}\r'.format(ros_command))

        # s = channel.recv(10000)
        while True:
            msg = channel.recv(1024)
            print(msg, flush=True)
            if not msg:
                ssh.close()
                break
            if ros_output in str(msg):
                break
        return 'Running: {}'.format(command), 200
    except TimeoutError as ex:
        # times out on OS X, localhost
        return "TimeoutException: SSH connection fails.", 401
    except paramiko.AuthenticationException as e:
        return "{}, please verify your credentials".format(e), 401
    except paramiko.SSHException as e:
        return "{}, invalid Username/Password for {}".format(e, ip), 401
    except paramiko.BadHostKeyException as e:
        return "Unable to verify server's host key: {}".format(e), 401


@app.route('/avis-lowlv', methods=['GET'])
@cross_origin()
def avis_low_lv():
    req = request.json
    username = req['username']
    password = req['password']
    ip = req['ip']
    ros_command = 'export ROS_HOSTNAME=localhost && export ROS_MASTER_URI=http://localhost:11311 && roslaunch avisbot_beta avisbot_lowlevel.launch'
    ros_output = 'Waiting for IMU to be attached...'
    try:
        channel = ssh.get_transport().open_session()
        channel.get_pty()
        channel.invoke_shell()
        channel.sendall('{}\r'.format(ros_command))
        # s = channel.recv(10000)
        while True:
            msg = channel.recv(1024)
            print(msg, flush=True)
            if not msg:
                ssh.close()
                break
            if ros_output in str(msg):
                break
        return ros_output, 200
    except paramiko.AuthenticationException as e:
        return "{}, please verify your credentials".format(e)
    except paramiko.SSHException as e:
        return "{}, invalid Username/Password for {}".format(e, ip)
    except paramiko.BadHostKeyException as e:
        return "Unable to verify server's host key: {}".format(e)


@app.route('/avis-highlv', methods=['GET'])
@cross_origin()
def avis_high_lv():
    req = request.json
    username = req['username']
    password = req['password']
    ip = req['ip']
    ros_command = 'export ROS_HOSTNAME=localhost && export ROS_MASTER_URI=http://localhost:11311 && roslaunch avisbot_beta avisbot_highlevel.launch'
    ros_output = 'simROS just started!'
    try:
        channel = ssh.get_transport().open_session()
        channel.get_pty()
        channel.invoke_shell()
        channel.sendall('{}\r'.format(ros_command))
        # s = channel.recv(10000)
        while True:
            msg = channel.recv(1024)
            print(msg, flush=True)
            # if not msg:
            #     ssh.close()
            #     break
            # if ros_output in str(msg):
            #     break
        return ros_output, 200
    except paramiko.AuthenticationException as e:
        return "{}, please verify your credentials".format(e)
    except paramiko.SSHException as e:
        return "{}, invalid Username/Password for {}".format(e, ip)
    except paramiko.BadHostKeyException as e:
        return "Unable to verify server's host key: {}".format(e)


@app.route('/disconnect', methods=['POST'])
@cross_origin()
def disconnect():
    req = request.json
    username = req['username']
    password = req['password']
    ip = req['ip']
    port = req['port']
    screen_command = 'killall screen'
    try:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password,
                    allow_agent=False, look_for_keys=False)

        channel = ssh.get_transport().open_session()
        channel.get_pty()
        channel.invoke_shell()
        channel.sendall('{}\r'.format(screen_command))
        ssh.close()
        return 'Disconnect.'
    except paramiko.AuthenticationException as e:
        return "{}, please verify your credentials".format(e)
    except paramiko.SSHException as e:
        return "{}, invalid Username/Password for {}".format(e, ip)
    except paramiko.BadHostKeyException as e:
        return "Unable to verify server's host key: {}".format(e)


if __name__ == "__main__":
    app.run(debug=True)