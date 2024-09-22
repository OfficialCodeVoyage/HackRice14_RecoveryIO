import cv2
from pose_estimation import PoseEstimator

def test_pose():
    pose_estimator = PoseEstimator()
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Cannot open webcam")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        image, results = pose_estimator.process_frame(frame)
        image = pose_estimator.draw_landmarks(image, results)
        cv2.imshow('Pose Test', image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    pose_estimator.close()

if __name__ == "__main__":
    test_pose()
