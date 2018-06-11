# ethereum-input-decoder
Decode transaction inputs and constructor arguments based on the ethereum contract ABI. Tries to lookup function
signature hashes from 4bytes.directory.

* python3
* suggested as a PR to [eth-abi #69](https://github.com/ethereum/eth-abi/pull/69)
* the heavy lifting is done by `eth-abi`
* utilized in [pyetherchain](https://github.com/tintinweb/pyetherchain) to decode and dump smart contract code with inputs

Decode transaction inputs and constructor arguments to contract at [0xab7c74abc0c4d48d1bdad5dcb26153fc8780f83e](https://etherscan.io/address/0xab7c74abc0c4d48d1bdad5dcb26153fc8780f83e#code) to a more human friendly notation.

#### Example: Decode providing the ABI as .json

Usage:

    python -m ethereum_input_decoder -a ./test/contract_abi_ab7c74abc0c4d48d1bdad5dcb26153fc8780f83e.json -c 000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000de0b6b3a764000000000000000000000000000000000000000000000000000000000000000000040000000000000000000000002903cadbe271e057edef157340b52a5898d7424f000000000000000000000000ba7ca1bcf210c1b37cf5818816c4a819c3040ea700000000000000000000000014cd6536d449e3f6878f2d6859e1ff92ae0990e60000000000000000000000000c24441e42277445e38e02dfc3494577c05ba46b -t 0x797af62798d790d3133e0049215669e09b55a0b59d586c95f94c2d56b2812040133d7707 -t 0x797af62798d790d3133e0049215669e09b55a0b59d586c95f94c2d56b2812040133d7707

Output:

    ==[Constructor]==
      Raw:         '000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000de0b6b3a764000000000000000000000000000000000000000000000000000000000000000000040000000000000000000000002903cadbe271e057edef157340b52a5898d7424f000000000000000000000000ba7ca1bcf210c1b37cf5818816c4a819c3040ea700000000000000000000000014cd6536d449e3f6878f2d6859e1ff92ae0990e60000000000000000000000000c24441e42277445e38e02dfc3494577c05ba46b'
      Description: constructor None ((address[]) _owners = ('0x2903cadbe271e057edef157340b52a5898d7424f', '0xba7ca1bcf210c1b37cf5818816c4a819c3040ea7', '0x14cd6536d449e3f6878f2d6859e1ff92ae0990e6', '0x0c24441e42277445e38e02dfc3494577c05ba46b'), (uint256) _required = 2, (uint256) _daylimit = 1000000000000000000) returns ()

    ==[Input]==
      Raw:         '0x797af62798d790d3133e0049215669e09b55a0b59d586c95f94c2d56b2812040133d7707'
      Description: function confirm ((bytes32) _h = b'\x98\xd7\x90\xd3\x13>\x00I!Vi\xe0\x9bU\xa0\xb5\x9dXl\x95\xf9L-V\xb2\x81 @\x13=w\x07') returns ((bool) )


#### Example: Decode without providing the ABI and forcing an online lookup from 4bytes.directory

Usage:

    python -m ethereum_input_decoder -t 0x166eb4cb962ee1f494711b8726972fc3b23519008854ca46e73383da53aea339ee82ee7d0000000000000000000000000000000000000000000000000000000000000000

Output:

    **online lookup**


    ==[Input]==
      Raw:         '0x166eb4cb962ee1f494711b8726972fc3b23519008854ca46e73383da53aea339ee82ee7d0000000000000000000000000000000000000000000000000000000000000000'
      Description: function Put ((bytes32) arg0 = b'\x16n\xb4\xcb\x96.\xe1\xf4\x94q\x1b\x87&\x97/\xc3\xb25\x19\x00\x88T\xcaF\xe73\x83\xdaS\xae\xa39', (uint256) arg1 = 107881794066862459943708362605633226548906029344009971714560720257241323667456) returns ()


## API

```python
from ethereum_input_decoder import ContractAbi

ca = ContractAbi(json.loads(json_abi_str))
print(ca.describe_input(b'797aaf...3d7707'))
# function confirm ((bytes32) _h = b'\x98\xd7\x90\xd3\x13>\x00I!Vi\xe0\x9bU\xa0\xb5\x9dXl\x95\xf9L-V\xb2\x81 @\x13=w\x07') returns ((bool) )
print(ca.describe_constructor(b'000000...5ba46b")))
# constructor None ((address[]) _owners = ('0x2903cadbe271e057edef157340b52a5898d7424f', '0xba7ca1bcf210c1b37cf5818816c4a819c3040ea7', '0x14cd6536d449e3f6878f2d6859e1ff92ae0990e6', '0x0c24441e42277445e38e02dfc3494577c05ba46b'), (uint256) _required = 2, (uint256) _daylimit = 1000000000000000000) returns ()
```
```python
# online lookup without having an ABI ready
from ethereum_input_decoder AbiMethod

print(AbiMethod.from_input_lookup(Utils.str_to_bytes(txinput)))
# function Put ((bytes32) arg0 = b'\x16n\xb4\xcb\x96.\xe1\xf4\x94q\x1b\x87&\x97/\xc3\xb25\x19\x00\x88T\xcaF\xe73\x83\xdaS\xae\xa39', (uint256) arg1 = 107881794066862459943708362605633226548906029344009971714560720257241323667456) returns ()
```
