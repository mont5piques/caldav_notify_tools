import requests

def send_sms(free_user_id, free_pass, content):
    r = requests.get(
        "https://smsapi.free-mobile.fr/sendmsg",
        params={
            "user" : free_user_id,
            "pass" :free_pass,
            "msg" : content
        }
    )
    return r.status_code == 200
