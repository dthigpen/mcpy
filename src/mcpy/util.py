from pathlib import Path

def file_path_to_mcfunction_path(path: Path):
    name = path.stem
    path = str(path)
    relevant_parts = list(Path(path[path.rindex('/data/') + 6:]).parts)
    namespace = relevant_parts.pop(0)
    relevant_parts.pop(0) # functions
    relevant_parts.pop() # last
    relevant_parts.append(name)
    print('parts', relevant_parts)
    return f'{namespace}:{"/".join(relevant_parts)}'
