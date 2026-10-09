"""Bounded stdin transport for the unchanged fit guard and canonical payload.

The existing SDK command limit remains enforced before any paid creation.
A failed or interrupted send propagates to the existing uncertain-run refusal.
"""
import hashlib

MAX_PAYLOAD = 120000
ARG_MAX_BYTES = 65536


def require(ok, reason):
    if not ok:
        raise ValueError('FIT_STDIN_' + reason)


def arguments(interpreter, source, payload):
    require(isinstance(interpreter, str) and interpreter.startswith('/'), 'INTERPRETER')
    require(isinstance(source, str) and bool(source), 'SOURCE')
    require(isinstance(payload, bytes) and 0 < len(payload) <= MAX_PAYLOAD, 'PAYLOAD_BOUND')
    # Compile only: fail on malformed guard source before allocating compute.
    compile(source, '<reviewed-fit-guard>', 'exec')
    pin = hashlib.sha256(payload).hexdigest()
    bootstrap = (
        "import sys,hashlib\n"
        "_transport_payload=sys.stdin.buffer.read(120001)\n"
        "if len(sys.argv)!=3:raise ValueError('FIT_STDIN_ARGUMENTS')\n"
        "if not 0<len(_transport_payload)<=120000:raise ValueError('FIT_STDIN_PAYLOAD_BOUND')\n"
        "if len(_transport_payload)!=int(sys.argv[1]):raise ValueError('FIT_STDIN_LENGTH')\n"
        "if hashlib.sha256(_transport_payload).hexdigest()!=sys.argv[2]:raise ValueError('FIT_STDIN_HASH')\n"
        "sys.argv=[sys.argv[0],_transport_payload.decode('utf-8')]\n"
        "exec(compile(" + repr(source) + ",'<reviewed-fit-guard>','exec'),globals())\n"
    )
    args = (interpreter, '-B', '-s', '-c', bootstrap, str(len(payload)), pin)
    require(sum(len(a.encode('utf-8')) for a in args) <= ARG_MAX_BYTES, 'SDK_ARGUMENT_BOUND')
    return args


def send(sandbox, args, payload, *, timeout, workdir, stdout, stderr):
    """One exec and one send; the caller owns the durable execute intent."""
    require(isinstance(payload, bytes) and 0 < len(payload) <= MAX_PAYLOAD, 'PAYLOAD_BOUND')
    require(len(args) == 7 and args[-2:] == (str(len(payload)), hashlib.sha256(payload).hexdigest()),
            'PAYLOAD_BINDING')
    require(sum(len(a.encode('utf-8')) for a in args) <= ARG_MAX_BYTES, 'SDK_ARGUMENT_BOUND')
    process = sandbox.exec(*args, timeout=timeout, workdir=workdir, stdout=stdout, stderr=stderr)
    process.stdin.write(payload)
    process.stdin.write_eof()
    process.stdin.drain()
    return {'schema':'fit-stdin-transport/v1', 'bytes':len(payload),
            'sha256':hashlib.sha256(payload).hexdigest(), 'eof':True}
