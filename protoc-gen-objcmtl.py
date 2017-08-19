#! /usr/bin/env python3
import sys
import os
from textwrap import dedent

from google.protobuf.compiler import plugin_pb2 as plugin
from google.protobuf import descriptor_pb2 as descriptor

def printe(s):
    print(s, file=sys.stderr)

def parse_parameters(parameter):
    return dict( tuple(x.strip() for x in p.split("=")) for p in parameter.split(",") )

def objc_file_name(prefix, proto_filename):
    filename, _ = os.path.splitext(os.path.basename(proto_filename))
    filename = prefix + filename.capitalize()
    file_dir = os.path.dirname(proto_filename)

    return os.path.join(file_dir, filename)

def generate_code(request, response):
    parameters = parse_parameters(request.parameter) if request.parameter else {}
    prefix = parameters.get("prefix", "")

    for proto_file in request.proto_file:
        # TODO: Capitalize file name
        base_filename = objc_file_name(prefix, proto_file.name)

        interface_file_name = base_filename + ".h"
        impl_file_name = base_filename + ".m"

        # Interface file contents
        iface_file_contents = dedent("""\
        // Generated by the protoc-gen-objcmtl plugin.
        // source: {source}
        #import <Mantle/Mantle.h>
        """.format(source=proto_file.name))

        # list of imports
        for dependency in proto_file.dependency:
            imported = objc_file_name(prefix, dependency)
            # TODO: remove common path prefix
            iface_file_contents += '#import "%s.h"\n' % imported

        impl_file_contents = dedent("""\
        // Generated by the protoc-gen-objcmtl plugin.
        // source: {source}
        #import "{iface_file}"

        """.format(source=proto_file.name, iface_file=interface_file_name))

        # flatten the nested messages and enums
        message_types = []
        enum_types = list(proto_file.enum_type)

        msg_queue = list(proto_file.message_type)
        while msg_queue:
            # process next
            message_type = msg_queue.pop()
            # add message to flatten list (processed)
            message_types.append( message_type )

            # add nested msgs to queue for processing
            msg_queue.extend( message_type.nested_type )

            # add enums to flatten list
            enum_types.extend( message_type.enum_type )

        # render enums
        for enum_type in enum_types:
            enum_name = enum_type.name

            iface_file_contents += "typedef enum : NSUInteger {\n"
            iface_file_contents += \
                ",\n".join("   {prefix}_{name} = {number}".format(prefix=enum_name,
                                                                  name=value.name,
                                                                  number=value.number)
                           for value in enum_type.value)
            iface_file_contents += "\n}} {prefix}{name};\n\n".format(prefix=prefix, name=enum_name)

        # render messages
        for message_type in message_types:
            class_name = prefix + message_type.name
            iface_file_contents += "@interface %s : MTLModel <MTLJSONSerializing>\n" % class_name
            impl_file_contents += "@implementation %s\n" % class_name

            for field in message_type.field:
                pointer = field.type in { descriptor.FieldDescriptorProto.TYPE_MESSAGE,
                                          descriptor.FieldDescriptorProto.TYPE_BYTES,
                                          descriptor.FieldDescriptorProto.TYPE_STRING }

                if field.type in { descriptor.FieldDescriptorProto.TYPE_DOUBLE,
                                    descriptor.FieldDescriptorProto.TYPE_FLOAT,
                                    descriptor.FieldDescriptorProto.TYPE_INT64,
                                    descriptor.FieldDescriptorProto.TYPE_UINT64,
                                    descriptor.FieldDescriptorProto.TYPE_INT32,
                                    descriptor.FieldDescriptorProto.TYPE_FIXED64,
                                    descriptor.FieldDescriptorProto.TYPE_FIXED32,
                                    descriptor.FieldDescriptorProto.TYPE_UINT32,
                                    descriptor.FieldDescriptorProto.TYPE_SFIXED32,
                                    descriptor.FieldDescriptorProto.TYPE_SFIXED64,
                                    descriptor.FieldDescriptorProto.TYPE_SINT32,
                                    descriptor.FieldDescriptorProto.TYPE_SINT64 }:
                    type_name = "NSNumber"
                elif field.type == descriptor.FieldDescriptorProto.TYPE_BOOL:
                    type_name = "BOOL"
                elif field.type == descriptor.FieldDescriptorProto.TYPE_STRING:
                    type_name = "NSString"
                elif field.type in { descriptor.FieldDescriptorProto.TYPE_MESSAGE,
                                      descriptor.FieldDescriptorProto.TYPE_ENUM }:
                    # For message and enum types, this is the name of the type.  If the name
                    # starts with a '.', it is fully-qualified.  Otherwise, C++-like scoping
                    # rules are used to find the type (i.e. first the nested types within this
                    # message are searched, then within the parent, on up to the root
                    # namespace).
                    # TODO: fix
                    type_name = prefix + field.type_name
                else:
                    raise Exception("type not supported: %s" %
                                    descriptor.FieldDescriptorProto.Type.Name(field.type))

                if field.label == descriptor.FieldDescriptorProto.LABEL_REPEATED:
                    type_name = "NSArray"

                iface_file_contents += \
                    "@property {type_name} {maybe_pointer}{name};\n".format(
                            type_name=type_name,
                            maybe_pointer="*" if pointer else "",
                            name=field.name
                        )

            prop_to_jsonkey = dict((f.name, f.json_name or f.name) for f in message_type.field)
            impl_file_contents += "+ (NSDictionary *)JSONKeyPathsByPropertyKey {\n return @{\n"
            impl_file_contents += ",\n".join('@"%s": @"%s"' % fs for fs in prop_to_jsonkey.items())
            impl_file_contents += "\n            };\n}\n"

            iface_file_contents += "@end\n"
            impl_file_contents += "@end\n"
            pass

        response.file.add(name=interface_file_name, content=iface_file_contents)
        response.file.add(name=impl_file_name, content=impl_file_contents)

if __name__ == '__main__':
    # Read request message from stdin
    data = sys.stdin.buffer.read()
    # Parse request
    request = plugin.CodeGeneratorRequest()
    request.ParseFromString(data)

    # Create response
    response = plugin.CodeGeneratorResponse()

    # Generate code
    generate_code(request, response)

    # Serialise response message
    output = response.SerializeToString()

    # Write to stdout
    sys.stdout.buffer.write(output)
