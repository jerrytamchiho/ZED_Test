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

def parse_args(init):
    if ("HD2K" in opt.resolution):
        init.camera_resolution = sl.RESOLUTION.HD2K
        print("[Sample] Using Camera in resolution HD2K")
    elif ("HD1080" in opt.resolution):
        init.camera_resolution = sl.RESOLUTION.HD1080
        print("[Sample] Using Camera in resolution HD1080")
    elif ("HD720" in opt.resolution):
        init.camera_resolution = sl.RESOLUTION.HD720
        print("[Sample] Using Camera in resolution HD720")
    elif len(opt.resolution)>0: 
        print("[Sample] No valid resolution entered. Using default")
    else : 
        init.camera_resolution = sl.RESOLUTION.HD1080
        print("[Sample] Using default resolution")
        
def main():

    init = sl.InitParameters()
    init.camera_resolution = sl.RESOLUTION.AUTO
    init.depth_mode = sl.DEPTH_MODE.NEURAL
    init.sdk_verbose = 1
    parse_args(init)

    # Open the camera
    zed = sl.Camera()
    status = zed.open(init)
    if status != sl.ERROR_CODE.SUCCESS: #Ensure the camera has opened succesfully
        print("Camera Open : "+repr(status)+". Exit program.")
        exit()

    # Enable Positional tracking (mandatory for object detection)
    positional_tracking_parameters = sl.PositionalTrackingParameters()
    # If the camera is static, uncomment the following line to have better performances
    # positional_tracking_parameters.set_as_static = True
    if zed.enable_positional_tracking(positional_tracking_parameters)!= sl.ERROR_CODE.SUCCESS:
        return
    
    # enable body tracking
    body_param = sl.BodyTrackingParameters()
    body_param.enable_tracking = False                # Track people across images flow
    body_param.enable_body_fitting = False            # Smooth skeleton move
    body_param.body_format = sl.BODY_FORMAT.BODY_18  # Choose the BODY_FORMAT you wish to use
    body_param.detection_model = sl.BODY_TRACKING_MODEL.HUMAN_BODY_FAST 
    if zed.enable_body_tracking(body_param) != sl.ERROR_CODE.SUCCESS:
        return

    # runtime parameters
    body_runtime_param = sl.BodyTrackingRuntimeParameters()
    body_runtime_param.detection_confidence_threshold = 40
    body_runtime_param.skeleton_smoothing = 0.7

    communication_param = sl.CommunicationParameters()
    communication_param.set_for_local_network(30002, "192.168.0.135")
    zed.start_publishing(communication_param)
    print("Start publishing")

    exit_app = False 
    bodies = sl.Bodies()

    try : 
        while not exit_app:
            if zed.grab() == sl.ERROR_CODE.SUCCESS: 
                zed.retrieve_bodies(bodies, body_runtime_param)
                # print(bodies)
                # sleep(0.001)
    except KeyboardInterrupt:
        exit_app = True 

    # close the Camera
    zed.disable_body_tracking()
    zed.disable_positional_tracking()
    zed.close()
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--resolution', type=str, help='Resolution, can be either HD2K, HD1200, HD1080, HD720, SVGA or VGA', default = '')
    opt = parser.parse_args()
    main()
