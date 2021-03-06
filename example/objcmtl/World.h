// Generated by the protoc-gen-objcmtl plugin.
// source: world.proto
#import <Mantle/Mantle.h>
#import "Hello.h"
typedef enum : NSUInteger {
   A = 0,
   B = 1
} XYNestedEnum;

@class XYWorld;
@class XYNestedMsg;

@interface XYWorld : MTLModel <MTLJSONSerializing>
@property XYNestedMsg *nested;
@property XYHello *hello;
@property XYNestedEnum enum_test;
@property NSArray *names;
@end

@interface XYNestedMsg : MTLModel <MTLJSONSerializing>
@property NSNumber *code;
@end
