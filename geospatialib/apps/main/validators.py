from django.core.exceptions import ValidationError

USERNAME_BLACKLIST = [
    'admin', 
    'admin_geospatialib',
    'geospatialib', 
    'user', 
    'username', 
]

def validate_username(username):
    if len(username) < 3:
        raise ValidationError('Username must be at least 3 characters.')
    
    if username in USERNAME_BLACKLIST:
        raise ValidationError('Username is not allowed.')
