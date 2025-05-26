import os
import numpy as np
from dotenv import load_dotenv
from my_client import MyClient, FormattedUsage


def temperature_gen(temperature=0.5):
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

    msgs = [{"role": "system", "content": "Create 3 INVEST user stories."},
            {"role": "system", "content": f'Here is example of proper formatting: {def_of_format}'},
            {"role": "system", "content": f'Here is definition of INVEST user story: {def_of_invest}'}]

    response = client.chat.completions.create(model='gpt-4o',
                                              messages=msgs,
                                              temperature=temperature)

    with open(f'backlog/sprint1-{temperature}.md', 'w', encoding='utf-8') as f:
        client.logger.info(FormattedUsage(response.usage))
        f.write(response.choices[0].message.content)


if __name__ == '__main__':
    for temperature in np.linspace(0.1, 0.9, 7):
        temperature_gen(temperature)
