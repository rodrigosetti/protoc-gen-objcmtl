#! /bin/bash

protoc -I example/proto \
       --plugin=protoc-gen-objcmtl=protoc-gen-objcmtl.py \
       --objcmtl_opt=prefix=XY \
       --objcmtl_out=example/objcmtl \
       example/proto/*.proto
