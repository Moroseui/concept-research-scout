"""Fixed Node connection timing; unchanged destinations, TLS and call deadline."""
from pathlib import PurePosixPath
FLAG='--network-family-autoselection-attempt-timeout=1000'

def command(argv):
    if (not isinstance(argv,list) or len(argv)!=2 or argv[0]!='/tools/node' or
            not isinstance(argv[1],str) or not argv[1].startswith('/tools/claude/') or
            '..' in PurePosixPath(argv[1]).parts or PurePosixPath(argv[1]).suffix not in {'.js','.cjs','.mjs'}):
        raise ValueError('REVIEW_CONNECTION_COMMAND_SHAPE')
    return [argv[0],FLAG,argv[1]]

def bind(runtime):
    original=runtime.claude_command
    if getattr(original,'_fixed_review_connection_timing',False):
        return lambda:None
    def fixed(*args,**kwargs):
        argv=original(*args,**kwargs)
        # Only the existing mounted Claude Node route is selected. All other
        # discovery/native commands retain their original behavior and checks.
        if kwargs.get('mounted') is True and kwargs.get('node')=='/tools/node':
            return command(argv)
        return argv
    fixed._fixed_review_connection_timing=True
    runtime.claude_command=fixed
    def restore():
        if runtime.claude_command is not fixed:raise ValueError('REVIEW_CONNECTION_BINDING_CHANGED')
        runtime.claude_command=original
    return restore
