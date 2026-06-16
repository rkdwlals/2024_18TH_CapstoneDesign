import cv2
import math
import numpy as np
from skimage.draw import line # 한 직선에 있는 모든 픽셀을 포함해 반환하는 함수 ex) (1,1000),(2,1000),(3,1000),(4,1000) ... (999,1000),(1000,1000)
import os

IMAGESIZE = 1000


def get_extreme_points(img : cv2.typing.MatLike):
    gray = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2GRAY)

    # 도형 외곽선 구하기
    edges = cv2.Canny(gray.copy(), 35, 55, L2gradient = True) # Canny Edge
    edges = cv2.dilate(edges.copy(), cv2.getStructuringElement(cv2.MORPH_RECT, (4,4))) # 팽창
    edges = cv2.morphologyEx(edges.copy(), cv2.MORPH_OPEN, (25,25)) # Opening 연산
    edges = cv2.medianBlur(edges.copy(), 11) # 평균 블러링
    edges = cv2.blur(edges.copy(), (15, 15)) # 블러링
    _, edges = cv2.threshold(edges.copy(), 10, 255, cv2.THRESH_BINARY) # 임계값 상승
    edges = cv2.erode(edges, cv2.getStructuringElement(cv2.MORPH_RECT, (15,15)), iterations = 1) # 축소
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE) # 외곽선 도출
    result_contours = contours

    
    # cv2.imshow("", cv2.drawContours(gray.copy(), result_contours, -1, 0, 3))
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    
    
    
    
    
    
    # 일정 넓이 이상을 가지는 외곽선만 사용
    result_contour_size = 5000
    real_contours = []
    for cnt in result_contours:
        if cv2.contourArea(cnt) >= result_contour_size:
            real_contours.append(cnt)

    
    biggest = real_contours[0]
    if (len(real_contours) >= 2):
        for cnt in real_contours:
            if (cv2.contourArea(biggest) <= cv2.contourArea(cnt)):
                biggest = cnt

    # test = cv2.drawContours(gray.copy(), biggest, -1, 0, 3)
    # cv2.imshow("", test)
    # cv2.waitKey()
    # cv2.destroyAllWindows()






    min_box = cv2.minAreaRect(biggest) # (외곽선으로 그려진) 원에 외접하는 사각형 하나를 찾음
    (x, y), (w, h), _ = min_box

    black_back = np.zeros((IMAGESIZE, IMAGESIZE), np.uint8)
    corner_image = cv2.drawContours(black_back.copy(), [cv2.convexHull(biggest)], -1, 255, thickness = 3, lineType = cv2.LINE_AA)
    draw_cnt = cv2.drawContours(gray.copy(), [cv2.convexHull(biggest)], -1, 255, thickness = 3, lineType = cv2.LINE_AA)
    # min_box = cv2.boxPoints(min_box)
    # # print(min_box)
    # min_box = np.intp(min_box)
    # minbox_image = cv2.drawContours(draw_cnt.copy(), [min_box], -1, 150, 3, lineType = cv2.LINE_AA)
    
    
    # 가장 짧은 선분 기준으로 특이점 찾음
    shortest_len = h

    if (shortest_len > w):
        shortest_len = w

    # cv2.imshow("",minbox_image)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    
    corners = cv2.goodFeaturesToTrack(corner_image, 8, 0.03, shortest_len // 3, blockSize = 10)


    real_corners = []

    # 실제로 꼭짓점으로 평가 가능한 점인지 다른 점들과의 각도를 이용해 선별
    for corner in corners:
        # print(corner)
        # (int(corner[0][0]), int(corner[0][1]))
        counter = 0

        for other in corners:
            if ((other[0][0] == corner[0][0]) & (other[0][1] == corner[0][1])):
                continue
            degree = (180.0 / math.pi) * math.atan2(other[0][1] - corner[0][1], other[0][0] - corner[0][0]) # result : -PI ~ PI
            degree = math.floor(degree)
            # print(corner, degree)
            if ( ((degree >= 80) & (degree <= 110)) # 1사분, 2사분면 사이의 각
                | ((degree <= 0) & (degree >= -10)) # 1사분, 4사분면 사이의 위의 각
                | ((degree >= 0) & (degree <= 10)) # 1사분, 4사분면 사이의 아래의 각
                | ((degree >= 170) & (degree <= 180)) # 2사분, 4사분면 사이의 위의 각
                | ((degree >= -180) & (degree <= -170)) # 2사분, 4사분면 사이의 아래의 각
                | ((degree <= -80) & (degree >= -110)) ) : # 3사분, 4사분면 사이의 각
                counter += 1 # 유효한 각

        if (counter >= 2):
            # print("yes")
            cv2.circle(corner_image, (int(corner[0][0]), int(corner[0][1])), 5, 150, thickness = 2)
            cv2.circle(draw_cnt, (int(corner[0][0]), int(corner[0][1])), 5, (0, 0, 255), thickness = 2)
            real_corners.append(corner)
        # print()
        
    # print(real_corners)
    
    # cv2.imshow("test", test)
    # cv2.imshow("drawCnt", draw_cnt)
    # cv2.imshow("corners", corner_image)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    result_corners = []
    
    # 각각의 4개의 꼭짓점을 위치별로 분류해 반환함.
    left_up = [IMAGESIZE, IMAGESIZE] # 왼쪽 위 ( 비교 위해 오른쪽 아래로 )
    left_down = [IMAGESIZE, 0] # 왼쪽 아래 ( 비교 위해 오른쪽 위로)
    right_up = [0, IMAGESIZE] # 오른쪽 위 ( 비교 위해 왼쪽 아래로 )
    right_down = [0, 0] # 오른쪽 아래 ( 비교 위해 왼쪽 위로 )

    gap = 80

    for point in real_corners:
        left_up_x = (left_up[0] >= (point[0][0] + gap)) | (left_up[0] >= (point[0][0] - gap))
        left_up_y = (left_up[1] >= (point[0][1] + gap)) | (left_up[1] >= (point[0][1] - gap))

        left_down_x = (left_down[0] >= (point[0][0] + gap)) | (left_down[0] >= (point[0][0] - gap))
        left_down_y = (left_down[1] <= (point[0][1] + gap)) | (left_down[1] <= (point[0][1] - gap))

        right_up_x = (right_up[0] <= (point[0][0] + gap)) | (right_up[0] <= (point[0][0] - gap))
        right_up_y = (right_up[1] >= (point[0][1] + gap)) | (right_up[1] >= (point[0][1] - gap))

        right_down_x = (right_down[0] <= (point[0][0] + gap)) | (right_down[0] <= (point[0][0] - gap))
        right_down_y = (right_down[1] <= (point[0][1] + gap)) | (right_down[1] <= (point[0][1] - gap))

        if left_up_x & left_up_y: # 왼쪽 위
            left_up[0] = point[0][0]
            left_up[1] = point[0][1]
        if left_down_x & left_down_y: # 왼쪽 아래
            left_down[0] = point[0][0]
            left_down[1] = point[0][1]
        if right_up_x & right_up_y: # 오른쪽 위
            right_up[0] = point[0][0]
            right_up[1] = point[0][1]
        if right_down_x & right_down_y: # 오른쪽 아래
            right_down[0] = point[0][0]
            right_down[1] = point[0][1]
    result_corners.append(left_up)
    result_corners.append(left_down)
    result_corners.append(right_up)
    result_corners.append(right_down)
    return result_corners
