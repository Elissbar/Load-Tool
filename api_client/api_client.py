import json
import requests

def file_send(**kwargs):
    payload = {'force': 'true', 'description': f'API-Load: {kwargs["desc"]}'}
    headers = {'X-Auth-Token': kwargs["token"]}
    data = {"file": open(kwargs['file'], 'rb')}

    response = requests.post(
        f'https://{kwargs["stand"]}/api/v1/submit/file',
        verify=False,
        headers=headers,
        data=payload,
        files=data)

    return response.status_code

def link_send(**kwargs):
	payload = {
		"LinkData": {
        	"Path": kwargs['link']
    	},
		"MessageData": {
			"Force": True,
			"Description": f'Link-Load: {kwargs["desc"]}'
		}
	}
	headers = {'X-Auth-Token': kwargs["token"], 'Content-Type': 'application/json'}

	response = requests.post(
		f'https://{kwargs["stand"]}/api/v1/link',
		verify=False,
		headers=headers,
		data=json.dumps(payload)
	)
	return response.status_code