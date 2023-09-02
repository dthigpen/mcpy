from mcpy import *

@datapack
def simple_pack():
    # get-started.md ------------------------
    with namespace("simple_datapack"):
        with directory("api/greetings"):
            @mcfunction
            def say_hello():
                yield "say Hello!"
                write('say There!')

    with namespace("minecraft"):
        @functions
        def load():
            yield {"values": [str(say_hello)]}
    #----------------------------------------
    
