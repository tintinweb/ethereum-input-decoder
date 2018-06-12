# -*- coding: UTF-8 -*-
"""
Utility functions for decoding inputs/arguments based on contract json abi definitions
"""
from eth_abi.abi import decode_abi
import eth_abi.exceptions
import binascii
import requests


class Utils:
    
    @staticmethod
    def str_to_bytes(s):
        """
        Convert 0xHexString to bytes
        :param s: 0x hexstring
        :return:  byte sequence
        """
        return bytes.fromhex(s.replace("0x", ""))

    @staticmethod
    def bytes_to_str(s):
        return "0x%s" % binascii.hexlify(s).decode("utf-8")


class FourByteDirectory(object):

    @staticmethod
    def parse_text_signature(text_signature):
        # no need for a fully blown parser here for now for the sake of minimal dependencies
        name, rest = text_signature.split("(", 1)
        args, rest = rest.strip().rsplit(")", 1)
        args = args.strip()
        return {'name': name.strip(),
                'type': 'function',
                'inputs': [{'name': 'arg%d' % i, 'type': a.strip()} for i, a in enumerate(args.split(",")) if args],
                'outputs': []}

    @staticmethod
    def lookup_signatures(sighash):
        resp = requests.get("https://www.4byte.directory/api/v1/signatures/?hex_signature=%s" % sighash).json()
        for sig in resp["results"]:
            yield sig["text_signature"]

    @staticmethod
    def get_pseudo_abi_for_sighash(sighash):
        for text_signature in FourByteDirectory.lookup_signatures(sighash):
            pseudo_abi = FourByteDirectory.parse_text_signature(text_signature)
            pseudo_abi['signature'] = sighash
            yield pseudo_abi

    @staticmethod
    def get_pseudo_abi_for_input(s):
        """
        Lookup sighash from 4bytes.directory, create a pseudo api and try to decode it with the parsed abi.
        May return multiple results as sighashes may collide.
        :param s: bytes input
        :return: pseudo abi for method
        """
        sighash = Utils.bytes_to_str(s[:4])
        for pseudo_abi in FourByteDirectory.get_pseudo_abi_for_sighash(sighash):
            types = [ti["type"] for ti in pseudo_abi['inputs']]
            try:
                # test decoding
                _ = decode_abi(types, s[4:])
                yield pseudo_abi
            except eth_abi.exceptions.DecodingError as e:
                continue


class ContractAbi(object):
    """
    Utility Class to encapsulate a contracts ABI
    """
    def __init__(self, jsonabi):
        self.abi = jsonabi
        self.signatures = {}
        self._prepare_abi(jsonabi)

    def _add_method_abi(self, jsonmethodabi):
        self.abi.append(jsonmethodabi)  # add the json-method-abi to the internal json repr
        self._prepare_abi(self.abi)  # re-init internal structures

    def _prepare_abi(self, jsonabi):
        """
        Prepare the contract json abi for sighash lookups and fast access

        :param jsonabi: contracts abi in json format
        :return:
        """
        self.signatures = {}
        for element_description in jsonabi:
            abi_e = AbiMethod(element_description)
            if abi_e["type"] == "constructor":
                self.signatures[b"__constructor__"] = abi_e
            elif abi_e["type"] == "fallback":
                abi_e.setdefault("inputs", [])
                self.signatures[b"__fallback__"] = abi_e
            elif abi_e["type"] == "function":
                self.signatures[Utils.str_to_bytes(abi_e["signature"])] = abi_e
            elif abi_e["type"] == "event":
                self.signatures[b"__event__"] = abi_e
            else:
                raise Exception("Invalid abi type: %s - %s - %s" % (abi_e.get("type"),
                                                                    element_description, abi_e))

    def describe_constructor(self, s):
        """
        Describe the input bytesequence (constructor arguments) s based on the loaded contract
         abi definition

        :param s: bytes constructor arguments
        :return: AbiMethod instance
        """
        method = self.signatures.get(b"__constructor__")
        if not method:
            # constructor not available
            m = AbiMethod({"type": "constructor", "name": "", "inputs": [], "outputs": []})
            return m

        types_def = method["inputs"]
        types = [t["type"] for t in types_def]
        names = [t["name"] for t in types_def]

        if not len(s):
            values = len(types) * ["<nA>"]
        else:
            values = decode_abi(types, s)

        # (type, name, data)
        method.inputs = [{"type": t, "name": n, "data": v} for t, n, v in list(
            zip(types, names, values))]
        return method

    def describe_input(self, s):
        """
        Describe the input bytesequence s based on the loaded contract abi definition

        :param s: bytes input
        :return: AbiMethod instance
        """
        signatures = self.signatures.items()

        for sighash, method in signatures:
            if sighash is None or sighash.startswith(b"__"):
                continue  # skip constructor

            if s.startswith(sighash):
                s = s[len(sighash):]

                types_def = self.signatures.get(sighash)["inputs"]
                types = [t["type"] for t in types_def]
                names = [t["name"] for t in types_def]

                if not len(s):
                    values = len(types) * ["<nA>"]
                else:
                    values = decode_abi(types, s)

                # (type, name, data)
                method.inputs = [{"type": t, "name": n, "data": v} for t, n, v in list(
                    zip(types, names, values))]
                return method
        else:
            method = AbiMethod({"type": "fallback",
                                "name": "__fallback__",
                                "inputs": [], "outputs": []})
            types_def = self.signatures.get(b"__fallback__", {"inputs": []})["inputs"]
            types = [t["type"] for t in types_def]
            names = [t["name"] for t in types_def]

            values = decode_abi(types, s)

            # (type, name, data)
            method.inputs = [{"type": t, "name": n, "data": v} for t, n, v in list(
                zip(types, names, values))]
            return method


class AbiMethod(dict):
    """
    Abstraction for an abi method that easily serializes to a human readable format.
    The object itself is an extended dictionary for easy access.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inputs = []

    def __str__(self):
        return self.describe()

    @staticmethod
    def from_input_lookup(s):
        """
        Return a new AbiMethod object from an input stream
        :param s: binary input
        :return: new AbiMethod object matching the provided input stream
        """
        for pseudo_abi in FourByteDirectory.get_pseudo_abi_for_input(s):
            method = AbiMethod(pseudo_abi)
            types_def = pseudo_abi["inputs"]
            types = [t["type"] for t in types_def]
            names = [t["name"] for t in types_def]

            values = decode_abi(types, s[4:])

            # (type, name, data)
            method.inputs = [{"type": t, "name": n, "data": v} for t, n, v in list(
                zip(types, names, values))]
            return method

    def describe(self):
        """

        :return: string representation of the methods input decoded with the set abi
        """
        outputs = ", ".join(["(%s) %s" % (o["type"], o["name"]) for o in
                             self["outputs"]]) if self.get("outputs") else ""
        inputs = ", ".join(["(%s) %s = %r" % (i["type"], i["name"], i["data"]) for i in
                            self.inputs]) if self.inputs else ""
        return "%s %s %s returns %s" % (self["type"], self.get("name"), "(%s)" % inputs
            if inputs else "()", "(%s)" % outputs if outputs else "()")
