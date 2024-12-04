def to_file(
    path: str,
    file_name: str,
    contents: str,
) -> None:
    with open(f"{path}/{file_name}", "w") as f:
        f.write(contents)