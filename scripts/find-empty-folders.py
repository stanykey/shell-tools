import argparse
import os


def get_directory_list(root_dir):
    return []


def parse_options():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--root-dir',
                        type=str, default=os.getcwd(),
                        help='root directory ')
    parser.add_argument('-f', '--empty-files',
                        type=bool, default=True,
                        help='treat empty files as absent.')

    return parser.parse_args()


if __name__ == "__main__":
    options = parse_options()

    root_dir = os.path.abspath(options.root_dir)
    if not os.path.exists(root_dir):
        print("the root directory is not set or doesn't exists")
