# AWS Lambda Transit Notifier Deployment Instructions

This document outlines the steps to prepare, deploy, and schedule your AWS Lambda function that sends you an email telling you when to leave work to catch the transit.

## Step 1: Prepare the lambda_function.py for Upload

- **Download Required Packages Locally:**
  - AWS Lambda does not include external libraries like `requests` by default.
  - You need to install such packages locally in your project directory so that they are bundled with your deployment package.
  - To install the `requests` package (and its dependencies) into your current directory, run:
    ```bash
    pip install requests -t .
    ```
  - This command places the `requests` library within your project directory, ensuring it gets included in the zip file.

- **Zip the Project Directory:**
  - After ensuring that `lambda_function.py` and the locally installed packages are in your project directory, package everything into a zip file:
    ```bash
    zip -r lambda_function.zip .
    ```

## Step 2: Upload to AWS Lambda Serverless Function

- **Create the Lambda Function:**
  - Create your Lambda function by uploading the `lambda_function.zip` file.
- **Set Environment Variables:**
  - In the Lambda function configuration, specify the following environment variables:
    - `GOOGLE_API_KEY`: Your Google Maps API key.
    - `ORIGIN`: The starting address.
    - `DESTINATION`: The destination address.
    - `SES_SENDER`: The verified sender email address in AWS SES.
    - `SES_RECIPIENT`: The recipient email address.
- **Test the Function:**
  - Execute a test run to verify that the Lambda function performs as expected.

## Step 3: Enable AWS SES and Verify Email

- **Enable AWS SES:**
  - Enable AWS Simple Email Service (SES) and go through the verification process for the email address that will receive notifications.
- **Test Email Functionality:**
  - Re-test the Lambda function until you confirm that emails are being successfully sent.

## Step 4: Setup AWS EventBridge Schedules

- **Configure the Scheduler:**
  - Use AWS EventBridge to schedule your Lambda function to run at the desired time each weekday.
- **Expected Outcome:**
  - Once configured, you should receive an email each weekday informing you when to leave to catch your transit.
