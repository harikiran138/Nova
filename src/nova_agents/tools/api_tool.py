import os
import requests
from typing import Dict, Any, Optional

class ApiTool:
    """Tool for interacting with JSON APIs."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "NovaAgent/2.1 (API Client)"
        })

    def request(self, method: str, url: str, headers: Dict[str, str] = None, data: Dict[str, Any] = None, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make an HTTP request and return JSON response.
        
        Args:
            method: GET, POST, PUT, DELETE, etc.
            url: Target URL.
            headers: Optional headers.
            data: JSON body for POST/PUT.
            params: Query parameters.
            
        Returns:
            Dict containing 'status_code', 'data' (json), or 'error'.
        """
        try:
            # Merge headers
            req_headers = self.session.headers.copy()
            if headers:
                req_headers.update(headers)
                
            # Resolve env vars in headers (e.g. "Authorization": "Bearer $MY_KEY")
            for k, v in req_headers.items():
                if isinstance(v, str) and v.startswith("$"):
                    env_var = v[1:]
                    env_val = os.environ.get(env_var)
                    if env_val:
                        req_headers[k] = env_val
                    else:
                        return {"success": False, "error": f"Environment variable {env_var} not found."}

            response = self.session.request(
                method=method,
                url=url,
                headers=req_headers,
                json=data,
                params=params,
                timeout=15
            )
            
            try:
                json_data = response.json()
            except:
                json_data = response.text[:1000] # Fallback to text if not JSON
                
            return {
                "success": response.ok,
                "status": response.status_code,
                "data": json_data
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
