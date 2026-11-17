def transmit(circuits):
    """
    Simulate an ideal quantum channel.
    Each quantum circuit is copied before transmission.
    """
    return [circuit.copy() for circuit in circuits]
