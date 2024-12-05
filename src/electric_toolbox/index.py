from electric_toolbox.common.to_file import to_file

from jinja2 import Environment
    

def build(path: str, j2_env: Environment,) -> None:
    nav = j2_env.get_template("index/index.j2")
    contents = nav.render()

    to_file(
        path=path,
        file_name="index.html",
        contents=contents,
    )
