# protoc-gen-objcmtl

Protocol Buffers plugin that generates Objective-C code integrated for
[Mantle Model Framework](https://github.com/Mantle/Mantle).

## Usage

```console
protoc --plugin=protoc-gen-objcmtl=protoc-gen-objcmtl.py --objcmtl_out=output *.proto
```

Optionally, you can specify an extra command line parameter to generate
Objective-C names (files, classes, and enums) with a prefix:

```
--objcmtl_opt=prefix=XY
```

## Dependencies

Python 3 and Python protobuf library.
