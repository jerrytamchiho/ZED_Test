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
    Multi cameras sample showing how to open multiple ZED in one program
"""

import pyzed.sl as sl
import cv2
import numpy as np
import threading
import time
import signal
import os
import argparse 

zed_list = []
name_list = []
thread_list = []
stop_signal = False

def signal_handler(signal, frame):
    global stop_signal
    stop_signal=True
    time.sleep(0.5)
    exit()

def grab_run(index, output_svo_file):
    global stop_signal
    global zed_list
    global name_list

    recording_param = sl.RecordingParameters(output_svo_file, sl.SVO_COMPRESSION_MODE.H264)
    err = zed_list[index].enable_recording(recording_param)
    if err != sl.ERROR_CODE.SUCCESS:
        print("Recording ZED : ", err)
        exit(1)
    else:
        print(f'Running {output_svo_file}')
        # print(output_svo_file)

    runtime = sl.RuntimeParameters()

    frames_count = 0
    missed_counter = 0

    while not stop_signal:
        err = zed_list[index].grab(runtime)
        if err == sl.ERROR_CODE.SUCCESS:
            frames_count += 1
        else:
            missed_counter += 1
            print('missed_frame')
        # time.sleep(0.001) #1ms

    zed_list[index].disable_recording()
    zed_list[index].close()

    print(f'ZED {name_list[index]} has {missed_counter}/{frames_count} missed frames')
	
def main():
    global stop_signal
    global zed_list
    global name_list
    global thread_list

    signal.signal(signal.SIGINT, signal_handler)

    print("Initializing...")
    init = sl.InitParameters()
    init.camera_resolution = sl.RESOLUTION.HD1080
    init.camera_fps = 30  # The framerate is lowered to avoid any USB3 bandwidth issues
    init.depth_mode = sl.DEPTH_MODE.ULTRA

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

    computer_id = "02"
    #Start camera threads
    for index in range(0, len(zed_list)):
        if zed_list[index].is_opened():
            output_path = f'{computer_id}_{name_list[index]}_{opt.output_file}'
            print(f'camera_id {name_list[index]}: {output_path}')
            if(os.path.exists(output_path)):
                print('Recording already exist. Prevent overwritting file.')
                exit()

            thread_list.append(threading.Thread(target=grab_run, args=(index, output_path)))
            thread_list[index].start()

    while stop_signal == False:
        pass

    for index in range(0, len(thread_list)):
        thread_list[index].join()

    print("\nFINISH")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_file', type=str, help='Path to the SVO file that will be written', required=False, default='recording')
    opt = parser.parse_args()
    if not opt.output_file.endswith(".svo") and not opt.output_file.endswith(".svo2"): 
        # print(opt.output_file)
        print('Add svo2 file format')
        opt.output_file  += '.svo2'
        # print("--output_file parameter should be a .svo file but is not : ", opt.output_file,"Exit program.")

    print(f'Recording filename: {opt.output_file}')   
    # if(os.path.exists(opt.output_file)):
    #     print('Recording already exist. Prevent overwritting file.')
    #     exit()

    main()