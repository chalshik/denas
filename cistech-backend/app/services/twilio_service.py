from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import os
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class TwilioService:
    """Service for handling SMS verification with Twilio"""
    
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.verify_service_sid = os.getenv("TWILIO_VERIFY_SERVICE_SID")
        
        if not all([self.account_sid, self.auth_token, self.verify_service_sid]):
            logger.warning("Twilio credentials not properly configured")
            self.client = None
        else:
            self.client = Client(self.account_sid, self.auth_token)
    
    async def send_verification_code(self, phone_number: str) -> Tuple[bool, str, Optional[str]]:
        """
        Send verification code to phone number
        Returns: (success, message, verification_sid)
        """
        if not self.client:
            logger.error("Twilio client not initialized")
            return False, "SMS service not available", None
        
        try:
            verification = self.client.verify.v2.services(
                self.verify_service_sid
            ).verifications.create(
                to=phone_number,
                channel='sms'
            )
            
            logger.info(f"Verification code sent to {phone_number}")
            return True, "Verification code sent successfully", verification.sid
            
        except TwilioException as e:
            logger.error(f"Twilio error sending verification: {str(e)}")
            return False, f"Failed to send verification code: {str(e)}", None
        except Exception as e:
            logger.error(f"Unexpected error sending verification: {str(e)}")
            return False, "Failed to send verification code", None
    
    async def verify_code(self, phone_number: str, code: str) -> Tuple[bool, str]:
        """
        Verify the SMS code
        Returns: (success, message)
        """
        if not self.client:
            logger.error("Twilio client not initialized")
            return False, "SMS service not available"
        
        try:
            verification_check = self.client.verify.v2.services(
                self.verify_service_sid
            ).verification_checks.create(
                to=phone_number,
                code=code
            )
            
            if verification_check.status == 'approved':
                logger.info(f"Phone verification successful for {phone_number}")
                return True, "Phone number verified successfully"
            else:
                logger.warning(f"Phone verification failed for {phone_number}: {verification_check.status}")
                return False, "Invalid verification code"
                
        except TwilioException as e:
            logger.error(f"Twilio error verifying code: {str(e)}")
            return False, f"Verification failed: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error verifying code: {str(e)}")
            return False, "Verification failed" 