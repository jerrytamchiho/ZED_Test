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

import sys
import pyzed.sl as sl
from signal import signal, SIGINT
import argparse 
import os 
import time
import datetime
import cv2

cam = sl.Camera()

#Handler to deal with CTRL+C properly
def handler(signal_received, frame):
    cam.disable_recording()
    cam.close()
    cv2.destroyAllWindows() 
    sys.exit(0)

signal(SIGINT, handler)

def main():
    
    init = sl.InitParameters()
    init.camera_resolution = sl.RESOLUTION.HD1080
    init.camera_fps = 30
    init.depth_mode = sl.DEPTH_MODE.ULTRA # Set configuration parameters for the ZED
    init.async_image_retrieval = True; # This parameter can be used to record SVO in camera FPS even if the grab loop is running at a lower FPS (due to compute for ex.)    

    ts = time.time()
    start_time = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
    print('Starting time: ', start_time)

    status = cam.open(init) 
    if status != sl.ERROR_CODE.SUCCESS: 
        print("Camera Open", status, "Exit program.")
        exit(1)

    # Get camera information (serial number)
    zed_serial = cam.get_camera_information().serial_number
    # print("Hello! This is my serial number: {}".format(zed_serial))

    output_dir = '/home/vizlab/Desktop/recordings'
    # output_dir = '~/Desktop/recordings'
    output_name = start_time + str(zed_serial) + '.svo2'
    print('Output file: ', output_name)
    output_path = os.path.join(output_dir, output_name)

    os.makedirs(output_dir, exist_ok=True)
    print(output_path)

    recording_param = sl.RecordingParameters(output_path, sl.SVO_COMPRESSION_MODE.H264) # Enable recording with the filename specified in argument
    err = cam.enable_recording(recording_param)
    if err != sl.ERROR_CODE.SUCCESS:
        print("Recording ZED : ", err)
        exit(1)

    runtime = sl.RuntimeParameters()
    print("SVO is Recording, use Ctrl-C to stop.") # Start recording SVO, stop with Ctrl-C command
    frames_recorded = 0

    image = sl.Mat()

    try:
        while True:
            status = cam.grab(runtime)
            if status == sl.ERROR_CODE.SUCCESS : # Check that a new image is successfully acquired
                cam.retrieve_image(image, sl.VIEW.LEFT, sl.MEM.CPU, sl.Resolution(800, 600))
                frames_recorded += 1
                print("Frame count: " + str(frames_recorded), end="\r")
                img_cv = image.get_data()  # Get image data in numpy array format
                cv2.imshow("ZED Camera Feed", img_cv)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                break
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print(f'Close recording')
        cam.disable_recording()
        cam.close()
        cv2.destroyAllWindows() 

    cam.disable_recording()
    cam.close()
    cv2.destroyAllWindows() 
    sys.exit(0)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    opt = parser.parse_args()
    # if not opt.output_svo_file.endswith(".svo") and not opt.output_svo_file.endswith(".svo2"): 
    #     print("--output_svo_file parameter should be a .svo file but is not : ", opt.output_svo_file,"Exit program.")
    #     exit()

    main()