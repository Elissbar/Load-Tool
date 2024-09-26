import json
import requests

def file_send(**kwargs):
    payload = {'force': 'true', 'description': f'API-Load: {kwargs["desc"]}'}
    headers = {'X-Auth-Token': kwargs["token"]}
    data = {"file": open(kwargs['item'], 'rb')}

    response = requests.post(
        f'https://{kwargs["stand"]}/',
        verify=False,
        headers=headers,
        data=payload,
        files=data,
		timeout=0.5
	)

    return response.status_code

def link_send(**kwargs):
	payload = {
		"LinkData": {
        	"Path": kwargs['item']
    	},
		"MessageData": {
			"Force": True,
			"Description": f'Link-Load: {kwargs["desc"]}'
		},
	}
	headers = {'X-Auth-Token': kwargs["token"], 'Content-Type': 'application/json'}

	response = requests.post(
		f'https://{kwargs["stand"]}/',
		verify=False,
		headers=headers,
		data=json.dumps(payload),
		timeout=0.5
	)
	return response.status_code
