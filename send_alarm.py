import kakao_utils

def send_excel_link():
    KAKAO_TOKEN_FILENAME = "kakao_token.json"  # 카카오 토큰 파일 경로
    KAKAO_APP_KEY = "c8d9e48bba0d97cc755c460bd37f6320"  # 카카오 앱 키
    tokens = kakao_utils.update_tokens(KAKAO_APP_KEY, KAKAO_TOKEN_FILENAME)
    print(tokens)  # Debugging: Check if token update was successful


    # 텍스트 메시지에 엑셀 파일 다운로드 링크 포함
    template = {
        "object_type": "text",
        "text": "엑셀 파일을 다운로드하려면 버튼을 클릭하세요!",
        "link": {
            "web_url": "https://your-file-hosting-service.com/your-excel-file.xlsx",  # 엑셀 파일 다운로드 링크
            "mobile_web_url": "https://your-file-hosting-service.com/your-excel-file.xlsx"
        },
        "button_title": "엑셀 파일 다운로드"
    }

    # 카카오 메시지 전송
    res = kakao_utils.send_message(KAKAO_TOKEN_FILENAME, template)
    if res.json().get('result_code') == 0:
        print('텍스트 메시지를 성공적으로 보냈습니다.')
    else:
        print('텍스트 메시지를 보내지 못했습니다. 오류메시지 : ', res.json())

send_excel_link()