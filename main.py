								# Ghost guitar                                 
                                
                                
import cv2
import mediapipe as mp

model_path = "hand_landmarker.task"
options = mp.tasks.vision.HandLandmarkerOptions(
            base_options = mp.tasks.BaseOptions(model_asset_path = model_path),
            running_mode = mp.tasks.vision.RunningMode.VIDEO,
            num_hands = 2,
            min_hand_detection_confidence= 1,
            min_hand_presence_confidence= 1,
            min_tracking_confidence= 1 
            
)
landmarker = mp.tasks.vision.HandLandmarker.create_from_options(options)

capture = cv2.VideoCapture(0)

while capture.isOpened():
    
    ret,frame = capture.read()
    
    if not ret :
        print("No signal from Camera, Make sure camera drivers are working properly")
        break
        
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting the program")
        break
        
    # To make the feed from camera look like a mirror 
    flipped_frame = cv2.flip(frame,1)
    cv2.imshow("Virtual Guitar Feed",flipped_frame)
    
capture.release()
cv2.destroyAllWindows