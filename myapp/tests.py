import pytest
import requests



ENDPOINT = "http://localhost:8000/"


# def test_userlogin():
#    data = {"username": "srinivas","password": "abcd"}
#    response = requests.post(ENDPOINT+'api/login/',json=data)
#    assert response.status_code == 200
#    token = response.json().get("access_token")
#    return token

# def test_register():
#     data = {
#         "name": "siiuuuuu",
#         "mobile_number": "8290654477",
#         "email": "siu@gmail.com",
#         "password": "buyer123",
#         "role": "buyer",
#     }
#     response = requests.post(ENDPOINT + 'api/register/', json=data)

#     # Assertions and checks related to the HTTP response
#     assert response.status_code == 201
#     res = response.json()
#     return res


# def test_sendOTP():
#    data = {

#     "email":"abdulrahumankhan20012177@gmail.com",
# }
#    response = requests.post(ENDPOINT+'api/sendOTP/',json=data)
#    assert response.status_code == 200
#    res = response.json()
#    return res


# def test_change_password():
#    data = {
#    "email":"abdulrahumankhan20012177@gmail.com",
#    "otp":"691742",
#    "new_password":"admin123"
#    }
#    response = requests.put(ENDPOINT+'api/change_password/',json=data)
#    assert response.status_code == 200
#    res = response.json()
#    return res



# def test_selling():
#    data = {"username": "abdulkhan","password": "seller123"}
#    response = requests.post(ENDPOINT+'api/login/',json=data)
#    assert response.status_code == 200
   # token = response.json()["token"]
   # print(token)

   # bearer_token = token
   # headers = {'Authorization': f'Bearer {bearer_token}'}

#    data = {
#     "name":"laptop",
#     "description":"laptop, it is most useful to this generation",
#     "model_name":"Acer",
#     "quantity":10,
#     "each_price":67000

# }
#    response = requests.post(ENDPOINT+'api/selling/',headers=headers,json=data)
#    assert response.status_code == 201
#    res = response.json()
#    return res


# def test_buying():
#    data = {"username": "nagaraj","password": "abcd"}
#    response = requests.post(ENDPOINT+'api/login/',json=data)
#    assert response.status_code == 200
#    token = response.json()["token"]
#    print(token)

#    bearer_token = token
#    headers = {'Authorization': f'Bearer {bearer_token}'}

#    data = {
#     "product_name":"Microsoft",
#     "quantity":"31"
#     }
#    response = requests.put(ENDPOINT+'api/buying/',headers=headers,json=data)
#    assert response.status_code == 201
#    res = response.json()
#    return res


if __name__ == '__main__':
   pytest.main([__file__])

