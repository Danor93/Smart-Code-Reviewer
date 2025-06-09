# OWASP Top 10 Security Guidelines for Code Review

## A01: Broken Access Control

### Common Issues

- Bypassing access control checks by modifying the URL
- Allowing primary key to be changed to another user's record
- Elevation of privilege (acting as an admin when logged in as a user)
- Metadata manipulation (JWT token replay, hidden fields tampering)

### Code Review Checklist

- Verify proper authorization checks before accessing resources
- Ensure user permissions are validated at the server side
- Check for proper session management
- Review JWT token validation and expiration

### Example Vulnerable Code

```python
# BAD: No authorization check
@app.route('/user/<user_id>/profile')
def get_profile(user_id):
    return User.query.get(user_id).to_dict()

# GOOD: Proper authorization
@app.route('/user/<user_id>/profile')
@login_required
def get_profile(user_id):
    if current_user.id != user_id and not current_user.is_admin:
        abort(403)
    return User.query.get(user_id).to_dict()
```

## A02: Cryptographic Failures

### Common Issues

- Hardcoded secrets and passwords
- Weak encryption algorithms
- Improper key management
- Transmitting data in clear text

### Code Review Checklist

- Check for hardcoded passwords or API keys
- Verify strong encryption algorithms are used (AES-256, RSA-2048+)
- Ensure proper random number generation
- Review SSL/TLS configuration

### Example Vulnerable Code

```python
# BAD: Hardcoded secret
SECRET_KEY = "mysecretkey123"
password = "admin123"  # Hardcoded password

# GOOD: Environment variables
SECRET_KEY = os.environ.get('SECRET_KEY')
password_hash = bcrypt.generate_password_hash(password)
```

## A03: Injection

### Common Issues

- SQL injection through unsanitized input
- NoSQL injection
- OS command injection
- LDAP injection

### Code Review Checklist

- Use parameterized queries or prepared statements
- Validate and sanitize all input
- Use allowlists for input validation
- Avoid dynamic query construction

### Example Vulnerable Code

```python
# BAD: SQL injection vulnerability
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)

# GOOD: Parameterized query
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

## A04: Insecure Design

### Common Issues

- Missing or ineffective control design
- Lack of threat modeling
- Insecure design patterns

### Code Review Checklist

- Review architecture and design patterns
- Check for proper separation of concerns
- Verify defense in depth implementation
- Ensure secure defaults

## A05: Security Misconfiguration

### Common Issues

- Default configurations and passwords
- Unnecessary features enabled
- Missing security headers
- Verbose error messages revealing system information

### Code Review Checklist

- Review configuration files for security settings
- Check for disabled security features
- Verify error handling doesn't leak sensitive information
- Ensure proper HTTP security headers

### Example Vulnerable Code

```python
# BAD: Debug mode in production
app.debug = True

# BAD: Verbose error messages
except Exception as e:
    return f"Database error: {str(e)}", 500

# GOOD: Generic error messages
except Exception as e:
    logger.error(f"Database error: {str(e)}")
    return "An error occurred", 500
```

## A06: Vulnerable and Outdated Components

### Code Review Checklist

- Review dependencies for known vulnerabilities
- Check for outdated libraries and frameworks
- Verify component authenticity
- Monitor security advisories

### Example Check

```python
# Check requirements.txt for outdated packages
# Use tools like safety, bandit, or dependabot
```

## A07: Identification and Authentication Failures

### Common Issues

- Weak password requirements
- Broken session management
- Missing multi-factor authentication

### Code Review Checklist

- Verify strong password policies
- Check session timeout and invalidation
- Review authentication mechanisms
- Ensure proper logout functionality

### Example Vulnerable Code

```python
# BAD: Weak session management
session['user_id'] = user.id
# No expiration, no secure flags

# GOOD: Secure session management
session.permanent = True
app.permanent_session_lifetime = timedelta(hours=1)
session['user_id'] = user.id
```

## A08: Software and Data Integrity Failures

### Code Review Checklist

- Verify digital signatures and checksums
- Review CI/CD pipeline security
- Check for auto-update mechanisms
- Validate serialized data

## A09: Security Logging and Monitoring Failures

### Code Review Checklist

- Verify security events are logged
- Check log protection and integrity
- Review alerting mechanisms
- Ensure compliance with regulations

### Example Implementation

```python
import logging

# Configure security logging
security_logger = logging.getLogger('security')
security_logger.info(f"Failed login attempt for user: {username} from IP: {request.remote_addr}")
```

## A10: Server-Side Request Forgery (SSRF)

### Common Issues

- Fetching remote resources without validation
- Bypassing firewalls and VPNs
- Internal service enumeration

### Code Review Checklist

- Validate and sanitize URLs
- Use allowlists for allowed domains
- Implement network segmentation
- Disable unnecessary URL schemas

### Example Vulnerable Code

```python
# BAD: SSRF vulnerability
url = request.args.get('url')
response = requests.get(url)

# GOOD: URL validation
allowed_domains = ['api.trusted-site.com']
parsed_url = urlparse(url)
if parsed_url.netloc in allowed_domains:
    response = requests.get(url)
```
