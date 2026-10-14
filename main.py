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
            # lower these values if performance is needed, Might lower accuracy
)
landmarker = mp.tasks.vision.HandLandmarker.create_from_options(options)

capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

down_strum_counter = 1
up_strum_counter = 1
previous_y_pos = 0
last_strum_time = 0
finger_tips = [8,12,16,20]
finger_pips = [6,10,14,18]
cooldown_ms = 150       
velocity_slow = 80      
velocity_fast = 220     
                
g_chord_sound = [pygame.mixer.Sound("chords/G_chord_down.wav"), pygame.mixer.Sound("chords/G_chord_up.wav"),pygame.mixer.Sound("chords/G_chord_fast_down.wav"),pygame.mixer.Sound("chords/G_chord_fast_up.wav")]
c_chord_sound = [pygame.mixer.Sound("chords/C_chord_down.wav"), pygame.mixer.Sound("chords/C_chord_up.wav"),pygame.mixer.Sound("chords/C_chord_fast_down.wav"),pygame.mixer.Sound("chords/C_chord_fast_up.wav")]
d_chord_sound = [pygame.mixer.Sound("chords/D_chord_down.wav"), pygame.mixer.Sound("chords/D_chord_up.wav"),pygame.mixer.Sound("chords/D_chord_fast_down.wav"),pygame.mixer.Sound("chords/D_chord_fast_up.wav")]
active_chord = g_chord_sound

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
    
    
    #if result.hand_landmarks:
    #    for hand in result.hand_landmarks:
    #        for landmark in hand:            
    #            x = int(landmark.x * flipped_frame.shape[1])
    #            y = int(landmark.y * flipped_frame.shape[0]) #visualizing landmarks for testing purpose,need to remove later to improve performance
    #            cv2.circle(flipped_frame, (x, y), 5, (0, 255, 0), -1)    
    #NOTE : Only uncomment this if you are unsure of the model's tracking capabilities
        


    if result.hand_landmarks: 
        for hand_idx in range(len(result.hand_landmarks)):
            hand_label = result.handedness[hand_idx][0].category_name
            
            #If you are confused why left = right here, frame is flipped before passing into mediapipe 
            if hand_label == "Left":

                #anchor point is 8, since its where pick is usually held
                anchor_point = result.hand_landmarks[hand_idx][8]
                x = int(anchor_point.x * flipped_frame.shape[1])
                y = int(anchor_point.y * flipped_frame.shape[0])
                cv2.circle(flipped_frame,(x,y), 5, (0, 255, 0 ), -1)
                
                current_y_pos = y
                delta_y = current_y_pos - previous_y_pos                
                
                time_since_last_strum = timestamp_ms - last_strum_time

                if time_since_last_strum > cooldown_ms:
                    
                    if delta_y > velocity_slow:        
                        
                        if delta_y >= velocity_fast:    
                            pygame.mixer.stop() 
                            active_chord[2].play() 
                            print("Fast Down Strum Detected ")
                        
                        else:
                            pygame.mixer.fadeout(50)
                            active_chord[0].play() 
                            print("Normal Down Strum")
                        last_strum_time = timestamp_ms

                    elif delta_y < -velocity_slow:
                    
                        if delta_y <= -velocity_fast:
                            pygame.mixer.stop()
                            active_chord[3].play() 
                            print("fast Up Strum Detected ")
                        else:
                            pygame.mixer.fadeout(50)
                            active_chord[1].play() 
                            print("Normal Up Strum ")
                        
                        last_strum_time = timestamp_ms
                previous_y_pos = current_y_pos
            
            if hand_label == "Right":
                
                fingers = []
                for tip,pip in zip(finger_tips, finger_pips):
                    if result.hand_landmarks[hand_idx][tip].y < result.hand_landmarks[hand_idx][pip].y:
                        fingers.append(1)
                    else:
                        fingers.append(0)
                    
                
                    #tip_x = int(result.hand_landmarks[hand_idx][tip].x * flipped_frame.shape[1])
                    #tip_y = int(result.hand_landmarks[hand_idx][tip].y * flipped_frame.shape[0])
                    #cv2.circle(flipped_frame,(tip_x,tip_y), 5, (0, 255, 0 ), -1)
                
                    #pip_x = int(result.hand_landmarks[hand_idx][pip].x * flipped_frame.shape[1])
                    #pip_y = int(result.hand_landmarks[hand_idx][pip].y * flipped_frame.shape[0])
                    #cv2.circle(flipped_frame,(pip_x,pip_y), 5, (0, 255, 0 ), -1)
                    
                if fingers == [1,0,0,0]:
                    print("G chord dectected")
                    active_chord = g_chord_sound
                    
                elif fingers == [0,1,1,1]:
                    active_chord = c_chord_sound
                    print("C chord dectected")
                    
                elif fingers == [1,1,1,1]:
                    print("D chord dectected")
                    active_chord = d_chord_sound
                    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting the program")
        break
        
    cv2.imshow("Virtual Guitar Feed",flipped_frame)
    
capture.release()
cv2.destroyAllWindows()