from horizon.services import api_keys


def test_generated_keys_are_prefixed_and_unique():
    a, b = api_keys.generate_key(), api_keys.generate_key()
    assert a.startswith("hzn_live_")
    assert api_keys.generate_key(live=False).startswith("hzn_test_")
    assert a != b


def test_hash_is_deterministic_and_pepper_dependent():
    key = api_keys.generate_key()
    assert api_keys.hash_key(key, "pepper") == api_keys.hash_key(key, "pepper")
    assert api_keys.hash_key(key, "pepper") != api_keys.hash_key(key, "other-pepper")


def test_hash_does_not_contain_plaintext():
    key = api_keys.generate_key()
    digest = api_keys.hash_key(key, "pepper")
    assert key not in digest
    assert len(digest) == 64


def test_display_prefix_is_a_strict_truncation():
    key = api_keys.generate_key()
    prefix = api_keys.display_prefix(key)
    assert key.startswith(prefix)
    assert len(prefix) == api_keys.PREFIX_DISPLAY_LEN
    assert len(prefix) < len(key)
