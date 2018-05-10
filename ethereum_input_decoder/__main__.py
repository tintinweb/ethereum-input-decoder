# -*- coding: UTF-8 -*-

from ethereum_input_decoder import ContractAbi
import argparse
import json
import sys, os

def main():
    parser = argparse.ArgumentParser(description='Ethereum Input decoder')

    inputs = parser.add_argument_group('inputs')
    inputs.add_argument('-t', '--tx-input', nargs='*', help='Decode transaction input to contract (hexstr)')
    inputs.add_argument('-c', '--constructor-input', help='Decode constructor argument to contract (hexstr)')

    definition = parser.add_argument_group('abi definition')
    definition.add_argument('-a', '--abi', required=True,
                            help='ABI definition in json. Expected input: String or path to json file')

    args = parser.parse_args()

    if not args.tx_input and not args.constructor_input:
        print("missing required argument --tx-input or --constructor-input")
        parser.print_help(sys.stderr)
        sys.exit(1)

    if os.path.isfile(args.abi):
        with open(args.abi, 'r') as f:
            jsonabi = json.load(f)
    else:
        jsonabi = json.loads(args.abi)

    c = ContractAbi(jsonabi)

    if args.constructor_input:
        description = c.describe_constructor(ContractAbi.str_to_bytes(args.constructor_input))
        print("\n==[Constructor]==")
        print("  Raw:         %r" % args.constructor_input)
        print("  Description: %s" % description)

    for txinput in args.tx_input:
        description = c.describe_input(ContractAbi.str_to_bytes(txinput))
        print("\n==[Input]==")
        print("  Raw:         %r" % txinput)
        print("  Description: %s" % description)



if __name__ == '__main__':
    main()