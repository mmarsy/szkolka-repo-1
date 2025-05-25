import argparse


def greet(args):
    if args.formal:
        print(f"Good day, {args.name}.")
    else:
        print(f"Hey {args.name}!")


def add(args):
    print(f"{args.x} + {args.y} = {args.x + args.y}")


def main():
    parser = argparse.ArgumentParser(description="My CLI tool")
    subparsers = parser.add_subparsers(dest="command")

    greet_parser = subparsers.add_parser("greet", help="Greet someone")
    greet_parser.add_argument("name")
    greet_parser.add_argument("--formal", action="store_true")
    greet_parser.set_defaults(func=greet)

    add_parser = subparsers.add_parser("add", help="Add two numbers")
    add_parser.add_argument("x", type=int)
    add_parser.add_argument("y", type=int)
    add_parser.set_defaults(func=add)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
