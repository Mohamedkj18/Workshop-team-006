# from config import settings
# import httpx
# from typing import Optional, Dict

import httpx
from typing import Optional, Dict
from config import settings

class UserServiceClient:
    """Client for communicating with the user service"""
    
    def __init__(self):
        self.base_url = settings.USER_SERVICE_URL
        self.timeout = 10.0
    

    # #need to be  async
    # async def verify_token(self, token: str) -> Optional[Dict]:  # NOT async
    #     """Verify user token with user service"""
    #     print(f"Verifying token with user service at: {self.base_url}")
        
    #     # Using synchronous httpx client
    #     with httpx.Client(timeout=self.timeout) as client:
    #         try:
    #             response = client.post(  # No 'await' needed
    #                 f"{self.base_url}/auth/verify",
    #                 json={"token": token}
    #             )
                
    #             print(f"User service response status: {response.status_code}")
                
    #             if response.status_code == 200:
    #                 result = response.json()
    #                 print(f"Token verification result: {result}")
    #                 if result.get("valid"):
    #                     return result.get("user")
                
    #             print(f"Token verification failed: {response.text}")
    #             return None
                
    #         except httpx.RequestError as e:
    #             print(f"Error verifying token with user service: {str(e)}")
    #             return None

    

    async def verify_token(self, token: str) -> Optional[Dict]:
        """Verify user token with user service (async)"""
        print(f"Verifying token with user service at: {self.base_url}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"http://user-service:8000/auth/verify",
                    json={"token": token}
                )
                print(f"User service response status: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    print(f"Token verification result: {result}")
                    if result.get("valid"):
                        return result.get("user")
                print(f"Token verification failed: {response.text}")
                return None
            except httpx.RequestError as e:
                print(f"Error verifying token with user service: {str(e)}")
                return None

    
    async def get_user_profile(self, user_id: str) -> Optional[Dict]:  #  async
        """Get user profile including Google tokens from user service"""
        print(f"Getting user profile for user_id: {user_id}")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(f"http://user-service:8000/auth/user/{user_id}")
                
                print(f"User profile response status: {response.status_code}")
                
                if response.status_code == 200:
                    profile = response.json()
                    print(f"User profile retrieved, has google_token: {'google_token' in profile}")
                    return profile
                    
                print(f"Failed to get user profile: {response.text}")
                return None
                
            except httpx.RequestError as e:
                print(f"Error getting user profile from user service: {str(e)}")
                return None
    
    def health_check(self) -> bool:  # NOT async
        """Check if user service is healthy"""
        with httpx.Client(timeout=5.0) as client:
            try:
                response = client.get(f"http://user-service:8000/health")
                return response.status_code == 200
            except httpx.RequestError:
                return False

# Global instance
user_service_client = UserServiceClient()






