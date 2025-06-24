########################################################################
#
# Copyright (c) 2022, STEREOLABS.
#
# All rights reserved.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
########################################################################

"""
    Open the camera and start streaming images using H264 codec
"""
import sys
import pyzed.sl as sl
import argparse
from time import sleep
import threading

zed_list = []
name_list = []
thread_list = []
stop_signal = False

def signal_handler(signal, frame):
    global stop_signal
    stop_signal=True
    time.sleep(0.5)
    exit()

def grab_run(index, port):

    global stop_signal
    global zed_list
    global name_list


    # Enable Positional tracking (mandatory for object detection)
    positional_tracking_parameters = sl.PositionalTrackingParameters()
    # If the camera is static, uncomment the following line to have better performances
    positional_tracking_parameters.set_as_static = True
    if zed_list[index].enable_positional_tracking(positional_tracking_parameters)!= sl.ERROR_CODE.SUCCESS:
        return
    
    # enable body tracking
    body_param = sl.BodyTrackingParameters()
    body_param.enable_tracking = False                # Track people across images flow
    body_param.enable_body_fitting = False            # Smooth skeleton move
    body_param.body_format = sl.BODY_FORMAT.BODY_18  # Choose the BODY_FORMAT you wish to use
    body_param.detection_model = sl.BODY_TRACKING_MODEL.HUMAN_BODY_FAST 
    if zed_list[index].enable_body_tracking(body_param) != sl.ERROR_CODE.SUCCESS:
        return

    # runtime parameters
    body_runtime_param = sl.BodyTrackingRuntimeParameters()
    body_runtime_param.detection_confidence_threshold = 40
    body_runtime_param.skeleton_smoothing = 0.7

    communication_param = sl.CommunicationParameters()
    communication_param.set_for_local_network(port, "192.168.0.135")
    zed_list[index].start_publishing(communication_param)
    print("Start publishing")

    exit_app = False 
    bodies = sl.Bodies()

    while not stop_signal:
        err = zed_list[index].grab()
        if err == sl.ERROR_CODE.SUCCESS:
            zed_list[index].retrieve_bodies(bodies, body_runtime_param)
        # time.sleep(0.001) #1ms

    zed_list[index].disable_body_tracking()
    zed_list[index].disable_positional_tracking()
    zed_list[index].close()

    print(f'ZED {name_list[index]} has {missed_counter}/{frames_count} missed frames')
	

def main():

    print("Initializing...")
    init = sl.InitParameters()
    init.camera_resolution = sl.RESOLUTION.HD1080
    init.camera_fps = 30  # The framerate is lowered to avoid any USB3 bandwidth issues
    init.depth_mode = sl.DEPTH_MODE.NEURAL

    #List and open cameras
    name_list = []
    cameras = sl.Camera.get_device_list()
    index = 0
    for cam in cameras:
        init.set_from_serial_number(cam.serial_number)
        name_list.append("ZED {}".format(cam.serial_number))
        print("Opening {}".format(name_list[index]))
        zed_list.append(sl.Camera())
        status = zed_list[index].open(init)
        if status != sl.ERROR_CODE.SUCCESS:
            print(repr(status))
            zed_list[index].close()
        index = index +1

    # init = sl.InitParameters()
    # init.camera_resolution = sl.RESOLUTION.AUTO
    # init.depth_mode = sl.DEPTH_MODE.NEURAL
    # init.sdk_verbose = 1
    # parse_args(init)

    #Start camera threads
    for index in range(0, len(zed_list)):
        if zed_list[index].is_opened():
            # output_path = f'{computer_id}_{name_list[index]}_{opt.output_file}'
            print(f'camera_id {name_list[index]}')

            thread_list.append(threading.Thread(target=grab_run, args=(index, 30002+(index*2))))
            thread_list[index].start()

    while stop_signal == False:
        pass

    for index in range(0, len(thread_list)):
        thread_list[index].join()

    print("\nFINISH")
    
    
if __name__ == "__main__":
    main()
