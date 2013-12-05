"""
    Implements a listing of all instances for a given model.
"""
from dougrain import Builder

from slumber.operations import ModelOperation
from slumber.server import get_slumber_root
from slumber.server.http import require_user


class InstanceList(ModelOperation):
    """Allows access to the instances.
    """
    @require_user
    def get(self, request, response, _appname, _modelname):
        """Return a paged set of instances for this model.
        """
        root = get_slumber_root()
        response['model'] = root + self.model.path

        query = self.model.model.objects.order_by('-pk')
        if request.GET.has_key('start_after'):
            query = query.filter(pk__lt=request.GET['start_after'])

        response['page'] = [
                dict(pk=o.pk, display=unicode(o),
                    data=self.model.operations['data'](o))
            for o in query[:10]]
        if len(response['page']) > 0:
            response['next_page'] = self(
                start_after=response['page'][-1]['pk'])


def hal_instance_list(builder, query_set):
    """Return a page of JSON-HAL based results across the query set.
    """
    from slumber import data_link
    for instance in query_set.order_by('-pk').iterator():
        item = Builder(data_link(instance))
        item.set_property('display', unicode(instance))
        builder.embed('page', item)


class InstanceListHal(ModelOperation):
    """Allow us to get an instance list in HAL format.
    """
    @require_user
    def get(self, _request, response, _appname, _modelname):
        """Return a HAL formatted version of the instance list.
        """
        root = get_slumber_root()

        hal = Builder(self.uri)
        hal.add_link('model', root + self.model.path)

        query = self.model.model.objects
        hal_instance_list(hal, query)

        response["instances"] = hal.as_object()
