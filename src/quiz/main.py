import argparse
import json
import logging
import os
from dotenv import load_dotenv
from my_client import Chat, FormattedUsage


load_dotenv()
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger('ASSERT DEBUG')


class EndGame(BaseException):
    pass


class AssessedChat(Chat):
    def ask(self, prompt, **kwargs):
        self.append({'role': 'user', 'content': prompt})
        score = None

        try:
            user = User.read_json(os.getenv("QUIZ_USER_STATE"))
            score = user['score']
            user.asses(self)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=self,
                **kwargs
            )
            if self.logger is not None:
                self.logger.info(FormattedUsage(response.usage))
            response_content = response.choices[0].message.content
            self.append({'role': 'assistant', 'content': response_content})
            return f'{self.chat_indicator}{response_content}'

        except EndGame:
            print(f"Game over. Your score: {score}")
            User.new_user()

    @staticmethod
    def read_json(filename, **kwargs):
        with open(filename, 'r') as f:
            obj = json.load(f)
            return AssessedChat(obj, **kwargs)


class User(dict):
    prompt_src = f'{os.getenv("PROMPTS_DIR")}quiz_assessor.txt'
    with open(prompt_src,  'r') as f:
        initial_prompt = [{"role": "system", "content": f.read()}]

    def asses(self, lst: Chat):
        try:
            prompt = self.initial_prompt
            prompt.append({"role": "system", "content": str(lst[-2:])})

            logger.debug(prompt)

            assessor = Chat(initial_prompt=prompt, initiative=False)
            outcome = assessor.ask("")

            if outcome == 'WRONG':
                self['lives'] -= 1
                if self['lives'] == 0:
                    raise EndGame

            if outcome == 'CORRECT':
                self['score'] += 1

            self.save(os.getenv("QUIZ_USER_STATE"))

        except IndexError:
            print('asses index error')

    def save(self, filename):
        with open(filename, 'w') as f:
            f.write(json.dumps(self))

    @staticmethod
    def read_json(filename):
        with open(filename, 'r') as f:
            obj = json.load(f)
            return User(**obj)

    @staticmethod
    def new_user():
        new_user = User(lives=3, score=0)
        new_user.save(os.getenv("QUIZ_USER_STATE"))


# answer current question
def answer(args):
    chat = AssessedChat.read_json(filename=os.getenv('QUIZ_CHAT_HISTORY'), initiative=False, chat_indicator='')
    print(chat.ask(args.ans))
    chat.save(os.getenv('QUIZ_CHAT_HISTORY'))


# show current question
def question(args):
    chat = Chat.read_json(filename=os.getenv('QUIZ_CHAT_HISTORY'), initiative=False, chat_indicator='')
    try:
        last_chat = [item for item in chat if item['role'] == 'assistant'][-1]
        print(last_chat['content'])

    except IndexError:
        print('Index error')


# begin quiz
def begin(args):
    open(os.getenv("QUIZ_CHAT_HISTORY"), 'w').close()

    prompt_src = f'{os.getenv("PROMPTS_DIR")}quiz_host.txt'
    with open(prompt_src, 'r') as f:
        initial_prompt = [{'role': 'system', 'content': f.read()}]

    Chat(initial_prompt=initial_prompt).save(os.getenv("QUIZ_CHAT_HISTORY"))


# inspect user status
def status(args):
    user = User.read_json(os.getenv("QUIZ_USER_STATE"))
    print(f'Lives: {user["lives"]}, Score: {user["score"]}')


def main():
    parser = argparse.ArgumentParser(description="My CLI tool")
    subparsers = parser.add_subparsers(dest="command")

    begin_parser = subparsers.add_parser("begin", help="Begin quiz.")
    begin_parser.set_defaults(func=begin)

    question_parser = subparsers.add_parser("question", help="Remind last question.")
    question_parser.set_defaults(func=question)

    answer_parser = subparsers.add_parser("ans", help="Answer question.")
    answer_parser.add_argument("ans")
    answer_parser.set_defaults(func=answer)

    status_parser = subparsers.add_parser("status", help="Inspect user status.")
    status_parser.set_defaults(func=status)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    load_dotenv()
    u = User(lives=3)
    u.save(os.getenv("QUIZ_USER_STATE"))
    print(User.read_json(os.getenv("QUIZ_USER_STATE")))
