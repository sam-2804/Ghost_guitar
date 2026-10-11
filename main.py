								# Ghost guitar                                 
                                
                                
import cv2
import mediapipe as mp
import time 
import pygame 

pygame.mixer.init()
pygame.mixer.set_num_channels(8)
model_path = "hand_landmarker.task"

options = mp.tasks.vision.HandLandmarkerOptions(
            base_options = mp.tasks.BaseOptions(model_asset_path = model_path),
            running_mode = mp.tasks.vision.RunningMode.VIDEO,
            num_hands = 2,
            min_hand_detection_confidence= 0.4,
            min_hand_presence_confidence= 0.4,
            min_tracking_confidence= 0.4
            
)
landmarker = mp.tasks.vision.HandLandmarker.create_from_options(options)

capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

down_strum_counter = 1
up_strum_counter = 1
previous_y_pos = 0
last_strum_time = 0
g_chord_sound = pygame.mixer.Sound("chords/g_chord.wav")

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

                #anchor point is 8, since its where pick is usually held
                anchor_point = result.hand_landmarks[hand_idx][8]
                x = int(anchor_point.x * flipped_frame.shape[1])
                y = int(anchor_point.y * flipped_frame.shape[0])
                
                current_y_pos = y
                delta_y = current_y_pos - previous_y_pos                
                
                if delta_y > 100:                    
                    if (timestamp_ms-last_strum_time) > 300:
                        g_chord_sound.play()
                        print(f"Down Strum Number {down_strum_counter} Detected")
                        down_strum_counter += 1
                    
                if delta_y < -100:                    
                    if (timestamp_ms-last_strum_time) > 300:
                        g_chord_sound.play()
                        print(f"Up Strum Number {up_strum_counter} Detected")
                        up_strum_counter += 1
                
                previous_y_pos = current_y_pos
                
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting the program")
        break
        
    cv2.imshow("Virtual Guitar Feed",flipped_frame)
    
capture.release()
cv2.destroyAllWindows