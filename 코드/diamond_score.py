import cv2
import math
import numpy as np
from skimage.draw import line
import os
import size_equalize
IMAGESIZE = 1000


def diamond_score_result(dst_draw_diamond : cv2.typing.MatLike, dst_exp_diamond : cv2.typing.MatLike):
    
    basic_shape = False
    closing = False
    contours = False
    entire_size = False
    direction = False

    # gray 변경후, 도형 외곽선 구하기 위한 Threshold 구하기
    gray_draw_diamond = cv2.cvtColor(dst_draw_diamond.copy(), cv2.COLOR_BGR2GRAY)
    gray_exp_diamond = cv2.cvtColor(dst_exp_diamond.copy(), cv2.COLOR_BGR2GRAY)
    move_pnt = np.float32([[0, 0], [0, 1000], [1000, 0], [1000, 1000]])

    # 겉에 남아있을수 있는 칸 윤곽선 밖으로 밀어내기
    resize = np.float32([[10, 10], [10, 990], [990, 10], [990, 990]])
    perspective_edit = cv2.getPerspectiveTransform(resize, move_pnt)

    gray_draw_diamond = cv2.warpPerspective(gray_draw_diamond, perspective_edit, (IMAGESIZE, IMAGESIZE))
    gray_exp_diamond = cv2.warpPerspective(gray_exp_diamond, perspective_edit, (IMAGESIZE, IMAGESIZE))
    dst_draw_diamond = cv2.warpPerspective(dst_draw_diamond, perspective_edit, (IMAGESIZE, IMAGESIZE))
    dst_exp_diamond = cv2.warpPerspective(dst_exp_diamond, perspective_edit, (IMAGESIZE, IMAGESIZE))

    # cv2.imshow("exp", gray_exp_diamond)
    # cv2.imshow("draw", gray_draw_diamond)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    # 도형 외곽선 구하기
    edges_draw_diamond = cv2.Canny(gray_draw_diamond.copy(), 20, 40, L2gradient = True) # Canny Edge
    edges_draw_diamond = cv2.blur(edges_draw_diamond.copy(), (43, 43))
    _, edges_draw_diamond = cv2.threshold(edges_draw_diamond.copy(), 3, 255, cv2.THRESH_BINARY)
    edges_draw_diamond = cv2.blur(edges_draw_diamond.copy(), (43, 43))
    _, edges_draw_diamond = cv2.threshold(edges_draw_diamond.copy(), 150, 255, cv2.THRESH_BINARY)
    edges_draw_diamond = cv2.erode(edges_draw_diamond.copy(), cv2.getStructuringElement(cv2.MORPH_CROSS, (54, 54)), iterations = 1)
    # edges_draw_diamond = cv2.morphologyEx(edges_draw_diamond.copy(), cv2.MORPH_GRADIENT, cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3)))
    contours_draw_diamond, _ = cv2.findContours(edges_draw_diamond.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE) # 외곽선 찾기

    result_contours_draw_diamond = contours_draw_diamond

    image_draw_diamond = cv2.drawContours(dst_draw_diamond.copy(), result_contours_draw_diamond, -1, (255, 0, 0), 3)

    # 일정 넓이 이상을 가지는 외곽선만 사용
    result_contour_draw_diamond_size = 5000
    real_contours_draw_diamond = []
    for cnt in result_contours_draw_diamond:
        if cv2.contourArea(cnt) >= result_contour_draw_diamond_size:
            real_contours_draw_diamond.append(cnt)

    # image_draw_diamond = cv2.drawContours(dst_draw_diamond.copy(), real_contours_draw_diamond, -1, (255, 0, 0), 3)

    # cv2.imshow("", image_draw_diamond)
    # cv2.imshow("edge", edges_draw_diamond)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    
    # 2개 이상의 외곽선이 검출되었으면, 가장 큰 외곽선 하나만 사용.
    biggest = real_contours_draw_diamond[0]
    if (len(real_contours_draw_diamond) >= 2):
        for cnt in real_contours_draw_diamond:
            if (cv2.contourArea(biggest) <= cv2.contourArea(cnt)):
                biggest = cnt

    # 뒤에서 사용 ( 크기 비교 기준 적용 )
    if len(real_contours_draw_diamond) >= 2: # 끊김 없는 윤곽선
        cnt_area_draw_diamond = cv2.contourArea(biggest)
    else: # 끊김 있는 윤곽선
        cnt_area_draw_diamond = cv2.contourArea(cv2.convexHull(biggest)) # 볼록하게 피기
    # extremes = get_extreme_points(cv2.approxPolyDP(biggest, 0.005 * cv2.arcLength(biggest, True), True))
    # print(extremes)




    # # # # # '마름모' 평가기준 1 ( '꼭짓점이 구분되는' / '면이 구분되는' 마름모 )
    # {

    black_back = np.zeros((IMAGESIZE, IMAGESIZE), np.uint8)
    corner_image = cv2.drawContours(black_back.copy(), [cv2.convexHull(biggest)], -1, 255, thickness = 3, lineType = cv2.LINE_AA)
    draw_cnt = cv2.drawContours(dst_draw_diamond.copy(), [cv2.convexHull(biggest)], -1, 255, thickness = 3, lineType = cv2.LINE_AA)

    _, for_minbox = cv2.threshold(corner_image.copy(), 5, 255, cv2.THRESH_BINARY)

    # cv2.imshow("", for_minbox)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    contours_for_minbox, _ = cv2.findContours(for_minbox.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)[0]

    # cv2.imshow("", cv2.drawContours(black_back.copy(), contours_for_minbox, -1, 255))
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    min_box = cv2.minAreaRect(contours_for_minbox) # 가장 짧은 선분의 길이를 근사하게 구하기 위함.
    (x, y), (draw_diamond_w, draw_diamond_h), _ = min_box
    min_box = cv2.boxPoints(min_box)
    # print(min_box)
    min_box = np.intp(min_box)
    # result = cv2.drawContours(black_back.copy(), [min_box], 0, 255, 2)
    # result = cv2.drawContours(result, biggest, -1, (255,0,0), 2)
    # cv2.imshow("", result)
    # cv2.waitKey()
    # cv2.destroyAllWindows()


    # cv2.imshow("drawCnt", draw_cnt)
    # cv2.imshow("corners", corner_image)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    # 가장 짧은 선분 기준으로 극점 찾음
    shortest_len = draw_diamond_h
    if (shortest_len > draw_diamond_w):
        shortest_len = draw_diamond_w

    # print(draw_diamond_h, draw_diamond_w)

    corners = cv2.goodFeaturesToTrack(corner_image.copy(), 100, 0.03, shortest_len // 4, blockSize = 5)

    # print(corners)

    # 직각에 근접한 꼭짓점들만 추출해 확인.
    real_corners = []
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

            if ( ((degree >= 35) & (degree <= 55))
                | ((degree >= 125) & (degree <= 145))
                | ((degree <= -35) & (degree >= -55))
                | ((degree <= -125) & (degree >= -145)) ) :
                counter += 1 # 유효한 각
        if (counter >= 2):
            # print("yes")
            # cv2.circle(corner_image, (int(corner[0][0]), int(corner[0][1])), 5, 150, thickness = 2)
            # cv2.circle(draw_cnt, (int(corner[0][0]), int(corner[0][1])), 5, (0, 0, 255), thickness = 2)
            real_corners.append(corner)
        # print()


    # 만약의 경우, 같은 직선상에 여러개가 검출될 경우, 가장 먼 거리에 있는 점만 처리하도록 결과 수정.
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


    removed = []
    # print(len(to_remove))
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
        else:
            for obj2 in removed: # 이미 제거한 대상에서 탐색
                if (obj == obj2).all(): # 이미 제거한 대상은 스킵
                    continue
                else:
                    for inx in range(len(real_corners)):
                        if (obj == real_corners[inx]).all():
                            find = True
                            # print(obj, real_corners[inx])
                            removed.append(obj)
                            remove_inx = inx
                    if(find):
                        find = False
                        real_corners.pop(remove_inx)


    # for corner in real_corners:
    #     cv2.circle(corner_image, (int(corner[0][0]), int(corner[0][1])), 5, 150, thickness = 2)
    #     cv2.circle(draw_cnt, (int(corner[0][0]), int(corner[0][1])), 5, (0, 255, 0), thickness = 2)

    score_diamond = 0

    if (len(real_corners) == 4):
        # print("diamond")
        score_diamond += 1
        basic_shape = True

    # cv2.imwrite("./result_image/draw_square_corners.jpg", draw_cnt)
    # cv2.imshow("approx", cv2.drawContours(dst_draw_diamond.copy(), cv2.approxPolyDP(biggest, 0.005 * cv2.arcLength(biggest, True), True), -1, 255, thickness = 3))
    # for corner in corners:
    #     cv2.circle(test, (int(corner[0][0]), int(corner[0][1])), 5, 125, thickness = 2)
    # cv2.imshow("test", test)

    # 이미지 확인용
    # cv2.imshow("drawCnt", draw_cnt)
    # cv2.imshow("corners", corner_image)
    # cv2.waitKey()
    # cv2.destroyAllWindows()








    if score_diamond >= 1: # score >= 1
        # '마름모' 평가기준 2 [!(가장긴 선분 >= 가장 짧은 선분 * 1.5)] # 선분 길이는 꼭짓점을 이용해 점사이 거리를 이용해 측정한다.
        # {
        min_dist = 1000
        max_dist = 0
        for point in real_corners:
            for other in real_corners:
                if (other == point).all():
                    continue
                else:
                    degree = (math.floor((180.0 / math.pi) 
                            * math.atan2(other[0][1] - point[0][1], other[0][0] - point[0][0])))
                    # print(degree)
                    # print(point, other)
                    if( ( (degree >= 25) & (degree <= 55) ) # 각도가 직각일때,
                        | ( (degree >= 115) & (degree <= 155) )
                        | ( (degree <= -25) & (degree >= -65) )
                        | ( (degree <= -115) & (degree >= -155) )):
                        dist = (math.sqrt(math.pow(other[0][1] - point[0][1], 2)
                                        + math.pow(other[0][0] - point[0][0], 2))) # 두 점 사이 거리
                        # print(dist)
                        # print()
                        if (dist < min_dist):
                            min_dist = dist
                        if (dist > max_dist):
                            max_dist = dist
                    # print()
        if ((max_dist) <= (min_dist * 1.5)):
            score_diamond += 1
            # print("diamond")
            contours = True
        # }

    
    
    
    
    
    
        # '마름모' 평가기준 3 ( 전체 크기 >= [예시 도형 크기 / 2] )
        # {
        edge_exp_diamond = cv2.Canny(gray_exp_diamond, 30, 55, L2gradient = True)
        contours_exp_diamond, _ = cv2.findContours(edge_exp_diamond.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

        exp_biggest = contours_exp_diamond[0]
        for exp_cnt in contours_exp_diamond:
            if cv2.contourArea(exp_cnt) > cv2.contourArea(exp_biggest):
                exp_biggest = exp_cnt
        
        cnt_area_exp_diamond = cv2.contourArea(exp_biggest)

        if cnt_area_draw_diamond >= (cnt_area_exp_diamond / 2):
            # print("diamond")
            score_diamond += 1
            entire_size = True

        # cv2.imshow("", edge_exp_diamond)
        # cv2.waitKey()
        # cv2.destroyAllWindows()
        # }









        # '마름모' 평가기준 4 ( 외곽선이 끊김 없이 이어지는가 )
        # {
        """
        윤곽선이 두개 존재한다 가정.
        두 윤곽선이 한 직선에 대해 몇번 교차하는지 셂
        """
        ROTATE45 = cv2.getRotationMatrix2D((IMAGESIZE // 2, IMAGESIZE // 2), 45, 1.0)
        closed_test_draw_diamond = cv2.warpAffine(dst_draw_diamond.copy(), ROTATE45, (IMAGESIZE, IMAGESIZE))

        move_pnt = np.float32([[0, 0], [0, 1000], [1000, 0], [1000, 1000]])

        # 겉에 남아있을수 있는 칸 윤곽선 밖으로 밀어내기
        resize = np.float32([[100,100], [100, 900], [900, 100], [900, 900]])
        perspective_edit = cv2.getPerspectiveTransform(resize, move_pnt)

        closed_test_draw_diamond = cv2.warpPerspective(closed_test_draw_diamond.copy(), perspective_edit, (IMAGESIZE, IMAGESIZE))
        closed_test_gray_draw_diamond = cv2.cvtColor(closed_test_draw_diamond.copy(), cv2.COLOR_BGR2GRAY)
        # cv2.imshow("", closed_test_draw_diamond)
        # cv2.waitKey()
        # cv2.destroyAllWindows()

        # 회전한 이미지에서 윤곽선 다시 찾기
        closed_test_edges_draw_diamond = cv2.Canny(closed_test_gray_draw_diamond.copy(), 22, 20, L2gradient = True) # Canny Edge|
        closed_test_edges_draw_diamond = cv2.blur(closed_test_edges_draw_diamond.copy(), (43, 43))
        _, closed_test_edges_draw_diamond = cv2.threshold(closed_test_edges_draw_diamond.copy(), 3, 255, cv2.THRESH_BINARY)
        closed_test_edges_draw_diamond = cv2.morphologyEx(closed_test_edges_draw_diamond.copy(), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10)))
        closed_test_edges_draw_diamond = cv2.erode(closed_test_edges_draw_diamond.copy(), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (49, 49)), iterations = 1)
        closed_test_edges_draw_diamond = cv2.morphologyEx(closed_test_edges_draw_diamond.copy(), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (40, 40)))
        # closed_test_edges_draw_diamond = cv2.morphologyEx(closed_test_edges_draw_diamond.copy(), cv2.MORPH_GRADIENT, cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3)))
        closed_test_contours_draw_diamond, _ = cv2.findContours(closed_test_edges_draw_diamond.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE) # 외곽선 찾기

        test_contours_draw_diamond = []
        for contour in closed_test_contours_draw_diamond:
            if (cv2.contourArea(contour) > 2000): # 테스트를 통해 구해낸, 회전시켜 비어버린 부분을 edge로 감지 못하는 크기
                test_contours_draw_diamond.append(contour)
        
        # test_biggest = cv2.drawContours(black_back.copy(), test_contours_draw_diamond, -1, 255, 3)

        # cv2.imshow("", closed_test_gray_draw_diamond)
        # cv2.imshow("edge", closed_test_edges_draw_diamond)
        # cv2.imshow("res", test_biggest)
        # cv2.waitKey()
        # cv2.destroyAllWindows()
        # print(points)






        # 수직선으로 검사
        pt1_vertical = (0, 0)
        pt2_vertical = (0, IMAGESIZE)
        counter = 0
        disc_count = 0

        org_result = cv2.drawContours(closed_test_draw_diamond.copy(), test_contours_draw_diamond, -1, (255,0,0), 3)

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
                for inx in range(len(test_contours_draw_diamond)):
                    if cv2.pointPolygonTest(test_contours_draw_diamond[inx], (int(pt[0]), int(pt[1])), False) == 0.0:  # If the point is on the contour
                        intersect_count += 1
                        # 확인용 이미지 출력용
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
            # 한 라인의 교차점 체크
            # {
            intersect_count = 0
            for pt in discrete_line:
                # print(pt)
                for inx in range(len(test_contours_draw_diamond)):
                    if cv2.pointPolygonTest(test_contours_draw_diamond[inx], (int(pt[0]), int(pt[1])), False) == 0.0:  # If the point is on the contour
                        intersect_count += 1
                        # 확인용 이미지 출력용
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
            pt1_horizontal = (pt1_horizontal[0], pt1_horizontal[1] + 1)
            pt2_horizontal = (pt2_horizontal[0], pt2_horizontal[1] + 1)
            # cv2.imshow("", result)
            # cv2.waitKey()
            # cv2.destroyAllWindows()
            # cv2.imwrite(f"./images/horizontal/{counter}.jpg", result)
            # counter += 1

        # 끊김 감지 횟수가 4회 이하이면, 끊김 없음 (수직, 수평선으로 두번 검사함 / 윤곽선 검출 결과에 따라 접하는 경우 존재.)
        if intersect_once_count <= 4:
            print("diamond")
            score_diamond += 1
            closing = True
        # }


        # '마름모' 평가기준 5 ( 각도가 예시와 비슷한가. )
        # {
        (_, _),(_, _), angle = bound_rect_draw_diamond = cv2.minAreaRect(biggest) # 각도 (0 ~ 90]
        print("degree : ", str(angle))
        if (angle >= 35) | (angle <= 55):
            print("diamond")
            score_diamond += 1
            direction = True
        # }
        print("Basic Shape : " + str(basic_shape))
        print("Closing : " + str(closing))
        print("Contours : " + str(contours))
        print("Direction : " + str(direction))
        print("Entire Size : " + str(entire_size))
        
    return score_diamond