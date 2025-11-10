import httpx
import json
from commun.jwt_access_token import JwtAccessToken

class HttpClient:
    def __init__(self):
        self.base_headers = {
            "Authorization": f"Bearer {JwtAccessToken()}",
            "Content-Type": "application/json",
        }
        self.client = httpx.AsyncClient(headers=self.base_headers)

    async def get(self, url, params=None, headers=None):
        merged_headers = self._merge_headers(headers)
        print(f"\n[GET] {url}")
        print(f"Headers: {merged_headers}")
        print(f"Params: {params}")

        response = await self.client.get(url, headers=merged_headers, params=params)

        self._log_response(response)
        return response

    async def post(self, url, data=None, headers=None):
        merged_headers = self._merge_headers(headers)
        print(f"\n[POST] {url}")
        print(f"Headers: {merged_headers}")
        print(f"Data: {data}")

        response = await self.client.post(url, headers=merged_headers, json=data)

        self._log_response(response)
        return response
    
    async def put(self, url, data=None, headers=None):
        merged_headers = self._merge_headers(headers)
        print(f"\n[PUT] {url}")
        print(f"Headers: {merged_headers}")
        print(f"Data: {data}")

        response = await self.client.put(url, headers=merged_headers, json=data)

        self._log_response(response)
        return response

    async def patch(self, url, data=None, headers=None):
        merged_headers = self._merge_headers(headers)
        print(f"\n[PATCH] {url}")
        print(f"Headers: {merged_headers}")
        print(f"Data: {data}")

        response = await self.client.patch(url, headers=merged_headers, json=data)

        self._log_response(response)
        return response

    async def delete(self, url, headers=None):
        merged_headers = self._merge_headers(headers)
        print(f"\n[DELETE] {url}")
        print(f"Headers: {merged_headers}")

        response = await self.client.delete(url, headers=merged_headers)

        self._log_response(response)
        return response

    def _log_response(self, response: httpx.Response):
        print(f"Response Status: {response.status_code}")
        try:
            print("Response JSON:", json.dumps(response.json(), indent=2))
        except Exception:
            print("Response Text:", response.text)

    def _merge_headers(self, headers):
        if headers:
            merged = self.base_headers.copy()
            merged.update(headers)
            return merged
        return self.base_headers

    async def close(self):
        await self.client.aclose()
