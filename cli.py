import sys

import import_from_c as ImportC
from megahal import MegaHAL
from checkpoint import CheckpointSaver

import random
import argparse
import json

def talk(model, input, learn=False):
    print(model.respond(input))
    
    if learn:
        model.learn(input)

def main():
    parser = argparse.ArgumentParser(description="Chatbot Parameters")
    parser.add_argument('--interactive', action='store_true', help='Enter interactive mode with prompt/reply loop')
    parser.add_argument('--input', type=str, help='Provide a one-off input sentence for a reply')
    parser.add_argument('--learn', action='store_true', help='Enable model learning from input')
    parser.add_argument('--train', type=str, help='Train the model from a text file')
    parser.add_argument('--import_brain', type=str, help='Path to old format brain file to load as baseline')
    parser.add_argument('--brain', type=str, default="megahal.pkl", help='Filename for new format brain')
    parser.add_argument('--print', action='store_true', help='Dump the model to stdout')

    args = parser.parse_args()

    checkpoint = CheckpointSaver(args.brain)

    if args.import_brain:
        print(f"Importing legacy brain from {args.import_brain}")
        bot = ImportC.import_model(args.import_brain)
    else:
        bot = checkpoint.load_checkpoint() or MegaHAL()

    if args.train:
        with open(args.train,"r") as corpus:
            for line in corpus:
                bot.learn(line)

    if args.print:
        print(json.dumps(bot.to_dict()))

    if args.learn:
        print("Learning mode enabled.")

    if args.interactive:
        print("Interactive mode activated. Enter 'exit' to quit.")

        while True:
            user_input = input(">")
            if user_input.lower() == 'exit':
                break
            talk(bot, user_input, args.learn)

    elif args.input:
        talk(bot, args.input, args.learn)

    if args.learn or args.import_brain or args.train:
        checkpoint.save_checkpoint(bot)


if __name__ == "__main__":
    main()