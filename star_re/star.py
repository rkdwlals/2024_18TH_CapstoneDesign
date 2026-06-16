import cv2
import numpy as np

# 이미지 불러오기 및 전처리
def load_and_preprocess_image(image_path, image_size=1000):
    # 이미지 파일을 읽고 크기를 조정합니다
    image = cv2.imread(image_path)
    
    # 이미지가 제대로 불러와졌는지 확인
    if image is None:
        raise FileNotFoundError(f"이미지를 불러올 수 없습니다: {image_path}")
    
    # 이미지를 지정된 크기로 리사이즈하고 회색조로 변환
    resized_image = cv2.resize(image, (image_size, image_size))
    gray_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
    
    # 블러링을 추가하여 잡음을 줄이고 더 깨끗한 윤곽선을 만듭니다
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    
    # 이진화 처리를 통해 픽셀을 흑백으로 분리
    _, threshold_image = cv2.threshold(blurred_image, 127, 255, cv2.THRESH_BINARY)
    
    # Canny 엣지 검출을 사용해 이미지의 윤곽선을 찾아냅니다
    edges = cv2.Canny(threshold_image, 30, 100)
    
    # 전처리된 이미지를 반환 (리사이즈된 원본 이미지와 윤곽선 이미지)
    return resized_image, edges

# 꼭짓점 검출 및 시각적 표시
def draw_vertices_and_contours(image, contour):
    # 파란색 윤곽선을 이미지에 그립니다
    cv2.drawContours(image, [contour], -1, (255, 0, 0), 2)  # 파란색 윤곽선
    
    # 윤곽선의 모서리 꼭짓점을 검출하고 초록색 원으로 표시
    epsilon = 0.05 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    for point in approx:
        cv2.circle(image, tuple(point[0]), 5, (0, 255, 0), -1)  # 초록색 원으로 꼭짓점 표시
    
    # 윤곽선과 꼭짓점이 표시된 이미지를 반환
    return image

# 꼭짓점 수가 예상과 일치하는지 확인
def check_vertices(contour, expected_vertices_count=5):
    # 윤곽선 길이에 비례한 근사치를 계산해 꼭짓점을 찾음
    epsilon = 0.05 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    # 꼭짓점 개수가 예상치와 같은지 여부 반환
    return len(approx) == expected_vertices_count

# 도형이 닫혀 있는지 확인
def check_if_closed(contour, threshold_distance=10):
    # 윤곽선의 시작점과 끝점의 좌표를 얻습니다
    start_point = contour[0][0]
    end_point = contour[-1][0]
    # 시작점과 끝점 사이의 유클리드 거리를 계산하고, threshold_distance 이하이면 닫힌 것으로 간주
    distance = np.linalg.norm(np.array(start_point) - np.array(end_point))
    return distance <= threshold_distance

# 꼭짓점 크기의 유사성을 확인
def check_vertex_size_similarity(contour):
    # 꼭짓점 수가 충분하지 않으면 False 반환
    if len(contour) < 5:
        return False
    # 꼭짓점 간의 거리를 계산하여 유사성 확인
    vertex_lengths = [cv2.norm(contour[i][0] - contour[(i+1)%5][0]) for i in range(5)]
    max_length, min_length = max(vertex_lengths), min(vertex_lengths)
    # 가장 큰 길이가 가장 작은 길이의 1.5배 이하면 True 반환
    return max_length <= 1.5 * min_length

# 두 윤곽선 간 방향 유사도를 체크
def check_direction_similarity(user_contour, expected_contour, threshold=1.5):
    # 두 윤곽선의 유사도를 측정하여 threshold 이하이면 유사한 것으로 간주
    similarity = cv2.matchShapes(user_contour, expected_contour, cv2.CONTOURS_MATCH_I1, 0.0)
    return similarity < threshold

# 전체 크기 비교
def check_overall_size(user_contour, expected_contour, size_ratio_threshold=0.5):
    # 사용자 윤곽선과 기대 윤곽선의 면적을 비교하여 기준치 이상이면 True 반환
    user_area = cv2.contourArea(user_contour)
    expected_area = cv2.contourArea(expected_contour)
    return user_area >= size_ratio_threshold * expected_area

# 전체 채점 및 시각화 함수
def star_score_result(user_star_image_path, expected_star_image_path):
    # 사용자와 기대 이미지를 불러와 전처리
    user_image, user_edges = load_and_preprocess_image(user_star_image_path)
    expected_image, expected_edges = load_and_preprocess_image(expected_star_image_path)

    # 윤곽선을 찾아 가장 큰 윤곽선을 선택
    contours_user, _ = cv2.findContours(user_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_expected, _ = cv2.findContours(expected_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    user_contour = max(contours_user, key=cv2.contourArea) if contours_user else None
    expected_contour = max(contours_expected, key=cv2.contourArea) if contours_expected else None

    # 윤곽선을 찾지 못하면 에러 메시지 반환
    if user_contour is None or expected_contour is None:
        return "윤곽선을 찾을 수 없습니다."

    # 사용자 및 기대 이미지에 꼭짓점과 윤곽선 시각화
    user_image_with_annotations = draw_vertices_and_contours(user_image.copy(), user_contour)
    expected_image_with_annotations = draw_vertices_and_contours(expected_image.copy(), expected_contour)

    # 시각화된 이미지 화면에 표시
    cv2.imshow("User Star Contours and Vertices", user_image_with_annotations)
    cv2.imshow("Expected Star Contours and Vertices", expected_image_with_annotations)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # 채점
    score = 0
    result_details = []

    # 각 기준별 채점 및 결과 메시지 생성
    if check_vertices(user_contour):
        score += 1
        result_details.append("기본 모양: 1점 획득")
    else:
        result_details.append("기본 모양: 0점 획득")

    if check_if_closed(user_contour):
        score += 1
        result_details.append("닫힘: 1점 획득")
    else:
        result_details.append("닫힘: 0점 획득")

    if check_vertex_size_similarity(user_contour):
        score += 1
        result_details.append("윤곽선: 1점 획득")
    else:
        result_details.append("윤곽선: 0점 획득")

    if check_direction_similarity(user_contour, expected_contour):
        score += 1
        result_details.append("방향: 1점 획득")
    else:
        result_details.append("방향: 0점 획득")

    if check_overall_size(user_contour, expected_contour):
        score += 1
        result_details.append("전체 크기: 1점 획득")
    else:
        result_details.append("전체 크기: 0점 획득")

    # 채점 결과 요약 반환
    return f"별 채점 결과: {score}/5점\n" + "\n".join(result_details)

# 이미지 파일 경로 설정
user_star_image_path = "C:/Users/jimin/OneDrive/star_image/user_star_image1.png"
expected_star_image_path = "C:/Users/jimin/OneDrive/star_image/expected_star_image.png"

# 채점 함수 호출 및 결과 출력
result = star_score_result(user_star_image_path, expected_star_image_path)
print(result)



#이미지 확인 후 이미지를 꺼주셔야 결과가 출력됩니다 형님


