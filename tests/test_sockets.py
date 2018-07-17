from pandamonium.sockets import make_internal_socket


def test_internal_socket():
    client_socket, agent_socket = make_internal_socket()
    assert client_socket.read() is None
    assert agent_socket.read() is None
    client_socket.send('foo')
    assert agent_socket.read() == 'foo'
    assert agent_socket.read() is None
    agent_socket.send('foo')
    assert client_socket.read() == 'foo'
    assert client_socket.read() is None
