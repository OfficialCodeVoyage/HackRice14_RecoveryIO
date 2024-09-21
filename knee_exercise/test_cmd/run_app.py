# run_app.py
import cv2
import time
import sys
import logging
import traceback

from pose_estimation import PoseEstimator
from angle_calculator import calculate_angle
from exercise_counter import SquatCounter
from gamification import Gamification
from database import ProgressTracker

def main():
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')

    # Initialize components
    pose_estimator = PoseEstimator(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    squat_counter = SquatCounter(angle_threshold_down=130, angle_threshold_up=170, min_hold_time=0.5)
    gamification = Gamification()
    progress_tracker = ProgressTracker()

    # Initialize video capture
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use DirectShow backend on Windows for better performance
    frame_width = 640
    frame_height = 480
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    desired_fps = 15  # Adjust as needed
    frame_duration = 1.0 / desired_fps
    last_time = time.time()

    reps = 0
    points = 0

    print("Starting Knee Rehabilitation Application...")
    print("Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        current_time = time.time()
        elapsed = current_time - last_time
        if elapsed < frame_duration:
            time.sleep(frame_duration - elapsed)
            continue
        last_time = current_time

        if not ret:
            logging.warning("Failed to read frame from camera.")
            continue

        try:
            # Resize frame for performance
            frame = cv2.resize(frame, (frame_width, frame_height))

            # Process frame with MediaPipe
            image, results = pose_estimator.process_frame(frame)
            # Optional: If you want to visualize the landmarks, uncomment the next line
            # image = pose_estimator.draw_landmarks(image, results)

            relevant_landmarks = pose_estimator.get_relevant_landmarks(results, focus_side='right')

            feedback = "Ready"

            if relevant_landmarks:
                hip_coords = relevant_landmarks['hip']
                knee_coords = relevant_landmarks['knee']
                ankle_coords = relevant_landmarks['ankle']

                # Calculate angle
                angle = calculate_angle(hip_coords, knee_coords, ankle_coords)
                logging.debug(f"Knee angle: {angle}")

                # Update squat counter
                reps, feedback = squat_counter.update(angle)
                logging.debug(f"Repetitions: {reps}, Feedback: {feedback}")

                # Update gamification
                if feedback == "Good Rep":
                    gamification.add_points(1)
                    points = gamification.get_points()
                    achievements = gamification.get_achievements().copy()
                    logging.debug(f"Points: {points}, Achievements: {achievements}")

                    # Record progress
                    progress_tracker.record_progress(reps, points)

                # Annotate angle on frame (optional)
                # Uncomment if you want to see angle annotations
                # h, w, _ = frame.shape
                # knee_coords_pixel = (int(knee_coords[0] * w), int(knee_coords[1] * h))
                # color = (0, 255, 0)  # Green
                # if feedback == "Too Low!":
                #     color = (0, 0, 255)  # Red
                # elif feedback == "Good Rep":
                #     color = (0, 255, 0)  # Green
                # else:
                #     color = (255, 255, 0)  # Yellow

                # cv2.putText(image, f"{int(angle)}°", knee_coords_pixel, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2, cv2.LINE_AA)

            # Display the image (optional)
            # Uncomment if you want to see the video feed without landmarks
            # cv2.imshow('Knee Rehabilitation - Command Line Mode', image)

            # Print feedback to console
            if feedback != "Ready":
                print(f"Reps: {reps} | Feedback: {feedback} | Points: {points}")

            # Exit condition
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Exiting application...")
                break

        except Exception as e:
            error_msg = f"Error in main loop: {e}\n{traceback.format_exc()}"
            logging.error(error_msg)
            print("An error occurred. Check logs for details.")
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    pose_estimator.close()
    progress_tracker.close()
    print("Application closed.")

if __name__ == "__main__":
    main()
