from flask import Flask, request, jsonify, Blueprint
import paramiko
import time
from flask_cors import CORS, cross_origin
import sys
import os

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}}, support_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'


def connect_ssh(username, password, ip, port):
    ssh.connect(ip, username=username, password=password,
                allow_agent=False, look_for_keys=False)


def kill_screen(ssh):
    screen_detached = "screen -ls | grep pts | cut -d. -f1 | awk '{print $1}' | xargs kill"
    screen_command = "screen -ls | grep Detached | cut -d. -f1 | awk '{print $1}' | xargs kill"
    screen_kill_command = "killall screen"
    screen_output = "No Sockets found"
    session_output = "no process found"
    channel = ssh.get_transport().open_session()
    channel.get_pty()
    channel.invoke_shell()
    # channel.sendall('{}\n'.format(screen_detached))
    channel.sendall('{}\r'.format(screen_kill_command))
    print("kill_screen", flush=True)
    # while True:
    #     msg = channel.recv(1024)
    #     print(msg, flush=True)
    #     if not msg:
    #         print("not msg", flush=True)
    #         ssh.close()
    #         break
    #     if screen_output in str(msg) or session_output in str(msg):
    #         state = True
    #         break
    return screen_kill_command


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
    address_error_output = 'already in use'
    address_error = False
    try:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password,
                    allow_agent=False, look_for_keys=False)
        # kill_state = kill_screen(ssh)

        channel = ssh.get_transport().open_session()
        channel.get_pty()
        channel.invoke_shell()
        channel.sendall('{}\n'.format(kill_screen_command))
        channel.sendall('{}\n'.format(screen_command))
        channel.sendall('{}\n'.format(ros_command))

        while True:
            msg = channel.recv(1024)
            print('{}'.format(msg.decode("utf-8")), flush=True)
            if not msg:
                ssh.close()
                break
            if address_error_output in str(msg):
                address_error = True
                break
            if ros_output in str(msg):
                break

        if address_error:
            return "{} already in use.\nPlease, change port number".format(port), 401
        else:
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
    ros_output = 'start with pid'
    try:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password,
                    allow_agent=False, look_for_keys=False)
        transport = ssh.get_transport()
        channel = transport.open_session()
        channel.get_pty()
        channel.invoke_shell()
        channel.sendall('{}\n'.format(screen_command))
        channel.sendall('{}\r'.format(ros_command))

        # while True:
        #     # print('channel.closed {}'.format(
        #     #     channel.closed), flush=True)
        #     # print('transport {}'.format(transport.is_active()), flush=True)
        #     msg = channel.recv(1024)
        #     print('msg: {}'.format(msg), flush=True)
        #     if not msg:
        #         # ssh.close()
        #         break
        #     if ros_output in str(msg):
        #         break
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
    screen_detached = "screen -ls | grep pts | cut -d. -f1 | awk '{print $1}' | xargs kill"
    screen_command = "screen -ls | grep Detached | cut -d. -f1 | awk '{print $1}' | xargs kill"
    screen_kill_command = "killall screen"
    screen_output = "No Sockets found"
    try:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password,
                    allow_agent=False, look_for_keys=False)

        # channel = ssh.get_transport().open_session()
        # channel.get_pty()
        # channel.invoke_shell()
        # channel.sendall('{}\n'.format(screen_detached))
        # channel.sendall('{}\r'.format(screen_command))
        # while True:
        #     msg = channel.recv(1024)
        #     print(msg, flush=True)
        #     if not msg:
        #         print("not msg", flush=True)
        #         ssh.close()
        #         break
        #     if screen_output in str(msg):
        #         break
        # # stdin, stdout, stderr = ssh.exec_command(
        # #     screen_kill_command, get_pty=True)
        # # ssh.close()
        kill_state = kill_screen(ssh)
        return 'Disconnect.', 200
    except paramiko.AuthenticationException as e:
        return "{}, please verify your credentials".format(e)
    except paramiko.SSHException as e:
        return "{}, invalid Username/Password for {}".format(e, ip)
    except paramiko.BadHostKeyException as e:
        return "Unable to verify server's host key: {}".format(e)


if __name__ == "__main__":
    app.run(debug=False)
    # port = int(os.environ.get('PORT', 5000))
    # app.run(host='0.0.0.0', port=port)
