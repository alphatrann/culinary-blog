from culinary_blog.cache import keys


def test_query_hash_ignores_parameter_order_and_distinguishes_values():
    assert keys.query_hash(a=1, b=None) == keys.query_hash(b=None, a=1)
    assert keys.query_hash(a=1) != keys.query_hash(a=2)
    assert keys.query_hash(a=None) != keys.query_hash(a="None2")
