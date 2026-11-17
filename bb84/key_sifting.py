def sift_keys(alice_bits, alice_bases, bob_bits, bob_bases):
    if not (
        len(alice_bits)
        == len(alice_bases)
        == len(bob_bits)
        == len(bob_bases)
    ):
        raise ValueError("All input sequences must have the same length.")

    matching_indices = [
        index
        for index in range(len(alice_bits))
        if alice_bases[index] == bob_bases[index]
    ]

    alice_key = [
        int(alice_bits[index])
        for index in matching_indices
    ]

    bob_key = [
        int(bob_bits[index])
        for index in matching_indices
    ]

    return matching_indices, alice_key, bob_key
