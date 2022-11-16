import json
import requests

def file_send(stand, token, desc, file):
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

def link_send(stand, token, desc, link):
	payload = {
		"LinkData": {
        	"Path": link
    	},
		"MessageData": {
			"Force": True,
			"Description": f'Link-Load: {desc}'
		}
	}
	headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}

	response = requests.post(
		f'https://{stand}/api/v1/link',
		verify=False,
		headers=headers,
		data=json.dumps(payload)
	)
	return response.status_code