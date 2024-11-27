from django.core.exceptions import ValidationError

USERNAME_BLACKLIST = [
    '',
    'admin', 
    'admin_geospatialib',
    'geospatialib', 
    'user', 
    'username', 
    'name', 
    'test', 
    'random_username', 
]

def validate_username(username):
    username = username.lower()

    if len(username) < 3:
        raise ValidationError('Username must be at least 3 characters.')
    
    if username in USERNAME_BLACKLIST:
        raise ValidationError('Username is not allowed.')