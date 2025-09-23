from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, NumberRange, Length, Regexp
import re

class ServiceForm(FlaskForm):
    name = StringField('Service Name', validators=[
        DataRequired(), 
        Length(min=1, max=100)
    ])
    
    host = StringField('Host (IP or DNS)', validators=[
        DataRequired(),
        Length(min=1, max=255)
    ])
    
    port = IntegerField('Port', validators=[
        DataRequired(),
        NumberRange(min=1, max=65535)
    ])
    
    description = TextAreaField('Description', validators=[
        Length(max=500)
    ])
    
    admin_email = StringField('Admin Email', validators=[
        DataRequired(),
        Email()
    ])
    
    check_interval = IntegerField('Check Interval (seconds)', validators=[
        DataRequired(),
        NumberRange(min=30, max=86400)  # 30 seconds to 24 hours
    ], default=300)
    
    check_type = SelectField('Check Type', choices=[
        ('tcp', 'TCP Port Check'),
        ('http', 'HTTP Check'),
        ('https', 'HTTPS Check')
    ], default='tcp', validators=[DataRequired()])
    
    def validate_host(self, field):
        """Validate that host is either a valid IP address or hostname."""
        host = field.data.strip()
        
        # Check if it's a valid IPv4 address
        ipv4_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        
        # Check if it's a valid hostname/FQDN
        hostname_pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
        
        if not (re.match(ipv4_pattern, host) or re.match(hostname_pattern, host)):
            raise ValueError('Please enter a valid IP address or hostname')