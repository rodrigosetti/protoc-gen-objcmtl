# protoc-gen-objcmtl

Protocol Buffers plugin that generates Objective-C code integrated for
[Mantle Model Framework](https://github.com/Mantle/Mantle).

See the source and generated [example](example) for a sample of output code.

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

## Limitations

 * Doesn't support the "group type", which is deprecated in protobuf version 3.
 * Doesn't support the type "bytes".
 * Doesn't support extensions.
