# Schema Description

To include a entry in the langue, the following format needs to be followed:

```lr
@ENTRY(main EntryAssociationName: kv_field UniqueIDKeyName string "uniqueID.String") {
    cluster ClusterName {
        kv_field KeyName string "Another example string";
        kv_field AnotherKey bool true;
        kv_field YetAnotherKey int 10; 
        cluster ClusterName -> UNKEY {
            string "Value only example string";
            ...
        }
    }
} @END;
```

This language only contains 2 restricted words for now: 
- `cluster` which handles nested information;
- `kv_field` which is handles key value pairs.

A cluster can be constructed by asigning a name and including as many key value pairs, or other clusters, into it. It can be done in the following format:

```lr
cluster ClusterName {
    kv_field KeyName string "Another example string";
    kv_field AnotherKey bool true;
    kv_field YetAnotherKey int 10; 
    cluster ClusterName -> UNKEY {
        string "Value only example string";
        ...
    }
}
```

A cluster can be changed to behave as a list by assigning an the arrow operator `->`, which makes it allow only values. If can be done in the following format:

```lr
cluster ClusterName -> UNKEY {
    string "Value only example string";
    ...
}
```

> **Note**: 
> 
> Beyond UNKEY other modifier, such as `MULTABLE` and `REPETABLE[#]`, will be implemented later as well.
>
> Cluster will also support additional parameters such as `descriptor`, `id`, `linked` and `related`.
> 

As already demonstrated, the `kv_field` allows assigning a key value pair. It requires a name for the key; when assigning a value it requires a type followed by the information. It can be done in the following format:

```lr
kv_field KeyName string "Another example string";
kv_field AnotherKey bool true;
kv_field YetAnotherKey int 10; 
```

There are a few different types which can be included in a kv_field: `string`, `int`, `bool` and `null`.

> **Note**: 
> 
> Other types, such as `float`, `date()`, `range`, `percentage`, `evolution` and `array`, will be implemeted later as well. Also the `string` type will eventually support multiline comments as well.
>
> Beyond the different types to be included, the `kv_field` will also accept additional parameters such as `descriptor`, `id`, `linked` and `related`.


