import requests
import json
import sys

def get_discord_token(email, password, code=None):
    """
    Get Discord authentication token using email and password
    Optionally uses 2FA code if provided
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMC4wLjAuMCBTYWZhcmkvNTM3LjM2In0='
    }
    
    # Create login field with email and password
    login_data = {
        'login': email,
        'password': password
    }

    try:
        # Initial login request
        response = requests.post('https://discord.com/api/v10/auth/login',
                                headers=headers,
                                json=login_data)

        if response.status_code == 200:
            data = response.json()

            # Check if we got a token directly
            if 'token' in data:
                return data['token']

            # If we need 2FA
            if 'mfa' in data and data['mfa'] == True:
                if not code:
                    print("2FA is enabled. Please provide your authentication code.")
                    return None

                # Try with 2FA code
                mfa_data = {
                    'code': code,
                    'ticket': data['ticket']
                }

                mfa_response = requests.post('https://discord.com/api/v10/auth/mfa/totp',
                                           headers=headers,
                                           json=mfa_data)

                if mfa_response.status_code == 200:
                    mfa_result = mfa_response.json()
                    if 'token' in mfa_result:
                        return mfa_result['token']

                print("Failed to authenticate with 2FA code.")
                return None

        print(f"Login failed with status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def save_token_to_file(token, filename="discord_token.txt"):
    """Save the token to a file"""
    with open(filename, 'w') as f:
        f.write(token)
    print(f"Token saved to {filename}")

def main():
    print("Discord Token Retriever for Termux")
    print("----------------------------------")

    # Get user credentials
    email = input("Enter your Discord email: ")
    password = input("Enter your Discord password: ")

    # Check if 2FA is needed
    use_2fa = input("Do you have 2FA enabled? (y/n): ").lower() == 'y'
    code = None

    if use_2fa:
        code = input("Enter your 2FA code: ")

    # Get the token
    token = get_discord_token(email, password, code)

    if token:
        print("\nSuccessfully retrieved Discord token:")
        print(token)

        save = input("\nSave token to file? (y/n): ").lower() == 'y'
        if save:
            save_token_to_file(token)
    else:
        print("\nFailed to retrieve Discord token.")
        print("Possible reasons:")
        print("1. Incorrect email or password")
        print("2. 2FA is enabled but you didn't provide the code")
        print("3. Account may be locked or requires captcha verification")
        print("4. Discord may have updated their authentication API")

if __name__ == "__main__":
    main()
