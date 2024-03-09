import cv2
import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

def process_hand_landmarks(results):
    all_x_coords_left = []
    all_y_coords_left = []
    all_x_coords_right = []
    all_y_coords_right = []

    for hand_landmarks in results.multi_hand_landmarks:
        # 감지된 손의 landmark를 사용하여 좌표 저장
        landmarks = hand_landmarks.landmark
        x_coords = [landmark.x for landmark in landmarks]
        y_coords = [landmark.y for landmark in landmarks]

        if landmarks[mp_hands.HandLandmark.WRIST].x < 0.5:
            all_x_coords_left.extend(x_coords)
            all_y_coords_left.extend(y_coords)
        else:
            all_x_coords_right.extend(x_coords)
            all_y_coords_right.extend(y_coords)

    return all_x_coords_left, all_y_coords_left, all_x_coords_right, all_y_coords_right

def hand_classification(model, image):
    # OpenCV를 사용하여 BGR 이미지를 RGB로 변환
    rgb_frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Mediapipe를 사용하여 양손 감지
    results = hands.process(rgb_frame)

    label1, label2 = None, None

    if results.multi_hand_landmarks and len(results.multi_hand_landmarks) >= 2:
        all_x_coords_left, all_y_coords_left, all_x_coords_right, all_y_coords_right = process_hand_landmarks(results)

        if all_x_coords_left and all_y_coords_left and all_x_coords_right and all_y_coords_right:
            # Calculate bounding box encompassing both hands
            x_min_left = min(all_x_coords_left)
            y_min_left = min(all_y_coords_left)
            x_max_left = max(all_x_coords_left)
            y_max_left = max(all_y_coords_left)
            box_width_left = x_max_left - x_min_left
            box_height_left = y_max_left - y_min_left

            x_min_right = min(all_x_coords_right)
            y_min_right = min(all_y_coords_right)
            x_max_right = max(all_x_coords_right)
            y_max_right = max(all_y_coords_right)
            box_width_right = x_max_right - x_min_right
            box_height_right = y_max_right - y_min_right

            # Normalize coordinates by box width and height
            x_coords_normalized_left = [(x - x_min_left) * 100 / box_width_left for x in all_x_coords_left]
            y_coords_normalized_left = [(y - y_min_left) * 100 / box_height_left for y in all_y_coords_left]
            x_coords_normalized_right = [(x - x_min_right) * 100 / box_width_right for x in all_x_coords_right]
            y_coords_normalized_right = [(y - y_min_right) * 100 / box_height_right for y in all_y_coords_right]

            # 모델에 입력할 데이터 구성
            input_data_left = np.array([[x, y] for x, y in zip(x_coords_normalized_left, y_coords_normalized_left)])
            input_data_right = np.array([[x, y] for x, y in zip(x_coords_normalized_right, y_coords_normalized_right)])

            # 모델 예측
            pre1 = model.predict(np.expand_dims(input_data_left, axis=0))
            pre2 = model.predict(np.expand_dims(input_data_right, axis=0))

            # 분류 결과를 화면에 표시
            label1 = int(np.argmax(pre1))
            label2 = int(np.argmax(pre2))

    return {"label1": label1, "label2": label2}
