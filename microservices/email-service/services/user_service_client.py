import httpx
from typing import Optional, Dict
from config import settings

class UserServiceClient:
    """Client for communicating with the user service"""
    
    def __init__(self):
        self.base_url = settings.USER_SERVICE_URL
        self.timeout = 10.0
    
    async def verify_token(self, token: str) -> Optional[Dict]:
        """Verify user token with user service"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/auth/verify",
                    json={"token": token}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("valid"):
                        return result.get("user")
                return None
            except httpx.RequestError as e:
                print(f"Error verifying token with user service: {str(e)}")
                return None
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile including Google tokens from user service"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/auth/user/{user_id}"
                )
                
                if response.status_code == 200:
                    return response.json()
                return None
            except httpx.RequestError as e:
                print(f"Error getting user profile from user service: {str(e)}")
                return None
    
    async def health_check(self) -> bool:
        """Check if user service is healthy"""
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
            except httpx.RequestError:
                return False

# Global instance
user_service_client = UserServiceClient()