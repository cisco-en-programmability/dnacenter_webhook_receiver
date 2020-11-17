
# Cisco DNA Center Webhook Receiver


**Cisco Products & Services:**

- Cisco DNA Center, Webhook receiver

**Tools & Frameworks:**

- Python environment to run the Flask App

**Usage**

 - Create a new Flask App to receive Cisco DNA Center notifications
 - "flask_receiver.py" - webhook receiver 
 - "config.py" - configure your lab environment
 - "test_webhook_receiver" - app to test the webhook receiver without Cisco DNA Center
 - The notifications received will be save to the file "all_webhooks_detailed.log"
 - Start the Flask App
 - Test by browsing to your receiver home page
 - Configure Cisco DNA Center Webhooks to send notifications to your new receiver
 - Trigger events for the configured webhooks
 - Verify the events are received by the webhook receiver
 - Sample Output:
 
 
 This sample code is for proof of concepts and labs

**License**

This project is licensed to you under the terms of the [Cisco Sample Code License](./LICENSE).
