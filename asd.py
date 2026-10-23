import requests
import json

url = "https://kauth.kakao.com/oauth/token"

data = {
    "grant_type" : "authorization_code",
    "client_id" : "c8d9e48bba0d97cc755c460bd37f6320",
    "redirect_uri" : "https://superoreo.kr",
    "code"         : "7vCRUzXPUk5XsQ7Ax5Jjm_u-TosuPAelvEdPfjP7QZoycCjFQqVpuQAAAAQKKcleAAABkmLI2oG2xj-RG-1vuA"
    
}
response = requests.post(url, data=data)

tokens = response.json()

print(tokens)