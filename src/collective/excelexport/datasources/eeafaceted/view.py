from copy import copy
import urllib
from eea.facetednavigation.criteria.interfaces import ICriteria


class ExportUrl(object):

    def export_url(self):
        params = copy(self.request.form)

        params = dict((key.replace('[]', ''), val)
                      for key, val in params.items())

        ignored_params = ('version', 'b_start', 'reversed')
        for ignored in ignored_params:
            if ignored in params:
                del params[ignored]

        criteria = ICriteria(self.context)
        for param in params.keys():
            try:
                widgetclass = criteria.widget(cid=param)
            except KeyError:
                # if widget has been removed
                continue
            widget = widgetclass(self.context, self.request, criteria.get(param))
            if widget.widget_type == 'resultsperpage':
                del params[param]

        params['excelexport.policy'] = 'eea.facetednavigation'
        export_url = "%s/@@collective.excelexport?%s" % (self.context.absolute_url(),
                                                         urllib.urlencode(params, doseq=True))
        return export_url
