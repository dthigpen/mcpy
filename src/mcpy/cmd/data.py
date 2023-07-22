from .common import EntityPath, StoragePath, BlockPath, Value, get_target_type


def modify_set(target: EntityPath | StoragePath | BlockPath, source: EntityPath | StoragePath | BlockPath | Value| str):
    target_type = get_target_type(target)
    source_type = get_target_type(source)
    yield f'data modify {target_type} {target} set from {source_type} {source}'


def modify_append(target: EntityPath | StoragePath | BlockPath, source: EntityPath | StoragePath | BlockPath | Value| str):
    target_type = get_target_type(target)
    source_type = get_target_type(source)
    yield f'data modify {target_type} {target} append from {source_type} {source}'