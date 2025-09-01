# Email Integration System - Eddits

This guide covers the comprehensive email integration system implemented for the Eddits application, including customer queries, appointment management, and automated email communications.

## Overview

The email integration system provides:
- Customer query management with automated responses
- Appointment booking and confirmation system
- Email template management with dynamic content
- Comprehensive email logging and analytics
- Admin interface for managing all email operations

## Features

### 1. Customer Query Management
- **Public API**: Customers can submit queries without authentication
- **Admin Management**: Staff can view, assign, and respond to queries
- **Automated Responses**: Email notifications sent when queries are responded to
- **Status Tracking**: Pending → In Progress → Resolved workflow
- **Priority Levels**: Low, Medium, High priority classification

### 2. Appointment System
- **Booking Requests**: Customers can request appointments
- **Confirmation Workflow**: Admin can confirm appointments with automatic email notifications
- **Reminder System**: Automated reminder emails for upcoming appointments
- **Multiple Types**: Consultation, Photo Shoot, Video Production, Event Coverage, etc.
- **Status Management**: Pending → Confirmed → Completed/Cancelled workflow

### 3. Email Templates
- **Dynamic Templates**: HTML and text versions with variable substitution
- **Template Types**: Query responses, appointment confirmations, reminders, welcome emails
- **Admin Customization**: Full template editing through admin interface
- **Preview & Testing**: Test email functionality with sample data

### 4. Email Logging & Analytics
- **Complete Audit Trail**: All sent emails are logged with status tracking
- **Delivery Status**: Sent, Failed, Pending status monitoring
- **Statistics Dashboard**: Email performance metrics and analytics
- **Error Tracking**: Failed email logging with error messages

## API Endpoints

### Customer Queries
```
GET    /api/email/api/queries/           # List queries (authenticated)
POST   /api/email/api/queries/           # Create query (public)
GET    /api/email/api/queries/{id}/      # Get specific query
PUT    /api/email/api/queries/{id}/      # Update query
DELETE /api/email/api/queries/{id}/      # Delete query
POST   /api/email/api/queries/{id}/respond/  # Respond to query
```

### Appointments
```
GET    /api/email/api/appointments/      # List appointments
POST   /api/email/api/appointments/      # Create appointment (public)
GET    /api/email/api/appointments/{id}/ # Get specific appointment
PUT    /api/email/api/appointments/{id}/ # Update appointment
POST   /api/email/api/appointments/{id}/confirm/  # Confirm appointment
```

### Email Templates
```
GET    /api/email/api/templates/         # List templates
POST   /api/email/api/templates/         # Create template
GET    /api/email/api/templates/{id}/    # Get specific template
PUT    /api/email/api/templates/{id}/    # Update template
POST   /api/email/api/templates/{id}/test/  # Test template
```

### Statistics & Analytics
```
GET    /api/email/api/stats/emails/      # Email statistics
GET    /api/email/api/stats/queries/     # Query statistics
GET    /api/email/api/stats/appointments/  # Appointment statistics
```

### Custom Email Operations
```
POST   /api/email/api/send-custom-email/     # Send custom email
POST   /api/email/api/send-welcome-email/    # Send welcome email
POST   /api/email/api/bulk-assign/           # Bulk assign queries
POST   /api/email/api/bulk-confirm/          # Bulk confirm appointments
POST   /api/email/api/send-reminders/        # Send appointment reminders
```

## Email Configuration

The system uses Django's email configuration from `settings.py`:

```python
# Email Configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@eddits.com')
```

### Environment Variables
Add these to your `.env` file:
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@eddits.com
```

## Usage Examples

### 1. Customer Submitting a Query
```javascript
// Frontend code to submit a query
const submitQuery = async (queryData) => {
  const response = await fetch('/api/email/api/queries/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: 'John Doe',
      email: 'john@example.com',
      phone: '+1234567890',
      subject: 'Wedding Photography Inquiry',
      message: 'I would like to inquire about wedding photography packages...',
      priority: 'medium'
    })
  });
  return response.json();
};
```

### 2. Admin Responding to Query
```javascript
// Admin responding to a query
const respondToQuery = async (queryId, responseMessage) => {
  const response = await fetch(`/api/email/api/queries/${queryId}/respond/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + authToken
    },
    body: JSON.stringify({
      message: responseMessage,
      is_internal: false  // Set to true for internal notes
    })
  });
  return response.json();
};
```

### 3. Booking an Appointment
```javascript
// Customer booking an appointment
const bookAppointment = async (appointmentData) => {
  const response = await fetch('/api/email/api/appointments/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: 'Jane Smith',
      email: 'jane@example.com',
      phone: '+1234567890',
      appointment_type: 'consultation',
      preferred_date: '2024-02-15',
      preferred_time: '14:00:00',
      duration_minutes: 60,
      message: 'I would like to discuss my upcoming event photography needs.'
    })
  });
  return response.json();
};
```

### 4. Confirming an Appointment
```javascript
// Admin confirming an appointment
const confirmAppointment = async (appointmentId, confirmationData) => {
  const response = await fetch(`/api/email/api/appointments/${appointmentId}/confirm/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + authToken
    },
    body: JSON.stringify({
      confirmed_date: '2024-02-15',
      confirmed_time: '14:00:00',
      location: 'Eddits Studio, 123 Main St',
      notes: 'Please bring any reference materials or inspiration photos.'
    })
  });
  return response.json();
};
```

## Admin Interface

The admin interface provides comprehensive management tools:

### Customer Queries
- View all queries with filtering and search
- Assign queries to team members
- Respond to queries with automatic email notifications
- Track query status and resolution
- Bulk operations for query management

### Appointments
- Manage appointment requests
- Confirm appointments with automatic email notifications
- Send reminder emails
- Track appointment status
- Bulk confirmation and reminder operations

### Email Templates
- Create and edit email templates
- Preview templates with sample data
- Test email sending functionality
- Manage template activation status

### Email Logs
- View all sent emails
- Monitor delivery status
- Track email performance
- Debug failed email deliveries

## Template Variables

Email templates support the following variables:

### Query Response Templates
- `{{ customer_name }}` - Customer's name
- `{{ query.subject }}` - Query subject
- `{{ query.message }}` - Original query message
- `{{ response_message }}` - Admin's response

### Appointment Templates
- `{{ customer_name }}` - Customer's name
- `{{ appointment.appointment_type }}` - Type of appointment
- `{{ appointment_date }}` - Formatted appointment date
- `{{ appointment_time }}` - Formatted appointment time
- `{{ appointment.location }}` - Appointment location
- `{{ appointment.duration_minutes }}` - Duration in minutes
- `{{ appointment.notes }}` - Additional notes

### Welcome Email Templates
- `{{ customer_name }}` - Customer's name

## Security Features

- **Authentication Required**: Most endpoints require authentication except public submission endpoints
- **Permission Checks**: Role-based access control for admin operations
- **Input Validation**: Comprehensive validation for all email inputs
- **Email Sanitization**: HTML content is sanitized to prevent XSS attacks
- **Rate Limiting**: Consider implementing rate limiting for public endpoints

## Monitoring & Maintenance

### Email Delivery Monitoring
- Check email logs regularly for failed deliveries
- Monitor email service provider limits and quotas
- Set up alerts for high failure rates

### Template Management
- Regularly review and update email templates
- Test templates after modifications
- Maintain backup copies of working templates

### Database Maintenance
- Archive old email logs periodically
- Clean up resolved queries and completed appointments
- Monitor database growth and performance

## Troubleshooting

### Common Issues

1. **Emails Not Sending**
   - Check email configuration in settings
   - Verify SMTP credentials
   - Check email service provider limits
   - Review email logs for error messages

2. **Template Rendering Issues**
   - Verify template syntax
   - Check variable names and context
   - Test templates with sample data

3. **Permission Errors**
   - Verify user authentication
   - Check user permissions and roles
   - Review API endpoint access controls

### Debug Commands

```bash
# Test email configuration
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])

# Check email templates
python manage.py shell
>>> from email_service.models import EmailTemplate
>>> EmailTemplate.objects.filter(is_active=True)

# View email logs
python manage.py shell
>>> from email_service.models import EmailLog
>>> EmailLog.objects.filter(status='failed')
```

## Future Enhancements

- **Email Scheduling**: Schedule emails for future delivery
- **Email Campaigns**: Bulk email campaigns for marketing
- **Advanced Analytics**: Detailed email performance metrics
- **Integration**: Integration with external email services (SendGrid, Mailgun)
- **Mobile Notifications**: Push notifications for mobile apps
- **Webhook Support**: Webhook notifications for email events

## Support

For technical support or questions about the email integration system:
1. Check the troubleshooting section above
2. Review the Django admin interface for system status
3. Check application logs for detailed error information
4. Contact the development team for advanced issues

---

*This documentation covers the complete email integration system for Eddits. Keep this guide updated as new features are added or configurations change.*