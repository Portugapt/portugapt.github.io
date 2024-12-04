from electric_toolbox.common.to_file import to_file

def build(path: str) -> None:
    contents="<p>Hello World</p>"
    to_file(
        path=path,
        file_name="index.html",
        contents=contents,
    )
