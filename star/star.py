import cv2
import numpy as np

# 이미지 불러오기 및 전처리
def load_and_preprocess_image(image_path, image_size=1000):
    image = cv2.imread(image_path)
    resized_image = cv2.resize(image, (image_size, image_size))
    gray_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray_image, 50, 150)
    return edges

# 꼭짓점 수 확인
def check_vertices(contour, expected_vertices_count=10):
    epsilon = 0.05 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    return len(approx) == expected_vertices_count

# 도형이 닫혀 있는지 확인하는 함수 (시작점과 끝점의 거리로 확인)
def check_if_closed(contour, threshold_distance=10):
    start_point = contour[0][0]  # 윤곽선의 시작점
    end_point = contour[-1][0]   # 윤곽선의 끝점
    
    # 시작점과 끝점 사이의 거리 계산
    distance = np.linalg.norm(np.array(start_point) - np.array(end_point))
    
    # 거리가 threshold_distance 이하인 경우 닫힌 것으로 간주
    return distance <= threshold_distance


# 꼭짓점 크기 비교
def check_vertex_size_similarity(contour):
    # 각 꼭짓점 길이를 계산하여 가장 큰 꼭짓점과 가장 작은 꼭짓점 비교
    if len(contour) < 5:
        return False
    vertex_lengths = [cv2.norm(contour[i][0] - contour[(i+1)%5][0]) for i in range(5)]
    max_length, min_length = max(vertex_lengths), min(vertex_lengths)
    return max_length <= 1.5 * min_length

# 방향 유사도 체크
def check_direction_similarity(user_contour, expected_contour, threshold=1.5):
    similarity = cv2.matchShapes(user_contour, expected_contour, cv2.CONTOURS_MATCH_I1, 0.0)
    return similarity < threshold

# 전체 크기 비교
def check_overall_size(user_contour, expected_contour, size_ratio_threshold=0.5):
    user_area = cv2.contourArea(user_contour)
    expected_area = cv2.contourArea(expected_contour)
    return user_area >= size_ratio_threshold * expected_area

# 채점 함수
def star_score_result(user_star_image_path, expected_star_image_path):
    user_edges = load_and_preprocess_image(user_star_image_path)
    expected_edges = load_and_preprocess_image(expected_star_image_path)

    # 윤곽선 검출
    contours_user, _ = cv2.findContours(user_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_expected, _ = cv2.findContours(expected_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    user_contour = max(contours_user, key=cv2.contourArea) if contours_user else None
    expected_contour = max(contours_expected, key=cv2.contourArea) if contours_expected else None

    if user_contour is None or expected_contour is None:
        return "윤곽선을 찾을 수 없습니다."

    score = 0
    result_details = []

    # 1. 기본 모양 검사
    if check_vertices(user_contour):
        score += 1
        result_details.append("기본 모양: 1점 획득")
    else:
        result_details.append("기본 모양: 0점 획득")

    # 2. 도형 닫힘 검사
    if check_if_closed(user_contour):
        score += 1
        result_details.append("닫힘: 1점 획득")
    else:
        result_details.append("닫힘: 0점 획득")

    # 3. 윤곽선 검사
    if check_vertex_size_similarity(user_contour):
        score += 1
        result_details.append("윤곽선: 1점 획득")
    else:
        result_details.append("윤곽선: 0점 획득")

    # 4. 방향 검사
    if check_direction_similarity(user_contour, expected_contour):
        score += 1
        result_details.append("방향: 1점 획득")
    else:
        result_details.append("방향: 0점 획득")

    # 5. 전체 크기 검사
    if check_overall_size(user_contour, expected_contour):
        score += 1
        result_details.append("전체 크기: 1점 획득")
    else:
        result_details.append("전체 크기: 0점 획득")

    return f"별 채점 결과: {score}/5점\n" + "\n".join(result_details)

# 이미지 파일 경로 설정 (예시)
user_star_image_path = "C:/Users/jimin/OneDrive/star_image/user_star_image1.png"
expected_star_image_path = "C:/Users/jimin/OneDrive/star_image/expected_star_image.png"

# 채점 함수 호출 및 결과 출력
result = star_score_result(user_star_image_path, expected_star_image_path)
print(result)




