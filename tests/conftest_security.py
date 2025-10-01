"""Security testing configuration and fixtures."""

import pytest
import tempfile
import os
import hashlib
import secrets
from unittest.mock import Mock, patch

from explainstack.auth import AuthService, AuthMiddleware
from explainstack.database import DatabaseManager
from explainstack.user import UserService, UserPreferencesManager
from explainstack.utils import FileHandler
from explainstack.analytics import AnalyticsManager


@pytest.fixture
def secure_database():
    """Secure database fixture for security testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        db_manager = DatabaseManager(db_path)
        yield db_manager
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


@pytest.fixture
def secure_auth_service(secure_database):
    """Secure authentication service fixture."""
    return AuthService(secure_database)


@pytest.fixture
def secure_auth_middleware(secure_auth_service):
    """Secure authentication middleware fixture."""
    return AuthMiddleware(secure_auth_service)


@pytest.fixture
def secure_user_service(secure_database):
    """Secure user service fixture."""
    return UserService(secure_database)


@pytest.fixture
def secure_preferences_manager(secure_database):
    """Secure preferences manager fixture."""
    return UserPreferencesManager(secure_database)


@pytest.fixture
def secure_file_handler():
    """Secure file handler fixture."""
    return FileHandler()


@pytest.fixture
def secure_analytics_manager():
    """Secure analytics manager fixture."""
    return AnalyticsManager()


@pytest.fixture
def test_user(secure_auth_service):
    """Test user fixture."""
    user_id = secure_auth_service.register_user("test@example.com", "password123")
    return {
        'id': user_id,
        'email': "test@example.com",
        'password': "password123"
    }


@pytest.fixture
def test_session(secure_auth_service, test_user):
    """Test session fixture."""
    session_id = secure_auth_service.login_user(test_user['email'], test_user['password'])
    return {
        'id': session_id,
        'user_id': test_user['id']
    }


@pytest.fixture
def malicious_inputs():
    """Malicious input fixtures for security testing."""
    return {
        'sql_injection': [
            "'; DROP TABLE users; --",
            "admin' OR '1'='1",
            "test@example.com'; DELETE FROM users; --",
            "'; INSERT INTO users (email, password) VALUES ('hacker@evil.com', 'password'); --"
        ],
        'xss_attempts': [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//"
        ],
        'path_traversal': [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/passwd",
            "C:\\Windows\\System32\\config\\SAM"
        ],
        'command_injection': [
            "test; rm -rf /",
            "test | cat /etc/passwd",
            "test && whoami",
            "test || id"
        ],
        'ldap_injection': [
            "*)(uid=*))(|(uid=*",
            "admin)(&(password=*))",
            "*)(|(password=*))",
            "admin)(|(objectClass=*))"
        ]
    }


@pytest.fixture
def security_test_data():
    """Security test data fixture."""
    return {
        'valid_emails': [
            "test@example.com",
            "user.name@domain.co.uk",
            "test+tag@example.org"
        ],
        'invalid_emails': [
            "invalid-email",
            "@example.com",
            "test@",
            "test..test@example.com"
        ],
        'valid_passwords': [
            "Password123!",
            "MySecureP@ssw0rd",
            "ComplexP@ssw0rd123"
        ],
        'weak_passwords': [
            "123456",
            "password",
            "qwerty",
            "abc123"
        ],
        'strong_passwords': [
            "MyV3ryS3cur3P@ssw0rd!",
            "C0mpl3xP@ssw0rd123!@#",
            "Str0ngP@ssw0rdW1thSp3c1alChars!"
        ]
    }


@pytest.fixture
def security_headers():
    """Security headers fixture."""
    return {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'",
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }


@pytest.fixture
def security_cookies():
    """Security cookies fixture."""
    return {
        'session_id': secrets.token_urlsafe(32),
        'csrf_token': secrets.token_urlsafe(32),
        'remember_token': secrets.token_urlsafe(32)
    }


@pytest.fixture
def security_encryption():
    """Security encryption fixture."""
    class SecurityEncryption:
        def __init__(self):
            self.key = secrets.token_bytes(32)
        
        def encrypt(self, data):
            """Encrypt data."""
            # This would implement actual encryption
            return hashlib.sha256(data.encode()).hexdigest()
        
        def decrypt(self, encrypted_data):
            """Decrypt data."""
            # This would implement actual decryption
            return encrypted_data
        
        def hash_password(self, password):
            """Hash password."""
            salt = secrets.token_bytes(32)
            return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        
        def verify_password(self, password, hashed):
            """Verify password."""
            # This would implement actual password verification
            return True
    
    return SecurityEncryption()


@pytest.fixture
def security_audit_logger():
    """Security audit logger fixture."""
    class SecurityAuditLogger:
        def __init__(self):
            self.events = []
        
        def log_event(self, event_type, user_id, details):
            """Log security event."""
            event = {
                'timestamp': time.time(),
                'event_type': event_type,
                'user_id': user_id,
                'details': details
            }
            self.events.append(event)
            return event
        
        def get_events(self, event_type=None):
            """Get security events."""
            if event_type:
                return [e for e in self.events if e['event_type'] == event_type]
            return self.events
        
        def get_events_by_user(self, user_id):
            """Get events by user."""
            return [e for e in self.events if e['user_id'] == user_id]
    
    return SecurityAuditLogger()


@pytest.fixture
def security_rate_limiter():
    """Security rate limiter fixture."""
    class SecurityRateLimiter:
        def __init__(self):
            self.attempts = {}
        
        def check_rate_limit(self, identifier, max_attempts=5, window=300):
            """Check rate limit."""
            current_time = time.time()
            
            if identifier not in self.attempts:
                self.attempts[identifier] = []
            
            # Remove old attempts
            self.attempts[identifier] = [
                attempt for attempt in self.attempts[identifier]
                if current_time - attempt < window
            ]
            
            # Check if rate limit exceeded
            if len(self.attempts[identifier]) >= max_attempts:
                return False
            
            # Record attempt
            self.attempts[identifier].append(current_time)
            return True
        
        def reset_rate_limit(self, identifier):
            """Reset rate limit for identifier."""
            if identifier in self.attempts:
                del self.attempts[identifier]
    
    return SecurityRateLimiter()


@pytest.fixture
def security_input_sanitizer():
    """Security input sanitizer fixture."""
    class SecurityInputSanitizer:
        def __init__(self):
            self.dangerous_patterns = [
                r'<script.*?>.*?</script>',
                r'javascript:',
                r'on\w+\s*=',
                r'<iframe.*?>.*?</iframe>',
                r'<object.*?>.*?</object>',
                r'<embed.*?>.*?</embed>'
            ]
        
        def sanitize(self, input_text):
            """Sanitize input text."""
            import re
            
            sanitized = input_text
            
            for pattern in self.dangerous_patterns:
                sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
            
            return sanitized
        
        def validate_email(self, email):
            """Validate email address."""
            import re
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(pattern, email) is not None
        
        def validate_password(self, password):
            """Validate password strength."""
            if len(password) < 8:
                return False, "Password must be at least 8 characters long"
            
            if not re.search(r'[A-Z]', password):
                return False, "Password must contain at least one uppercase letter"
            
            if not re.search(r'[a-z]', password):
                return False, "Password must contain at least one lowercase letter"
            
            if not re.search(r'\d', password):
                return False, "Password must contain at least one digit"
            
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                return False, "Password must contain at least one special character"
            
            return True, "Password is valid"
    
    return SecurityInputSanitizer()


@pytest.fixture
def security_session_manager():
    """Security session manager fixture."""
    class SecuritySessionManager:
        def __init__(self):
            self.sessions = {}
            self.session_timeout = 3600  # 1 hour
        
        def create_session(self, user_id):
            """Create secure session."""
            session_id = secrets.token_urlsafe(32)
            session_data = {
                'user_id': user_id,
                'created_at': time.time(),
                'last_activity': time.time(),
                'ip_address': '127.0.0.1',
                'user_agent': 'test-agent'
            }
            self.sessions[session_id] = session_data
            return session_id
        
        def validate_session(self, session_id):
            """Validate session."""
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            current_time = time.time()
            
            # Check if session expired
            if current_time - session['last_activity'] > self.session_timeout:
                del self.sessions[session_id]
                return False
            
            # Update last activity
            session['last_activity'] = current_time
            return True
        
        def destroy_session(self, session_id):
            """Destroy session."""
            if session_id in self.sessions:
                del self.sessions[session_id]
        
        def get_session(self, session_id):
            """Get session data."""
            return self.sessions.get(session_id)
    
    return SecuritySessionManager()


@pytest.fixture
def security_file_validator():
    """Security file validator fixture."""
    class SecurityFileValidator:
        def __init__(self):
            self.allowed_extensions = ['.py', '.txt', '.md', '.diff', '.patch']
            self.max_file_size = 10 * 1024 * 1024  # 10MB
            self.dangerous_patterns = [
                b'<script',
                b'javascript:',
                b'<iframe',
                b'<object',
                b'<embed'
            ]
        
        def validate_file(self, filename, content):
            """Validate file for security."""
            # Check file extension
            if not any(filename.endswith(ext) for ext in self.allowed_extensions):
                return False, "File type not allowed"
            
            # Check file size
            if len(content) > self.max_file_size:
                return False, "File too large"
            
            # Check for dangerous content
            for pattern in self.dangerous_patterns:
                if pattern in content.lower():
                    return False, "File contains potentially dangerous content"
            
            return True, "File is valid"
        
        def scan_content(self, content):
            """Scan content for security issues."""
            issues = []
            
            for pattern in self.dangerous_patterns:
                if pattern in content.lower():
                    issues.append(f"Potentially dangerous content detected: {pattern}")
            
            return issues
    
    return SecurityFileValidator()
