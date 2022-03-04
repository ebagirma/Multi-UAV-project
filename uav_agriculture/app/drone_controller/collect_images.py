# from picamera.array import PiRGBArray
# from picamera import PiCamera
# import time
# import cv2
# # initialize the camera and grab a reference to the raw camera capture
# camera = PiCamera()
# # camera.resolution = (640, 480)
# camera.framerate = 32
# rawCapture = PiRGBArray(camera, size=(640, 480))
# # allow the camera to warmup
# time.sleep(0.1)
# # capture frames from the camera
# for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
#     # grab the raw NumPy array representing the image, then initialize the timestamp
#     # and occupied/unoccupied text
#     image = frame.array
#     # show the frame
#     cv2.imshow("Frame", image)
#     key = cv2.waitKey(1) & 0xFF
#     # clear the stream in preparation for the next frame
#     rawCapture.truncate(0)
#     # if the `q` key was pressed, break from the loop
#     if key == ord("q"):
#         break

# import the opencv library 
import cv2 
import os 
import time
import datetime

def stopStreaming():
    os.remove("camera.lock")
  
# define a video capture object 

def stream(vehicle):
    vid = cv2.VideoCapture(0) 
    with open("camera.lock", "w+"):
        pass

    # i = 0
    
    while True: 
        
        # Capture the video frame 
        # by frame 
        _, frame = vid.read() 
    
        # Display the resulting frame 
        # cv2.imshow('frame', frame)
        # try:
        loc = vehicle.location.global_relative_frame
        lat, lon, alt = loc.lat, loc.lon, loc.alt
        # except:
        #     lat, lon, alt = 3.3342 + i, 54.22 + i, 10
        
        name = '::'.join([str(lat), str(lon), str(alt)])
        
        # i += 1

        name = name + "__" + str(time.time()) + ".jpg"
        cv2.imwrite('data/' + name, frame)
        
        time.sleep(0.5)
        if not os.path.exists('camera.lock'):
            break
        

    
    # After the loop release the cap object 
    vid.release() 
    # Destroy all the windows 
    cv2.destroyAllWindows() 