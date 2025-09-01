from django.core.management.base import BaseCommand
from email_service.models import EmailTemplate


class Command(BaseCommand):
    help = 'Populate initial email templates'
    
    def handle(self, *args, **options):
        templates = [
            {
                'name': 'Query Response Template',
                'template_type': 'query_response',
                'subject': 'Re: {{ query.subject }}',
                'html_content': '''
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2c3e50;">Thank you for contacting Eddits</h2>
                        
                        <p>Dear {{ customer_name }},</p>
                        
                        <p>Thank you for reaching out to us regarding: <strong>{{ query.subject }}</strong></p>
                        
                        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0;">
                            <p><strong>Your Query:</strong></p>
                            <p>{{ query.message }}</p>
                        </div>
                        
                        <div style="background-color: #e8f5e8; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0;">
                            <p><strong>Our Response:</strong></p>
                            <p>{{ response_message }}</p>
                        </div>
                        
                        <p>If you have any further questions, please don't hesitate to contact us.</p>
                        
                        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                            <p>Best regards,<br>
                            <strong>The Eddits Team</strong></p>
                            
                            <p style="font-size: 12px; color: #666;">
                                This email was sent in response to your inquiry. If you did not submit this query, please contact us immediately.
                            </p>
                        </div>
                    </div>
                </body>
                </html>
                ''',
                'text_content': '''
                Thank you for contacting Eddits
                
                Dear {{ customer_name }},
                
                Thank you for reaching out to us regarding: {{ query.subject }}
                
                Your Query:
                {{ query.message }}
                
                Our Response:
                {{ response_message }}
                
                If you have any further questions, please don't hesitate to contact us.
                
                Best regards,
                The Eddits Team
                ''',
                'is_active': True
            },
            {
                'name': 'Appointment Confirmation Template',
                'template_type': 'appointment_confirmation',
                'subject': 'Appointment Confirmed - {{ appointment.appointment_type }}',
                'html_content': '''
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #28a745;">Appointment Confirmed!</h2>
                        
                        <p>Dear {{ customer_name }},</p>
                        
                        <p>Your appointment has been confirmed. Here are the details:</p>
                        
                        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; width: 30%;">Type:</td>
                                    <td style="padding: 8px 0;">{{ appointment.appointment_type }}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold;">Date:</td>
                                    <td style="padding: 8px 0;">{{ appointment_date }}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold;">Time:</td>
                                    <td style="padding: 8px 0;">{{ appointment_time }}</td>
                                </tr>
                                {% if appointment.location %}
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold;">Location:</td>
                                    <td style="padding: 8px 0;">{{ appointment.location }}</td>
                                </tr>
                                {% endif %}
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold;">Duration:</td>
                                    <td style="padding: 8px 0;">{{ appointment.duration_minutes }} minutes</td>
                                </tr>
                            </table>
                        </div>
                        
                        {% if appointment.notes %}
                        <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                            <p><strong>Additional Notes:</strong></p>
                            <p>{{ appointment.notes }}</p>
                        </div>
                        {% endif %}
                        
                        <p>Please arrive 10 minutes early for your appointment. If you need to reschedule or cancel, please contact us at least 24 hours in advance.</p>
                        
                        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                            <p>Looking forward to seeing you!<br>
                            <strong>The Eddits Team</strong></p>
                        </div>
                    </div>
                </body>
                </html>
                ''',
                'text_content': '''
                Appointment Confirmed!
                
                Dear {{ customer_name }},
                
                Your appointment has been confirmed. Here are the details:
                
                Type: {{ appointment.appointment_type }}
                Date: {{ appointment_date }}
                Time: {{ appointment_time }}
                {% if appointment.location %}Location: {{ appointment.location }}{% endif %}
                Duration: {{ appointment.duration_minutes }} minutes
                
                {% if appointment.notes %}
                Additional Notes:
                {{ appointment.notes }}
                {% endif %}
                
                Please arrive 10 minutes early for your appointment. If you need to reschedule or cancel, please contact us at least 24 hours in advance.
                
                Looking forward to seeing you!
                The Eddits Team
                ''',
                'is_active': True
            },
            {
                'name': 'Appointment Reminder Template',
                'template_type': 'appointment_reminder',
                'subject': 'Reminder: Your appointment tomorrow - {{ appointment.appointment_type }}',
                'html_content': '''
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #007bff;">Appointment Reminder</h2>
                        
                        <p>Dear {{ customer_name }},</p>
                        
                        <p>This is a friendly reminder about your upcoming appointment:</p>
                        
                        <div style="background-color: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #007bff;">
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; width: 30%;">Type:</td>
                                    <td style="padding: 8px 0;">{{ appointment.appointment_type }}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold;">Date:</td>
                                    <td style="padding: 8px 0;">{{ appointment_date }}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold;">Time:</td>
                                    <td style="padding: 8px 0;">{{ appointment_time }}</td>
                                </tr>
                                {% if appointment.location %}
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold;">Location:</td>
                                    <td style="padding: 8px 0;">{{ appointment.location }}</td>
                                </tr>
                                {% endif %}
                            </table>
                        </div>
                        
                        <p>Please remember to arrive 10 minutes early. If you need to reschedule or cancel, please contact us as soon as possible.</p>
                        
                        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                            <p>See you soon!<br>
                            <strong>The Eddits Team</strong></p>
                        </div>
                    </div>
                </body>
                </html>
                ''',
                'text_content': '''
                Appointment Reminder
                
                Dear {{ customer_name }},
                
                This is a friendly reminder about your upcoming appointment:
                
                Type: {{ appointment.appointment_type }}
                Date: {{ appointment_date }}
                Time: {{ appointment_time }}
                {% if appointment.location %}Location: {{ appointment.location }}{% endif %}
                
                Please remember to arrive 10 minutes early. If you need to reschedule or cancel, please contact us as soon as possible.
                
                See you soon!
                The Eddits Team
                ''',
                'is_active': True
            },
            {
                'name': 'Welcome Email Template',
                'template_type': 'welcome',
                'subject': 'Welcome to Eddits - Your Photography Journey Begins!',
                'html_content': '''
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <div style="text-align: center; margin-bottom: 30px;">
                            <h1 style="color: #2c3e50; margin-bottom: 10px;">Welcome to Eddits!</h1>
                            <p style="font-size: 18px; color: #7f8c8d;">Your Photography Journey Begins Here</p>
                        </div>
                        
                        <p>Dear {{ customer_name }},</p>
                        
                        <p>Welcome to Eddits! We're thrilled to have you join our community of photography enthusiasts and professionals.</p>
                        
                        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h3 style="color: #2c3e50; margin-top: 0;">What you can expect from us:</h3>
                            <ul style="padding-left: 20px;">
                                <li>Professional photography services for all occasions</li>
                                <li>High-quality photo and video editing</li>
                                <li>Personalized consultation and planning</li>
                                <li>Secure online galleries for your memories</li>
                                <li>Expert guidance throughout your photography journey</li>
                            </ul>
                        </div>
                        
                        <div style="background-color: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h3 style="color: #27ae60; margin-top: 0;">Ready to get started?</h3>
                            <p>Browse our services, book a consultation, or reach out with any questions. We're here to help capture your most precious moments!</p>
                        </div>
                        
                        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center;">
                            <p>Thank you for choosing Eddits!<br>
                            <strong>The Eddits Team</strong></p>
                            
                            <p style="font-size: 12px; color: #666; margin-top: 20px;">
                                Follow us on social media for photography tips, behind-the-scenes content, and client showcases!
                            </p>
                        </div>
                    </div>
                </body>
                </html>
                ''',
                'text_content': '''
                Welcome to Eddits!
                Your Photography Journey Begins Here
                
                Dear {{ customer_name }},
                
                Welcome to Eddits! We're thrilled to have you join our community of photography enthusiasts and professionals.
                
                What you can expect from us:
                - Professional photography services for all occasions
                - High-quality photo and video editing
                - Personalized consultation and planning
                - Secure online galleries for your memories
                - Expert guidance throughout your photography journey
                
                Ready to get started?
                Browse our services, book a consultation, or reach out with any questions. We're here to help capture your most precious moments!
                
                Thank you for choosing Eddits!
                The Eddits Team
                
                Follow us on social media for photography tips, behind-the-scenes content, and client showcases!
                ''',
                'is_active': True
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for template_data in templates:
            template, created = EmailTemplate.objects.get_or_create(
                template_type=template_data['template_type'],
                defaults=template_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created template: {template.name}')
                )
            else:
                # Update existing template if needed
                for key, value in template_data.items():
                    if key != 'template_type':
                        setattr(template, key, value)
                template.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated template: {template.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nEmail templates setup complete!\n'
                f'Created: {created_count} templates\n'
                f'Updated: {updated_count} templates'
            )
        )