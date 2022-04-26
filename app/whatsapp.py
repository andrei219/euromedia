token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjNmMjliNGNiZGQ5MmMwZmRhMWMwYjcwYjYwZTFiMzAzZTM0MDk4MmU1YmVjZWUyYWFlNGQ0NWE2OTc0Y2UwZmJiZDNlZmNjNGUxMjVmMjI0In0.eyJhdWQiOiI5NTYwMTMyOGUzOThiZmU5N2FiMTk0ZjExNDlmNDBiNCIsImp0aSI6IjNmMjliNGNiZGQ5MmMwZmRhMWMwYjcwYjYwZTFiMzAzZTM0MDk4MmU1YmVjZWUyYWFlNGQ0NWE2OTc0Y2UwZmJiZDNlZmNjNGUxMjVmMjI0IiwiaWF0IjoxNjUwOTAyNjc4LCJuYmYiOjE2NTA5MDI2NzgsImV4cCI6MTk2NjUyMTg3OCwic3ViIjoiIiwic2NvcGVzIjpbImNybTphZG1pbiIsImNybTpiaWxsaW5nIiwibWVkaWE6Y3JlYXRlIiwibWVkaWE6ZGVsZXRlIiwibWVkaWE6cmVhZCIsIm1lc3NhZ2VzOmRlbGV0ZSIsIm1lc3NhZ2VzOnJlYWQiLCJtZXNzYWdlczpzZW5kIiwibWVzc2VuZ2VyOnNldHRpbmdzIiwib2F1dGg6c2NvcGVzOnJlYWQiLCJvYXV0aDp1c2VyczptYW5hZ2UiLCJwYXJ0bmVyOnVzZXJzOm1hbmFnZSIsInN1YnNjcmlwdGlvbnM6Y3JlYXRlIiwic3Vic2NyaXB0aW9uczpkZWxldGUiLCJzdWJzY3JpcHRpb25zOnJlYWQiLCJzdWJzY3JpcHRpb25zOnVwZGF0ZSIsInRlbXBsYXRlczpjcmVhdGUiLCJ0ZW1wbGF0ZXM6ZGVsZXRlIiwidGVtcGxhdGVzOnJlYWQiLCJ0ZW1wbGF0ZXM6dXBkYXRlIiwidXNlcjpwcm9maWxlIiwidXNlcjpwcm9maWxlOnB1YmxpYyIsInVzZXI6c2NvcGVzIiwid2ViaG9va3M6Y3JlYXRlIiwid2ViaG9va3M6ZGVsZXRlIiwid2ViaG9va3M6cmVhZCIsIndlYmhvb2tzOnVwZGF0ZSJdLCJjdXN0b21lcl9pZCI6MTAyMzI0MH0.aYZr5E0H2ClBB8_AePC2ZKMpufUtfFSteD7DrI9MzQLcil4e7Y6vZKUF3ou1DvYszB1i-OkEuP79oJ8tmDk2xYh4HuyWobJtd-rKjdx-rGGkk-Ph4iTBddWbiocfppqys7kk1qdb9XRJHy2xDlC8b9aYzBKNGszKmlZ4VAIYH4vCCNGIPcRi7NTjFvX022NVZqLTbgoezy72Wvh_ApqugeCMGZ0Qqhn3Rlrxcbs5ZXfMUP6Q-YGINLJwyQYV-KKCSzzi5DE-lH8Uki-MKTrIscQzw1GX5WqaV3Na-FHdUpT7wsQoIYforA3D7wUn9sEN_XarqfTLWpH3WHC5FCWG9Q"
import json
import requests

if __name__ == '__main__':
    url = "https://api.messengerpeople.dev/messages"

    channel_uuid = "e6a8ccbd-ed27-48cd-b787-e281174f2626"
    recipient = "34673567274"
    headers = {
        "Content-Type": "application/vnd.messengerpeople.v1+json",
        "Accept": "application/vnd.messengerpeople.v1+json",
        "Authorization": f"Bearer {token}"
    }

    data = {
        "identifier": f"{channel_uuid}:{recipient}",
        "payload": {
            "type": "text",
            "text": "Hi from python 3!",
        }
    }

    import json

    response = requests.post(
        url=url,
        headers=headers,
        data=json.dumps(data)
    )
#
#
# import requests
#
# response = requests.delete(
#     "https://api.messengerpeople.dev/messages/bd160eb6-994e-45cb-9b06-685324269c0c",
#     headers={
#         "Content-Type": "application/vnd.messengerpeople.v1+json",
#         "Accept": "application/vnd.messengerpeople.v1+json",
#         "Authorization": f"Bearer {token}",
#     },
# )
#
#
print(json.dumps(response.json(), indent=4))

