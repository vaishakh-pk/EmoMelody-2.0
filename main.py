from keras.models import load_model
from time import time, sleep
from keras.preprocessing.image import img_to_array
from keras.preprocessing import image
import cv2
import numpy as np
import os
import random
import pygame
import socket

# Define the IP address and port of the NodeMCU server
NODEMCU_IP = '192.168.1.7'  # Replace with the IP address of NodeMCU
NODEMCU_PORT = 12345  # Choose a port number

# Load pre-trained face detection model and emotion classification model
face_classifier = cv2.CascadeClassifier(r'D:\EmoMelody\EmoMelody\haarcascade_frontalface_default.xml')
classifier = load_model(r'D:\EmoMelody\EmoMelody\model.h5')

# Define emotion labels
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']

# Initialize video capture
cap = cv2.VideoCapture(0)

# Initialize variables for tracking time and counting emotions
start_time = time()  # Start time for 10-second interval
emotion_counter = {label: 0 for label in emotion_labels}  # Dictionary to count occurrences of each emotion
total_frames = 0  # Counter for total frames processed

# Function to send emotion data to NodeMCU
def send_emotion_to_node_mcu(emotion):
    try:
        # Create a socket object
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Connect to the NodeMCU server
            s.connect((NODEMCU_IP, NODEMCU_PORT))
            # Send emotion data over the socket connection
            s.sendall(emotion.encode())
        print("Emotion data sent to NodeMCU successfully")
    except Exception as e:
        print("Error sending emotion data to NodeMCU:", e)

# Function to play audio based on detected emotion
def play_audio(emotion, song_path):
    pygame.mixer.init()
    pygame.mixer.music.load(song_path)  # Load the selected song
    pygame.mixer.music.play()  # Play the song

# Main loop for emotion detection
while True:
    _, frame = cap.read()  # Read frame from video capture
    labels = []
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert frame to grayscale
    faces = face_classifier.detectMultiScale(gray)  # Detect faces in the grayscale frame

    # Flag to control emotion detection loop
    detect_emotion = True

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)  # Draw rectangle around detected face
        roi_gray = gray[y:y + h, x:x + w]  # Extract region of interest (ROI) - face
        roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)  # Resize ROI to match model input

        if np.sum([roi_gray]) != 0 and detect_emotion:
            roi = roi_gray.astype('float') / 255.0  # Normalize ROI
            roi = img_to_array(roi)  # Convert ROI to array
            roi = np.expand_dims(roi, axis=0)  # Expand dimensions to match model input

            prediction = classifier.predict(roi)[0]  # Perform emotion classification
            label = emotion_labels[prediction.argmax()]  # Get predicted emotion label
            emotion_counter[label] += 1  # Increment counter for detected emotion
            label_position = (x, y)
            cv2.putText(frame, label, label_position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0),
                        2)  # Display emotion label
            detect_emotion = False  # Pause emotion detection loop

    cv2.imshow('Emotion Detector', frame)  # Display frame with emotion detection
    total_frames += 1  # Increment total frames counter

    if time() - start_time >= 10:  # Check if 10 seconds have passed
        most_common_emotion = max(emotion_counter, key=emotion_counter.get)  # Find the most occurring emotion
        print("Most occurring emotion:", most_common_emotion)  # Print the most occurring emotion
        print("Total frames processed:", total_frames)  # Print total frames processed
        send_emotion_to_node_mcu(most_common_emotion)

        # Release and reinitialize the video capture object
        cap.release()
        cap = cv2.VideoCapture(0)

        # Reset emotion detection variables
        start_time = time()
        emotion_counter = {label: 0 for label in emotion_labels}
        total_frames = 0

        # Define folders containing songs corresponding to each emotion
        folder_mapping = {
            'Angry': r'D:\EmoMelody\EmoMelody\Songs\Angry',
            'Disgust': r'D:\EmoMelody\EmoMelody\Songs\Disgust',
            'Fear': r'D:\EmoMelody\EmoMelody\Songs\Fear',
            'Happy': r'D:\EmoMelody\EmoMelody\Songs\Happy',
            'Neutral': r'D:\EmoMelody\EmoMelody\Songs\Neutral',
            'Sad': r'D:\EmoMelody\EmoMelody\Songs\Sad',
            'Surprise': r'D:\EmoMelody\EmoMelody\Songs\Surprise'
        }
        folder_path = folder_mapping.get(most_common_emotion, '')  # Get folder path based on detected emotion
        if folder_path:
            songs = os.listdir(folder_path)  # List all songs in the folder
            if songs:
                # Select a random song from the folder
                song_path = os.path.join(folder_path, random.choice(songs))
                play_audio(most_common_emotion, song_path)  # Play audio based on the most occurring emotion

        # Wait for song to finish playing before resuming emotion detection
        song_duration = pygame.mixer.Sound(song_path).get_length()
        sleep(song_duration)
        detect_emotion = True  # Resume emotion detection loop

    if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit loop if 'q' key is pressed
        break

cap.release()  # Release video capture
cv2.destroyAllWindows()  # Close all OpenCV windows
