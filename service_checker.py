from abc import ABC, abstractmethod
import socket
import time
import requests
from typing import Dict, Any, Tuple
from models import ServiceStatus

class ServiceChecker(ABC):
    """Abstract base class for service checking strategies."""
    
    def __init__(self, host: str, port: int, timeout: int = 10):
        self.host = host
        self.port = port
        self.timeout = timeout
    
    @abstractmethod
    def check(self) -> Tuple[ServiceStatus, float, str]:
        """
        Check the service and return status, response time, and error message.
        
        Returns:
            Tuple[ServiceStatus, float, str]: (status, response_time_seconds, error_message)
        """
        pass

class TCPChecker(ServiceChecker):
    """TCP port connectivity checker."""
    
    def check(self) -> Tuple[ServiceStatus, float, str]:
        start_time = time.time()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            response_time = time.time() - start_time
            
            if result == 0:
                return ServiceStatus.UP, response_time, ""
            else:
                return ServiceStatus.DOWN, response_time, f"Connection refused to {self.host}:{self.port}"
        except socket.timeout:
            response_time = time.time() - start_time
            return ServiceStatus.DOWN, response_time, f"Timeout connecting to {self.host}:{self.port}"
        except Exception as e:
            response_time = time.time() - start_time
            return ServiceStatus.DOWN, response_time, f"Error connecting to {self.host}:{self.port}: {str(e)}"

class HTTPChecker(ServiceChecker):
    """HTTP/HTTPS service checker."""
    
    def __init__(self, host: str, port: int, timeout: int = 10, use_ssl: bool = False, path: str = "/"):
        super().__init__(host, port, timeout)
        self.use_ssl = use_ssl
        self.path = path
    
    def check(self) -> Tuple[ServiceStatus, float, str]:
        protocol = "https" if self.use_ssl else "http"
        url = f"{protocol}://{self.host}:{self.port}{self.path}"
        
        start_time = time.time()
        try:
            response = requests.get(url, timeout=self.timeout, verify=False)
            response_time = time.time() - start_time
            
            if 200 <= response.status_code < 400:
                return ServiceStatus.UP, response_time, ""
            else:
                return ServiceStatus.DOWN, response_time, f"HTTP {response.status_code}: {response.reason}"
        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            return ServiceStatus.DOWN, response_time, f"HTTP timeout for {url}"
        except requests.exceptions.ConnectionError:
            response_time = time.time() - start_time
            return ServiceStatus.DOWN, response_time, f"HTTP connection error for {url}"
        except Exception as e:
            response_time = time.time() - start_time
            return ServiceStatus.DOWN, response_time, f"HTTP error for {url}: {str(e)}"

class ServiceCheckerFactory:
    """Factory class to create appropriate service checkers."""
    
    @staticmethod
    def create_checker(check_type: str, host: str, port: int, timeout: int = 10, **kwargs) -> ServiceChecker:
        """
        Create a service checker based on the check type.
        
        Args:
            check_type: Type of check ('tcp', 'http', 'https')
            host: Host to check
            port: Port to check
            timeout: Timeout in seconds
            **kwargs: Additional arguments for specific checkers
            
        Returns:
            ServiceChecker: Appropriate checker instance
        """
        if check_type.lower() == 'tcp':
            return TCPChecker(host, port, timeout)
        elif check_type.lower() == 'http':
            return HTTPChecker(host, port, timeout, use_ssl=False, path=kwargs.get('path', '/'))
        elif check_type.lower() == 'https':
            return HTTPChecker(host, port, timeout, use_ssl=True, path=kwargs.get('path', '/'))
        else:
            raise ValueError(f"Unsupported check type: {check_type}")