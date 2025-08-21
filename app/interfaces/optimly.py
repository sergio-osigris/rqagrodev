
import requests

class ApiException(Exception):
    def __init__(self, status_code: int, message: str, details: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}

class APIRequestHandler:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    def _get_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "x_api_key": self.api_key
        }

    def _handle_response(self, response: requests.Response) -> dict:
        if not response.ok:
            try:
                details = response.json()
            except Exception:
                details = {}
            raise ApiException(
                status_code=response.status_code,
                message=response.text,
                details=details
            )
        return response.json()

    def get(self, endpoint: str,params: dict = None) -> dict:
        response = requests.get(f"{self.base_url}{endpoint}",params=params, headers=self._get_headers())
        return self._handle_response(response)

    def post(self, endpoint: str, payload: dict) -> dict:
        response = requests.post(f"{self.base_url}{endpoint}", json=payload, headers=self._get_headers())
        return self._handle_response(response)

    def put(self, endpoint: str, payload: dict) -> dict:
        response = requests.put(f"{self.base_url}{endpoint}", json=payload, headers=self._get_headers())
        return self._handle_response(response)

    def delete(self, endpoint: str) -> dict:
        response = requests.delete(f"{self.base_url}{endpoint}", headers=self._get_headers())
        return self._handle_response(response)


class OptimlyClient:
    def __init__(self, api_key: str,base_api_url :str = "http://127.0.0.1:3000/") -> None:
        """
        Initialize the SDK

        :param api_key: API key associated with the project.
        """
        self.api_key = api_key
        self.base_api_url = base_api_url
        self.request_handler = APIRequestHandler(self.base_api_url, self.api_key)


    def health_check(self) -> dict:
        """
        Test the API connection with a health check endpoint.
        """
        return self.request_handler.get("/health")


    def new_message(self,chat_id,content,sender):
        payload = {"chat_id":chat_id,"sender": sender, "content": content}
        return self.request_handler.post(f"/external/message/new-message", payload)
        
    def new_chat(self,client_id):
        payload = {"client_id":client_id}
        return self.request_handler.post(f"/external/message/new-chat", payload)
    
    def call_agent(self,chat_id,content):
        payload = {"chat_id":chat_id,"content":content}
        return self.request_handler.post(f"/external/agent", payload)
