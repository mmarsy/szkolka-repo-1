import os
from dotenv import load_dotenv
from my_client import MyClient, FormattedUsage


if __name__ == '__main__':
    load_dotenv()

    client = MyClient(
        api_version="2024-10-21",
        azure_endpoint=os.getenv("MY_BASE_URL"),
        api_key=os.getenv("API_KEY"),
    )

    def_of_invest = '''
INVEST criteria for user stories:
- Independent
- Negotiable
- Valuable
- Estimable
- Small
- Testable
'''

    def_of_format = '''
    ### User Story 
**As a** returning customer  
**I want to** log in using Google  
**So that** I can quickly access my account

**Acceptance Criteria:**
- Google login button is visible on login page
- Authentication works for valid Google accounts
- User is redirected to their dashboard after login'''

    msgs = [{"role": "system", "content": "Create 3 INVEST user stories."}]

    response = client.chat.completions.create(model='gpt-4o',
                                              messages=msgs,
                                              temperature=0.5)

    with open('backlog/sprint1.md', 'w') as f:
        client.logger.info(FormattedUsage(response.usage))
        f.write(response.choices[0].message.content)
