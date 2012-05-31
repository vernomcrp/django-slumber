"""
    A test version of the client.
"""
import mock

from slumber.connector.api import get_model_type
from slumber.connector.dictobject import DictObject


def _do_get(model, **query):
    """Implements a mocked version of the get operator.
    """
    for i in model.instances:
        found = True
        for k, v in query.items():
            found = found and getattr(i, k) == v
        if found:
            return i
    assert False, "The instance was not found"


class _MockInstance(DictObject):
    """A mock instance that will add in a _url parameter.
    """
    def __init__(self, model_path, **kwargs):
        super(_MockInstance, self).__init__(**kwargs)
        if hasattr(self, 'pk'):
            self._url = ('slumber://' + model_path.replace('__', '/')
                + '/data/%s/' % getattr(self, 'pk'))

    def __repr__(self):
        return getattr(self, '_url', 'Unkown mock instance')


class _MockClient(DictObject):
    """Mock slumber client class.
    """
    def __init__(self, **instances):
        super(_MockClient, self).__init__()
        for model, instances in instances.items():
            root = self
            for k in model.split('__')[:-1]:
                if not hasattr(root, k):
                    setattr(root, k, DictObject())
                root = getattr(root, k)
            model_name = model.split('__')[-1]
            model_url = model.replace('__', '/') + '/'
            model_type = get_model_type(model_url, [_MockInstance])
            setattr(model_type, 'instances',
                [model_type(model, **i) for i in instances])
            setattr(model_type, 'get', classmethod(_do_get))
            setattr(root, model_name, model_type)

    def _flush_client_instance_cache(self):
        """Empty stub so that the middleware works in tests.
        """


def mock_client(**instances):
    """Replaces the client with a mocked client that provides access to the
    provided applications, models and instances.
    """
    models = _MockClient(**instances)
    def decorator(test_method):
        """The actual decorator that is going to be used on the test method.
        """
        @mock.patch('slumber._client', models)
        def test_wrapped(test, *a, **kw):
            """The wrapper for the test method.
            """
            test_method(test, *a, **kw)
        test_wrapped.__doc__ = test_method.__doc__
        return test_wrapped
    return decorator
