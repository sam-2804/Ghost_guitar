								# Ghost guitar                                 
                                
                                
import cv2

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