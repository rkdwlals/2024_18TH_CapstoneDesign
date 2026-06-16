import cv2
import math
import numpy as np
from skimage.draw import line# 한 직선에 있는 모든 픽셀을 포함해 반환하는 함수 ex) (1,1000),(2,1000),(3,1000),(4,1000) ... (999,1000),(1000,1000)
import os
import size_equalize

IMAGESIZE = 1000

def square_score_result(dst_draw_square : cv2.typing.MatLike, dst_exp_square : cv2.typing.MatLike):
    basic_shape = False
    closing = False
    contours = False
    direction = False
    entire_size = False
    
    
    
    
    # 처리 기준 적용 전 전처리
    # 바이너리 이미지로 변환후, 혹여나 남아있을 바깥의 구분선을 없애기 위한 원근 변경
    gray_exp_square = cv2.cvtColor(dst_exp_square.copy(), cv2.COLOR_BGR2GRAY)
    gray_draw_square = cv2.cvtColor(dst_draw_square.copy(), cv2.COLOR_BGR2GRAY)
    move_pnt = np.float32([[0, 0], [0, 1000], [1000, 0], [1000, 1000]])

    resize = np.float32([[10, 10], [10, 990], [990, 10], [990, 990]])
    perspective_edit = cv2.getPerspectiveTransform(resize, move_pnt)

    gray_draw_square = cv2.warpPerspective(gray_draw_square, perspective_edit, (IMAGESIZE, IMAGESIZE))
    gray_exp_square = cv2.warpPerspective(gray_exp_square, perspective_edit, (IMAGESIZE, IMAGESIZE))
    dst_draw_square = cv2.warpPerspective(dst_draw_square, perspective_edit, (IMAGESIZE, IMAGESIZE))
    dst_exp_square = cv2.warpPerspective(dst_exp_square, perspective_edit, (IMAGESIZE, IMAGESIZE))


    # 도형 외곽선 구하기
    edges_draw_square = cv2.Canny(gray_draw_square.copy(), 13, 25, L2gradient = True) # Canny Edge
    edges_draw_square = cv2.blur(edges_draw_square.copy(), (41, 41))
    _, edges_draw_square = cv2.threshold(edges_draw_square.copy(), 10, 255, cv2.THRESH_BINARY)
    edges_draw_square = cv2.erode(edges_draw_square, cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25)), iterations = 1) # 축소

    contours_draw_square, _ = cv2.findContours(edges_draw_square.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    result_contours_draw_square = contours_draw_square

    image_draw_square = cv2.drawContours(dst_draw_square.copy(), result_contours_draw_square, -1, (255, 0, 0), 3)
    
    # 일정 넓이 이상을 가지는 외곽선만 사용
    # 노이즈로 잡힌 다른 외곽선들을 배제하기 위함.
    result_contour_draw_square_size = 5000
    real_contours_draw_square = []
    for cnt in result_contours_draw_square:
        if cv2.contourArea(cnt) >= result_contour_draw_square_size:
            real_contours_draw_square.append(cnt)

    image_draw_square = cv2.drawContours(dst_draw_square.copy(), real_contours_draw_square, -1, (255, 0, 0), 3)

    # cv2.imshow("exp", gray_exp_square)
    # cv2.imshow("draw", gray_draw_square)
    # cv2.imshow("edge", edges_draw_square)
    # cv2.imshow("drawCnt", image_draw_square)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    
    
    
    
    
    
    # # # # # '사각형' 평가기준 1 ( '꼭짓점이 구분되는' / '면이 구분되는' 사각형 )
    # {
    score_square = 0
    
    # 2개 이상의 외곽선이 검출되었으면, 가장 큰 외곽선 하나만 사용.
    # 외곽선이 1개 검출되었다는 것은, 끊긴 외곽선이라는것
    biggest = real_contours_draw_square[0]
    if (len(real_contours_draw_square) >= 2):
        for cnt in real_contours_draw_square:
            if (cv2.contourArea(biggest) <= cv2.contourArea(cnt)):
                biggest = cnt

    # 뒤에서 사용 ( 크기 비교 기준 적용 )
    if len(real_contours_draw_square) >= 2:
        cnt_area_draw_square = cv2.contourArea(biggest)
    else:
        cnt_area_draw_square = cv2.contourArea(cv2.convexHull(biggest))

    # extremes = get_extreme_points(cv2.approxPolyDP(biggest, 0.005 * cv2.arcLength(biggest, True), True))
    # print(extremes)

    min_box = cv2.minAreaRect(biggest) # 해당 외곽선에 외접하는 사각형을 구해, 가장 짧은 선분의 길이를 근사하게 구하기 위함.
    (x, y), (draw_square_w, draw_square_h), _ = min_box # minAreaRect의 구조. 마지막 변수는 각도를 반환.

    min_box = cv2.boxPoints(min_box) # 외접하는 사각형의 각 꼭짓점 값들 도출
    min_box = np.intp(min_box) # 요소들의 정수화.
    # result = cv2.drawContours(dst_draw_square.copy(), [min_box], 0, (0,0,255), 2)
    # result = cv2.drawContours(result, biggest, -1, (255,0,0), 2)
    # cv2.imshow("", result)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    black_back = np.zeros((IMAGESIZE, IMAGESIZE), np.uint8) # 검은 배경의 IMAGESIZE * IMAGESIZE 의 이미지를 만듬.
    
    # 코너를 검출하는데 지장이 없도록 외곽선을 검은색 배경에 흰 선으로 그어 다시 출력.
    corner_image = cv2.drawContours(black_back.copy(), [cv2.convexHull(biggest)], -1, 255, thickness = 3, lineType = cv2.LINE_AA)
    
    # 테스트용 이미지.
    draw_cnt = cv2.drawContours(dst_draw_square.copy(), [cv2.convexHull(biggest)], -1, 255, thickness = 3, lineType = cv2.LINE_AA)
    # test = corner_image.copy()
    # cv2.imwrite("./result_image/draw_square_convex.jpg", draw_cnt)
    # corner_image = cv2.cvtColor(draw_cnt, cv2.COLOR_BGR2GRAY)




    # 가장 짧은 선분 기준으로 극점 찾음
    shortest_len = draw_square_h

    if (shortest_len > draw_square_w):
        shortest_len = draw_square_w

    # print(draw_square_w, draw_square_h)

    corners = cv2.goodFeaturesToTrack(corner_image, 8, 0.03, shortest_len // 2, blockSize = 10)
    # corners = cv2.cornerHarris(corner_image, 2, 15, 0.04)
    # corners = np.where(corners > 0.1 * corners.max())
    # corners = np.stack((corners[1], corners[0]), axis=-1)
    # corners = list(corners)
    # print(corners)

    # print(len(corners))



    # 직각에 근접한 꼭짓점들만 추출해 확인.

    real_corners = []

    for corner in corners:
        # print(corner)
        # (int(corner[0][0]), int(corner[0][1]))
        counter = 0
        for other in corners:
            if ((other[0][0] == corner[0][0]) & (other[0][1] == corner[0][1])):
                continue
            # 두 점 사이의 각을 구합니다.
            degree = (180.0 / math.pi) * math.atan2(other[0][1] - corner[0][1], other[0][0] - corner[0][0]) # result : -PI ~ PI
            degree = math.floor(degree)
            degree = abs(degree)
            print(corner, degree)
            if ( ((degree >= 80) & (degree <= 110)) # 1사분, 2사분면 사이의 각, # 3사분, 4사분면 사이의 각
                | ((degree >= 0) & (degree <= 10)) # 1사분, 4사분면 사이의 아래의 각, # 1사분, 4사분면 사이의 위의 각
                | ((degree >= 170) & (degree <= 180))): # 2사분, 4사분면 사이의 위의 각, # 2사분, 4사분면 사이의 아래의 각)
                counter += 1 # 유효한 각

        if (counter >= 2):
            # print("yes")
            # cv2.circle(corner_image, (int(corner[0][0]), int(corner[0][1])), 5, 150, thickness = 2)
            # cv2.circle(draw_cnt, (int(corner[0][0]), int(corner[0][1])), 5, (0, 0, 255), thickness = 2)
            real_corners.append(corner)
        print()

    # for point in real_corners:
    #     cv2.circle(draw_cnt, (int(point[0][0]), int(point[0][1])), 5, (0,0,255), thickness = 5, lineType = cv2.LINE_AA)
    
    
    
    # 만약의 경우, 같은 직선상에 여러개가 검출될 경우, 가장 먼 거리에 있는 점만 처리하도록 결과 수정.
    # 같은 직선상에 존재하는지는, 두 점 사이의 각도를 이용해 계산.
    to_remove = []
    if (len(real_corners) > 4):
        gap = 10 # 10도 gap은 같은 직선상에 위치한것으로처리
        for corner in real_corners:
            angles = []
            corner_final = {}
            for other in real_corners:
                if ((other[0][0] == corner[0][0]) & (other[0][1] == corner[0][1])): # 같은 위치는 스킵
                    continue
                
                degree = (180.0 / math.pi) * math.atan2(other[0][1] - corner[0][1], other[0][0] - corner[0][0])
                degree = math.floor(degree)
                if (len(angles) != 0):
                    Similar = False
                    for angle in angles:
                        if (((angle - gap) <= degree) & ((angle + gap) >= degree)): # 각도가 비슷하면
                            Similar = True
                            other_dist = math.sqrt(math.pow(other[0][1] - corner[0][1], 2) + math.pow(other[0][0] - corner[0][0], 2)) # 두 점 사이 거리
                            first_dist = math.sqrt(math.pow(corner_final[angle][0][1] - corner[0][1],2) + math.pow(corner_final[angle][0][0] - corner[0][0],2)) # 두 점 사이 거리
                            if (first_dist < other_dist): # 가장 먼것을 선택, 가까운것은 지울 대상으로 선택
                                to_remove.append(corner_final[angle])
                                corner_final[angle] = other
                            else:
                                to_remove.append(other)
                                continue
                    if (not Similar):
                        corner_final[degree] = other
                        angles.append(degree)
                else:
                    corner_final[degree] = other
                    angles.append(degree)

    
    # 한 직선상에 겹치는 여러 점들을 제거
    removed = []
    print(len(to_remove))
    for obj in to_remove: # 대상들 제거
        remove_inx = 0
        find = False
        if (len(removed) == 0): # 1개도 제거하지 않았을때,
            for inx in range(len(real_corners)):
                if (obj == real_corners[inx]).all(): # 제거할 대상이라면,
                    find = True
                    # print(obj, real_corners[inx])
                    removed.append(obj)
                    remove_inx = inx
            if(find):
                find = False
                real_corners.pop(remove_inx)
        else: # 1개 이상 제거했을시, 
            for obj2 in removed: # 이미 제거한 대상에서 탐색
                if (obj == obj2).all(): # 이미 제거한 대상은 스킵
                    continue
                else: # 이미 제거된 대상이 아니면,
                    for inx in range(len(real_corners)):
                        if (obj == real_corners[inx]).all(): # 제거할 대상이 아직 존재할시,
                            find = True
                            # print(obj, real_corners[inx])
                            removed.append(obj)
                            remove_inx = inx
                    if(find):
                        find = False
                        real_corners.pop(remove_inx)
    
    # 그 결과로 꼭짓점 수가 4개라면
    if (len(real_corners) == 4):
        print("square")
        score_square += 1
        basic_shape = True

    # cv2.imwrite("./result_image/draw_square_corners.jpg", draw_cnt)
    # cv2.imshow("approx", cv2.drawContours(dst_draw_square.copy(), cv2.approxPolyDP(biggest, 0.005 * cv2.arcLength(biggest, True), True), -1, 255, thickness = 3))
    # for corner in corners:
    #     cv2.circle(test, (int(corner[0][0]), int(corner[0][1])), 5, 125, thickness = 2)

    
    # for corner in real_corners:
    #     cv2.circle(corner_image, (int(corner[0][0]), int(corner[0][1])), 5, 150, thickness = 2)
    #     cv2.circle(draw_cnt, (int(corner[0][0]), int(corner[0][1])), 5, (0, 255, 0), thickness = 2)

    # cv2.imshow("test", test)
    # cv2.imshow("drawCnt", draw_cnt)
    # cv2.imshow("corners", corner_image)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    
    
    
    
    
    
    
    
    if score_square >= 1: # score >= 1
        # '사각형' 평가기준 2 [!(가장긴 선분 >= 가장 짧은 선분 * 1.5)] # 점 사이 거리 이용해 측정
        # {
        min_dist = 1000
        max_dist = 0
        for point in real_corners:
            for other in real_corners:
                if (other == point).all():
                    continue
                else:
                    degree = math.floor((180.0 / math.pi) * math.atan2(other[0][1] - point[0][1], other[0][0] - point[0][0]))
                    # print(degree)
                    # print(point, other)
                    degree = abs(degree)
                    if( ( (degree >= 0) & (degree <= 10) )
                        | ( (degree >= 80) & (degree <= 110) )
                        | ( (degree <= 180) & (degree >= 170) )):
                        dist = math.sqrt(math.pow(other[0][1] - point[0][1], 2) + math.pow(other[0][0] - point[0][0], 2)) # 두 점 사이 거리
                        # print(dist)
                        # print()
                        if (dist < min_dist):
                            min_dist = dist
                        if (dist > max_dist):
                            max_dist = dist
                    # print()
        if ((max_dist) <= (min_dist * 1.5)):
            score_square += 1
            # print("square")
            contours = True

        # print (long_ratio, short_ratio)
        # cv2.imwrite("./result_image/draw_square_length.jpg", result)
        # cv2.imshow("", result)
        # cv2.waitKey()
        # cv2.destroyAllWindows()
        # }

    
    
    
    
    
    

        # '사각형' 평가기준 3 ( 전체 크기 >= [예시 도형 크기 / 2] )
        # {
        # 예시 이미지 크기 측정
        edges_exp_square = cv2.Canny(gray_exp_square, 50, 10, L2gradient = True)

        kernel = np.ones((5,5),np.uint8) # 몇배로? ( 5배 )
        edges_exp_square = cv2.dilate(edges_exp_square, kernel, iterations = 2) # 얇은 외곽선 팽창시키기
        edges_exp_square = cv2.medianBlur(edges_exp_square, 25) # 블러 처리로 윤곽선이 블럭처럼 생기지 않게 (각지지 않게)
        edges_exp_square = cv2.erode(edges_exp_square, kernel, iterations = 1) # 축소

        contours_exp_square, _ = cv2.findContours(edges_exp_square, cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_L1)
        result_contours_exp_square = contours_exp_square

        exp_biggest = result_contours_exp_square[0]
        for exp_cnt in result_contours_exp_square:
            if (cv2.contourArea(exp_biggest) <= cv2.contourArea(exp_cnt)):
                exp_biggest = exp_cnt

        # 예시 이미지 윤곽선이 덮는 넓이 반환
        cnt_area_exp_square = cv2.contourArea(exp_biggest)

        if cnt_area_draw_square >= (cnt_area_exp_square / 2):
            # print("close to square")
            score_square += 1
            entire_size = True

        # }

    


        # '사각형' 평가기준 4 ( 윤곽선이 끊김 없이 이어지는가 )
        # {
        """
        윤곽선이 두개 존재한다 가정.
        두 윤곽선이 한 직선에 대해 몇번 교차하는지 셂
        
        수평선, 수직선 두번의 과정을 거쳐 각각의 작선에 접하는 횟수로 연산을 함
        """

        # print(points)

        # 수직선으로 검사
        pt1_vertical = (0, 0)
        pt2_vertical = (0, IMAGESIZE)

        counter = 0
        
        disc_count = 0
        
        org_result = cv2.drawContours(dst_draw_square.copy(), real_contours_draw_square, -1, (255, 0, 0), 3)
        # cv2.imshow("", org_result)
        # cv2.waitKey()
        # cv2.destroyAllWindows()
        intersect_once_count = 0

        while not(pt1_vertical[0] > IMAGESIZE): # 이미지 끝까지 (수직선)
            print(f"Line coordinate : {pt1_vertical}, {pt2_vertical}")
            pt1_cal = (int(pt1_vertical[0]), int(pt1_vertical[1]))
            pt2_cal = (int(pt2_vertical[0]), int(pt2_vertical[1]))
            result = cv2.line(org_result.copy(), pt1_cal, pt2_cal, (0,255,0), thickness = 2)

            # print(pt1, pt2)
            discrete_line = zip(*line(*pt1_cal, *pt2_cal))

            # 한 직선의 교차점 체크
            # {
            intersect_count = 0
            for pt in discrete_line:
                for inx in range(len(real_contours_draw_square)):
                    if cv2.pointPolygonTest(real_contours_draw_square[inx], (int(pt[0]), int(pt[1])), False) == 0.0:  # If the point is on the contour
                        intersect_count += 1
                        # result = cv2.circle(result, pt, 2, (0, 0, 255), 2)
                        # cv2.imshow("", result)
                        # cv2.waitKey()
                        # cv2.destroyAllWindows()
            # }
            print(f"this line's intersect : {intersect_count}")
            if (intersect_count <= 2) & (intersect_count > 0): # 두 번 이하로 교차(접)했으면 (접하지 않는건 카운트 X)
                if (disc_count >= 10): # 10 번 이상 연속으로 2번 접하는가?
                    intersect_once_count += 1 # 카운트
                else:
                    disc_count += 1
            else:
                disc_count = 0
            print(f"Entire intersect : {intersect_once_count}\n\n")
            # 다음 수직선으로 넘김.
            pt1_vertical = (pt1_vertical[0] + 1, pt1_vertical[1])
            pt2_vertical = (pt2_vertical[0] + 1, pt2_vertical[1])

            # cv2.imshow("", result)
            # cv2.waitKey()
            # cv2.destroyAllWindows()
            # cv2.imwrite(f"./images/vertical/{counter}.jpg", result)
            # counter += 1

        # print(intersect_once_count)

        # 수평선으로 검사
        pt1_horizontal = (0, 0)
        pt2_horizontal = (IMAGESIZE, 0)

        counter = 0

        while not(pt1_horizontal[1] > IMAGESIZE): # 이미지 끝까지 (수평선)
            print(f"Line coordinate : {pt1_horizontal}, {pt2_horizontal}")
            pt1_cal = (int(pt1_horizontal[0]), int(pt1_horizontal[1]))
            pt2_cal = (int(pt2_horizontal[0]), int(pt2_horizontal[1]))
            result = cv2.line(org_result.copy(), pt1_cal, pt2_cal, (0,255,0), thickness = 2)

            # print(pt1, pt2)
            discrete_line = zip(*line(*pt1_cal, *pt2_cal))

            # 한 직선의 교차점 체크
            # {
            intersect_count = 0
            for pt in discrete_line:
                # print(pt)
                for inx in range(len(real_contours_draw_square)):
                    if cv2.pointPolygonTest(real_contours_draw_square[inx], (int(pt[0]), int(pt[1])), False) == 0.0:  # 점이 만약 외곽선 위에 위치한 점이라면,
                        intersect_count += 1
                # result = cv2.circle(result, pt, 2, (0, 0, 255), 2)
                # cv2.imshow("", result)
                # cv2.waitKey()
                # cv2.destroyAllWindows() 
                # print(pt)
            # }
            print(f"this line's intersect : {intersect_count}")
            if (intersect_count <= 2) & (intersect_count > 0): # 두 번 이하로 교차(접)했으면 (접하지 않는건 카운트 X)
                if (disc_count >= 10): # 10 번 이상 연속으로 2번 접하는가?
                    intersect_once_count += 1 # 카운트
                else:
                    disc_count += 1
            else:
                disc_count = 0
            print(f"Entire intersect : {intersect_once_count}\n\n")
            # 다음 수평선으로 넘김.
            pt1_horizontal = (pt1_horizontal[0], pt1_horizontal[1] + 1)
            pt2_horizontal = (pt2_horizontal[0], pt2_horizontal[1] + 1)

            # cv2.imshow("", result)
            # cv2.waitKey()
            # cv2.destroyAllWindows()
            # cv2.imwrite(f"./images/horizontal/{counter}.jpg", result)
            # counter += 1


        # 2번 이하로 접한횟수가 4회 이하이면, (수직, 수평선으로 두번 검사함 / 윤곽선 검출 결과에 따라 접하는 경우 존재.)
        if intersect_once_count <= 4:
            # print("close to square")
            score_square += 1
            closing = True
        # }
    
    


        # '사각형' 평가기준 5 ( 각도가 예시와 비슷한가. )
        # {
        (_, _),(_, _), angle = bound_rect_draw_square = cv2.minAreaRect(biggest) # 각도 (0 ~ 90]
        if (angle >= 80) | (angle <= 10):
            print(angle)
            # print("Close to Square")
            score_square += 1
            direction = True
    
    print("Basic Shape : " + str(basic_shape))
    print("Closing : " + str(closing))
    print("Contours : " + str(contours))
    print("Direction : " + str(direction))
    print("Entire Size : " + str(entire_size))
    return score_square