# -*- coding: UTF-8 -*-

import sys
import os
import argparse
import json
from ethereum_input_decoder import ContractAbi,AbiMethod, Utils


def main():
    parser = argparse.ArgumentParser(description='Ethereum Input decoder')

    inputs = parser.add_argument_group('inputs')
    inputs.add_argument('-t', '--tx-input', nargs='*', help='Decode transaction input to contract (hexstr)')
    inputs.add_argument('-c', '--constructor-input', help='Decode constructor argument to contract (hexstr)')

    definition = parser.add_argument_group('abi definition')
    # if abi is not set we try to lookup the sighash from 4bytes.directory
    definition.add_argument('-a', '--abi',
                            help='ABI definition in json. Expected input: String or path to json file')

    args = parser.parse_args()

    if not args.tx_input and not args.constructor_input:
        print("missing required argument --tx-input or --constructor-input")
        parser.print_help(sys.stderr)
        sys.exit(1)

    if args.abi:
        # abi provided - use abi to decode.

        if os.path.isfile(args.abi):
            with open(args.abi, 'r') as f:
                jsonabi = json.load(f)
        else:
            jsonabi = json.loads(args.abi)

        c = ContractAbi(jsonabi)

        if args.constructor_input:
            description = c.describe_constructor(Utils.str_to_bytes(args.constructor_input))
            print("\n==[Constructor]==")
            print("  Raw:         %r" % args.constructor_input)
            print("  Description: %s" % description)

        for txinput in args.tx_input:
            description = c.describe_input(Utils.str_to_bytes(txinput))
            print("\n==[Input]==")
            print("  Raw:         %r" % txinput)
            print("  Description: %s" % description)

    else:
        # abi not set, try to lookup sighash
        print("\n**online lookup**\n")
        for txinput in args.tx_input:
            description = AbiMethod.from_input_lookup(Utils.str_to_bytes(txinput))
            print("\n==[Input]==")
            print("  Raw:         %r" % txinput)
            print("  Description: %s" % description)


if __name__ == '__main__':
    main()
