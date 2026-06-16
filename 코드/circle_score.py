import cv2
import math
import numpy as np
from skimage.draw import line
import os
import size_equalize 

IMAGESIZE = 1000

def circle_score_result(dst_draw_circle : cv2.typing.MatLike, dst_exp_circle : cv2.typing.MatLike):
    basic_shape = False
    closing = False
    contours = False
    entire_size = False

    # gray 변경후, 도형 외곽선 구하기 위한 Threshold 구하기
    gray_draw_circle = cv2.cvtColor(dst_draw_circle, cv2.COLOR_BGR2GRAY)
    gray_exp_circle = cv2.cvtColor(dst_exp_circle, cv2.COLOR_BGR2GRAY)

    move_pnt = np.float32([[0, 0], [0, 1000], [1000, 0], [1000, 1000]])
    # 겉에 남아있을수 있는 칸 윤곽선 밖으로 밀어내기

    resize = np.float32([[10, 10], [10, 990], [990, 10], [990, 990]])
    perspective_edit = cv2.getPerspectiveTransform(resize, move_pnt)

    gray_draw_circle = cv2.warpPerspective(gray_draw_circle, perspective_edit, (IMAGESIZE, IMAGESIZE))
    gray_exp_circle = cv2.warpPerspective(gray_exp_circle, perspective_edit, (IMAGESIZE, IMAGESIZE))
    dst_draw_circle = cv2.warpPerspective(dst_draw_circle, perspective_edit, (IMAGESIZE, IMAGESIZE))
    dst_exp_circle = cv2.warpPerspective(dst_exp_circle, perspective_edit, (IMAGESIZE, IMAGESIZE))

    # cv2.imshow("draw", dst_draw_circle)
    # cv2.imshow("exp", dst_exp_circle)

    # cv2.waitKey()
    # cv2.destroyAllWindows()
    # cv2.imwrite("./result_image/draw_circle_zoom.jpg", gray_draw_circle)



    # 도형 외곽선 구하기

    edges_draw_circle = cv2.Canny(gray_draw_circle.copy(), 20, 40, L2gradient = True) # Canny Edge
    edges_draw_circle = cv2.blur(edges_draw_circle.copy(), (43, 43))
    _, edges_draw_circle = cv2.threshold(edges_draw_circle.copy(), 1, 255, cv2.THRESH_BINARY)
    edges_draw_circle = cv2.erode(edges_draw_circle, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (36, 36)), iterations = 1) # 축소

    contours_draw_circle, _ = cv2.findContours(edges_draw_circle.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE) # 외곽선 찾기

    result_contours_draw_circle = contours_draw_circle
    image_draw_circle = cv2.drawContours(dst_draw_circle.copy(), result_contours_draw_circle, -1, (255, 0, 0), 3)
    # 이미지 확인용 코드
    # cv2.imwrite("./result_image/draw_circle_edge.jpg", edges_draw_circle)
    # cv2.imwrite("./result_image/draw_circle_polygon.jpg", image_draw_circle)
    # for cnt_draw_circle in result_contours_draw_circle:
    #     cnt_length_draw_square = cv2.arcLength(cnt_draw_square, True)
    #     approx_draw_square = cv2.approxPolyDP(cnt_draw_square, 0.005 * cnt_length_draw_square, True)
    #     for point in approx_draw_square:
    #         cv2.circle(image_draw_square, (point[0][0], point[0][1]), 3, (0, 255, 0), -1)
    # cv2.imshow("", image_draw_circle)
    # cv2.imshow("gray", gray_draw_circle)
    # cv2.imshow("org", dst_draw_circle)
    # cv2.imshow("edge", edges_draw_circle)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    # 일정 넓이 이상을 가지는 외곽선만 사용
    result_contour_draw_circle_size = 5000
    real_contours_draw_circle = []
    for cnt in result_contours_draw_circle:
        if cv2.contourArea(cnt) >= result_contour_draw_circle_size:
            real_contours_draw_circle.append(cnt)

    image_draw_circle = cv2.drawContours(dst_draw_circle.copy(), real_contours_draw_circle, -1, (255, 0, 0), 3)

    # for a in real_contours_draw_circle:
    #     cv2.imshow("", cv2.drawContours(dst_draw_circle.copy(), [a], -1, (0, 255, 0), 3))
    #     cv2.waitKey()
    #     cv2.destroyAllWindows()

    # print(len(real_contours_draw_circle))
    # cv2.imwrite("./result_image/draw_circle_problem_edge.jpg", edges_draw_circle)
    # cv2.imshow("", image_draw_circle)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    score_circle = 0





    # # # # # '원' 평가기준 1 ( '모양에 각이 없는' 원 )
    # {

    # 가장 바깥의 외곽선 한개 구하기
    biggest = real_contours_draw_circle[0]
    if (len(real_contours_draw_circle) >= 2):
        for cnt in real_contours_draw_circle:
            if (cv2.contourArea(biggest) <= cv2.contourArea(cnt)):
                biggest = cnt

    # 아동 이미지가 얼마나 원과 유사한가 확인
    # approx_draw_circle = cv2.approxPolyDP(result_contour_draw_circle, 0.05 * cnt_length_draw_circle, True)

    # https://www.geeksforgeeks.org/find-circles-and-ellipses-in-an-image-using-opencv-python/
    # https://deep-learning-study.tistory.com/241
    # ratio가 1에 가까울수록 원형
    # 4 * pi * (pi * r^2) / (2 * pi * r) ^ 2 ==> (2 * pi * r) ^ 2 / (2 * pi * r) ^ 2 

    # 끊긴 원일경우 ==> 볼록하게 만든 도형 외곽선으로 비교
    # 연결된 원일경우 ==> 가장 바깥의 외곽선을 구한걸 그대로 사용
    # 각각의 상태에 맞게 원과의 유사도 계산.
    if (len(real_contours_draw_circle) == 1):
        cnt_length_draw_circle = cv2.arcLength(cv2.convexHull(biggest), True)
        cnt_area_draw_circle = cv2.contourArea(cv2.convexHull(biggest))
        circle_ratio = 4 * math.pi * cnt_area_draw_circle / pow(cnt_length_draw_circle, 2)
    else:
        cnt_length_draw_circle = cv2.arcLength(biggest, True)
        cnt_area_draw_circle = cv2.contourArea(biggest)
        circle_ratio = 4 * math.pi * cnt_area_draw_circle / pow(cnt_length_draw_circle, 2)


    # 예시 사진 원 그림의 외곽선을 아동의 그림과 비교하기 위해 외곽선을 도출.
    edges_exp_circle = cv2.Canny(gray_exp_circle, 50, 10, L2gradient = True)

    kernel = np.ones((5,5),np.uint8) # 몇배로? ( 5배 )
    edges_exp_circle = cv2.dilate(edges_exp_circle, kernel, iterations = 2) # 얇은 외곽선 팽창시키기
    edges_exp_circle = cv2.medianBlur(edges_exp_circle, 25) # 블러 처리로 윤곽선이 블럭처럼 생기지 않게 (각지지 않게)
    edges_exp_circle = cv2.erode(edges_exp_circle, kernel, iterations = 1) # 축소

    contours_exp_circle, _ = cv2.findContours(edges_exp_circle, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_L1)
    result_contours_exp_circle = contours_exp_circle

    exp_biggest = result_contours_exp_circle[0]
    for exp_cnt in result_contours_exp_circle:
        if (cv2.contourArea(exp_biggest) <= cv2.contourArea(exp_cnt)):
            exp_biggest = exp_cnt

    if (circle_ratio > 0.85): # 정사각형의 원과의 유사율이 0.78, 완전한 원이 1.
        if (len(real_contours_draw_circle) == 1):
            base_draw = cv2.convexHull(biggest)
        else:
            base_draw = biggest

        condition = cv2.matchShapes(base_draw, exp_biggest, cv2.CONTOURS_MATCH_I3, 0)
        # (0 => 완전일치, 1 => 완전 불일치)
        if condition <= 0.01:
            print(condition)
            score_circle += 1
            print("close to circle")
            basic_shape = True
        else:
            print("not circle")
    else:
        print("not circle")
    
    # cv2.imwrite("./result_image/draw_circle_convexHull.jpg", cv2.drawContours(gray_draw_circle.copy(), [draw_image_ch], -1, (0,255,0), thickness = 3))
    # print(approx_draw_circle)
    # cv2.imwrite("./result_image/draw_circle_problem.jpg", image_draw_circle)
    # cv2.imshow("ch", image)
    # cv2.imshow("", image_draw_circle)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    # }
    
    
    
    
    
    # 기본 모양 기준 통과시

    if score_circle >= 1: # score >= 1
        # # # # # '원' 평가기준 2 [!(가장긴 지름 >= 가장 짧은 지름 * 3)]
        # {
        draw_circle_area = cv2.contourArea(biggest)
        bound_rect_draw_circle = cv2.minAreaRect(biggest) # (외곽선으로 그려진) 원에 외접하는 사각형 하나를 찾음
        (x, y), (draw_circle_w, draw_circle_h), _ = bound_rect_draw_circle

        bound_rect_draw_circle = cv2.boxPoints(bound_rect_draw_circle)
        bound_rect_draw_circle = np.intp(bound_rect_draw_circle)
        result = cv2.drawContours(dst_draw_circle.copy(), [bound_rect_draw_circle], 0, (0,0,255), 2)
        result = cv2.drawContours(result, biggest, -1, (255,0,0), 2)

        long_ratio = 0
        short_ratio = 0

        if draw_circle_w >= draw_circle_h:
            long_ratio = draw_circle_w
            short_ratio = draw_circle_h
        else:
            long_ratio = draw_circle_h
            short_ratio = draw_circle_w

        # print(draw_circle_w, draw_circle_h)

        if not(long_ratio >= (short_ratio * 3)):
            print("close to circle")
            score_circle += 1
            contours = True

        # cv2.imwrite("./result_image/draw_circle_length.jpg", result)
        # cv2.imshow("", result)
        # cv2.waitKey()
        # cv2.destroyAllWindows()
        # }
        
        
        
        
        
        # # # # # '원' 평가기준 3 ( 전체 크기 >= [예시 도형 크기 / 2] )
        # {
        # 예시 이미지 크기 측정
        edges_exp_circle = cv2.Canny(gray_exp_circle, 50, 10, L2gradient = True)

        kernel = np.ones((5,5),np.uint8) # 몇배로? ( 5배 )
        edges_exp_circle = cv2.dilate(edges_exp_circle, kernel, iterations = 2) # 얇은 외곽선 팽창시키기
        edges_exp_circle = cv2.medianBlur(edges_exp_circle, 25) # 블러 처리로 윤곽선이 블럭처럼 생기지 않게 (각지지 않게)
        edges_exp_circle = cv2.erode(edges_exp_circle, kernel, iterations = 1) # 축소

        contours_exp_circle, _ = cv2.findContours(edges_exp_circle, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_L1)
        result_contours_exp_circle = contours_exp_circle

        exp_biggest = result_contours_exp_circle[0]
        for exp_cnt in result_contours_exp_circle:
            if (cv2.contourArea(exp_biggest) <= cv2.contourArea(exp_cnt)):
                exp_biggest = exp_cnt

        # 예시 이미지 윤곽선이 덮는 넓이 반환
        cnt_area_exp_circle = cv2.contourArea(exp_biggest)

        if cnt_area_draw_circle >= (cnt_area_exp_circle / 2):
            print("close to circle")
            score_circle += 1
            entire_size = True

        # }

    
    
    
    
        # # # # # '원' 평가기준 4 ( 윤곽선이 끊김 없이 이어지는가 )
        # {
        """
        윤곽선이 두개 존재한다 가정.
        두 윤곽선이 한 직선에 대해 몇번 교차하는지 셂
        """

        # print(points)

        # # # # 수직선으로 검사
        pt1_vertical = (0, 0)
        pt2_vertical = (0, IMAGESIZE)

        counter = 0
        disc_count = 0

        org_result = cv2.drawContours(dst_draw_circle.copy(), real_contours_draw_circle, -1, (255, 0, 0), 3)
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

            # 한 라인의 교차점 체크
            # {
            intersect_count = 0
            for pt in discrete_line:
                for inx in range(len(real_contours_draw_circle)):
                    if cv2.pointPolygonTest(real_contours_draw_circle[inx], (int(pt[0]), int(pt[1])), False) == 0.0:  # If the point is on the contour
                        intersect_count += 1
                        result = cv2.circle(result, pt, 2, (0, 0, 255), 2)
                        # cv2.imshow("", result)
                        # cv2.waitKey()
                        # cv2.destroyAllWindows()
            # }
            print(f"this line's intersect : {intersect_count}")
            if (intersect_count <= 2) & (intersect_count > 0): # 두 번 이하로 교차(접)했으면 (접하지 않는건 카운트 X)
                if (disc_count >= 3): # 3 번 이상 연속으로 2번 접하는가?
                    intersect_once_count += 1 # 카운트
                else:
                    disc_count += 1
            else:
                disc_count = 0
            print(f"Entire intersect : {intersect_once_count}\n\n")
            pt1_vertical = (pt1_vertical[0] + 1, pt1_vertical[1])
            pt2_vertical = (pt2_vertical[0] + 1, pt2_vertical[1])

            # cv2.imshow("", result)
            # cv2.waitKey()
            # cv2.destroyAllWindows()
            # cv2.imwrite(f"./images/vertical/{counter}.jpg", result)
            # counter += 1

        # print(intersect_once_count)

        # # # # 수평선으로 검사
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

            # 한 라인의 교차점 체크
            # {
            intersect_count = 0
            for pt in discrete_line:
                # print(pt)
                for inx in range(len(real_contours_draw_circle)):
                    if cv2.pointPolygonTest(real_contours_draw_circle[inx], (int(pt[0]), int(pt[1])), False) == 0.0:  # If the point is on the contour
                        intersect_count += 1
                        result = cv2.circle(result, pt, 2, (0, 0, 255), 2)
                        # cv2.imshow("", result)
                        # cv2.waitKey()
                        # cv2.destroyAllWindows() 
                # print(pt)
            # }
            print(f"this line's intersect : {intersect_count}")
            if (intersect_count <= 2) & (intersect_count > 0): # 두 번 이하로 교차(접)했으면 (접하지 않는건 카운트 X)
                if (disc_count >= 3): # 3 번 이상 연속으로 2번 접하는가?
                    intersect_once_count += 1 # 카운트
                else:
                    disc_count += 1
            else:
                disc_count = 0
            print(f"Entire intersect : {intersect_once_count}\n\n")
            pt1_horizontal = (pt1_horizontal[0], pt1_horizontal[1] + 1)
            pt2_horizontal = (pt2_horizontal[0], pt2_horizontal[1] + 1)

            # cv2.imshow("", result)
            # cv2.waitKey()
            # # cv2.destroyAllWindows()
            # cv2.imwrite(f"./images/horizontal/{counter}.jpg", result)
            # counter += 1


        # 2번 이하로 접한횟수가 4회 이하이면, (수직, 수평선으로 두번 검사함)
        if intersect_once_count <= 4:
            print("close to circle")
            score_circle += 1
            closing = True
        # }
    
    print("\n\n")
    
    print("Basic Shape : " + str(basic_shape))
    print("Closing : " + str(closing))
    print("Contours : " + str(contours))
    print("Entire Size : " + str(entire_size))
    return score_circle