								# Ghost guitar                                 
                                
                                
import cv2
import mediapipe as mp
import time 

model_path = "hand_landmarker.task"
options = mp.tasks.vision.HandLandmarkerOptions(
            base_options = mp.tasks.BaseOptions(model_asset_path = model_path),
            running_mode = mp.tasks.vision.RunningMode.VIDEO,
            num_hands = 2,
            min_hand_detection_confidence= 0.7,
            min_hand_presence_confidence= 0.7,
            min_tracking_confidence= 0.7
            
)
landmarker = mp.tasks.vision.HandLandmarker.create_from_options(options)

capture = cv2.VideoCapture(0)

while capture.isOpened():
    
    ret,frame = capture.read()
    
    if not ret :
        print("No signal from Camera, Make sure camera drivers are working properly")
        break

    
    # To make the feed from camera look like a mirror 
    flipped_frame = cv2.flip(frame,1)
    
    # OpenCV outputs BGR, While mediapipe requires RGB
    rgb_frame = cv2.cvtColor(flipped_frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
   
    timestamp_ms = int(time.time() * 1000)
    result = landmarker.detect_for_video(mp_image, timestamp_ms)    
    
    if result.hand_landmarks:
        for hand in result.hand_landmarks:
            for landmark in hand:            
                x = int(landmark.x * flipped_frame.shape[1])
                y = int(landmark.y * flipped_frame.shape[0])
                # visualizing landmarks for testing purpose,need to remove later to improve performance
                cv2.circle(flipped_frame, (x, y), 5, (0, 255, 0), -1)    
    
    if result.hand_landmarks: 
        for hand_idx in range(len(result.hand_landmarks)):
            hand_label = result.handedness[hand_idx][0].category_name
            
            #If you are confused why left = right here, frame is flipped before passing into mediapipe 
            if hand_label == "Left":
                print("Right hand detected")
                index_fnger_tip = result.hand_landmarks[hand_idx][8]
                x = int(index_fnger_tip.x * flipped_frame.shape[1])
                y = int(index_fnger_tip.y * flipped_frame.shape[0])
                
                #Temporary condition for strumming
                if y < 180:
                    print("Strum")
                    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting the program")
        break
        
    cv2.imshow("Virtual Guitar Feed",flipped_frame)
    
capture.release()
cv2.destroyAllWindows