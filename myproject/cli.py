from argparse import ArgumentParser


def parse_args():
    parser = ArgumentParser(description="Description of your program")
    parser.add_argument("-f", "--foo", help="Description for foo argument", required=True)

    return parser.parse_args()


def main():
    args = parse_args()
    print(args)
