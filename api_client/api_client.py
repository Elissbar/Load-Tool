import requests

def api_client(stand, token, desc, file):
    payload = {'force': 'true', 'description': f'API-Load: {desc}'}
    headers = {'X-Auth-Token': token}
    data = {"file": open(file, 'rb')}

    response = requests.post(
            f'https://{stand}/api/v1/submit/file',
            verify=False,
            headers=headers,
            data=payload,
            files=data)

    return response.status_code
