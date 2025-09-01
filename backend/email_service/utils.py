from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from .models import EmailTemplate, EmailLog
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Service class for handling email operations"""
    
    @staticmethod
    def send_templated_email(template_type, recipient_email, recipient_name='', context=None, query=None, appointment=None):
        """
        Send an email using a predefined template
        
        Args:
            template_type: Type of email template to use
            recipient_email: Email address of the recipient
            recipient_name: Name of the recipient
            context: Dictionary of context variables for the template
            query: Related CustomerQuery object (optional)
            appointment: Related Appointment object (optional)
        
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Get the active template
            template = EmailTemplate.objects.filter(
                template_type=template_type,
                is_active=True
            ).first()
            
            if not template:
                logger.error(f"No active template found for type: {template_type}")
                return False
            
            # Prepare context
            if context is None:
                context = {}
            
            context.update({
                'recipient_name': recipient_name,
                'site_name': 'Eddits by Meet Dudhwala',
                'contact_email': settings.ADMIN_EMAIL,
            })
            
            # Render email content
            subject = EmailService._render_template_string(template.subject, context)
            html_content = EmailService._render_template_string(template.html_content, context)
            text_content = EmailService._render_template_string(template.text_content, context) if template.text_content else None
            
            # Create email log entry
            email_log = EmailLog.objects.create(
                recipient_email=recipient_email,
                recipient_name=recipient_name,
                subject=subject,
                email_type=template_type,
                template_used=template,
                query=query,
                appointment=appointment,
                status='pending'
            )
            
            # Send email
            success = EmailService._send_email(
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                recipient_email=recipient_email,
                recipient_name=recipient_name
            )
            
            # Update email log
            if success:
                email_log.status = 'sent'
                email_log.sent_at = timezone.now()
            else:
                email_log.status = 'failed'
                email_log.error_message = 'Failed to send email'
            
            email_log.save()
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending templated email: {str(e)}")
            return False
    
    @staticmethod
    def send_custom_email(subject, html_content, text_content, recipient_email, recipient_name=''):
        """
        Send a custom email without using templates
        
        Args:
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content of the email
            recipient_email: Email address of the recipient
            recipient_name: Name of the recipient
        
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Create email log entry
            email_log = EmailLog.objects.create(
                recipient_email=recipient_email,
                recipient_name=recipient_name,
                subject=subject,
                email_type='custom',
                status='pending'
            )
            
            # Send email
            success = EmailService._send_email(
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                recipient_email=recipient_email,
                recipient_name=recipient_name
            )
            
            # Update email log
            if success:
                email_log.status = 'sent'
                email_log.sent_at = timezone.now()
            else:
                email_log.status = 'failed'
                email_log.error_message = 'Failed to send email'
            
            email_log.save()
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending custom email: {str(e)}")
            return False
    
    @staticmethod
    def _send_email(subject, html_content, text_content, recipient_email, recipient_name=''):
        """
        Internal method to send email using Django's email backend
        
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Prepare recipient
            if recipient_name:
                to_email = f"{recipient_name} <{recipient_email}>"
            else:
                to_email = recipient_email
            
            # Create email message
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content or html_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[to_email]
            )
            
            # Add HTML content if available
            if html_content and text_content:
                msg.attach_alternative(html_content, "text/html")
            
            # Send email
            msg.send()
            
            logger.info(f"Email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {recipient_email}: {str(e)}")
            return False
    
    @staticmethod
    def _render_template_string(template_string, context):
        """
        Render a template string with context variables
        
        Args:
            template_string: Template string with placeholders
            context: Dictionary of context variables
        
        Returns:
            str: Rendered string
        """
        try:
            # Simple template variable replacement
            # For more complex templating, consider using Django's template engine
            rendered = template_string
            for key, value in context.items():
                placeholder = f"{{{{{key}}}}}"
                rendered = rendered.replace(placeholder, str(value))
            return rendered
        except Exception as e:
            logger.error(f"Error rendering template string: {str(e)}")
            return template_string
    
    @staticmethod
    def send_query_response(query, response_message):
        """
        Send response email for a customer query
        
        Args:
            query: CustomerQuery object
            response_message: Response message to send
        
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        context = {
            'query_subject': query.subject,
            'query_message': query.message,
            'response_message': response_message,
            'query_id': query.id,
        }
        
        return EmailService.send_templated_email(
            template_type='query_response',
            recipient_email=query.email,
            recipient_name=query.name,
            context=context,
            query=query
        )
    
    @staticmethod
    def send_appointment_confirmation(appointment):
        """
        Send confirmation email for an appointment
        
        Args:
            appointment: Appointment object
        
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        context = {
            'appointment_type': appointment.get_appointment_type_display(),
            'appointment_date': appointment.confirmed_date or appointment.preferred_date,
            'appointment_time': appointment.confirmed_time or appointment.preferred_time,
            'location': appointment.location,
            'duration': appointment.duration_minutes,
            'notes': appointment.notes,
            'appointment_id': appointment.id,
        }
        
        return EmailService.send_templated_email(
            template_type='appointment_confirmation',
            recipient_email=appointment.email,
            recipient_name=appointment.name,
            context=context,
            appointment=appointment
        )
    
    @staticmethod
    def send_appointment_reminder(appointment):
        """
        Send reminder email for an upcoming appointment
        
        Args:
            appointment: Appointment object
        
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        context = {
            'appointment_type': appointment.get_appointment_type_display(),
            'appointment_date': appointment.confirmed_date or appointment.preferred_date,
            'appointment_time': appointment.confirmed_time or appointment.preferred_time,
            'location': appointment.location,
            'duration': appointment.duration_minutes,
            'appointment_id': appointment.id,
        }
        
        return EmailService.send_templated_email(
            template_type='appointment_reminder',
            recipient_email=appointment.email,
            recipient_name=appointment.name,
            context=context,
            appointment=appointment
        )
    
    @staticmethod
    def send_welcome_email(user):
        """
        Send welcome email to a new user
        
        Args:
            user: User object
        
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        context = {
            'user_name': user.get_full_name() or user.email,
            'login_url': f"{settings.FRONTEND_URL}/login" if hasattr(settings, 'FRONTEND_URL') else '#',
        }
        
        return EmailService.send_templated_email(
            template_type='welcome',
            recipient_email=user.email,
            recipient_name=user.get_full_name(),
            context=context
        )