import xlwt
from collective.excelexport.interfaces import IStyles
from zope.component import adapts
from zope.interface import implementer, Interface


@implementer(IStyles)
class Styles(object):

    def __init__(self, context, request):
        pass

    adapts(Interface, Interface)

    content = xlwt.easyxf(
        'font: height 200, name Arial, colour_index black, bold off; '
        'align: wrap on, vert centre, horiz left;'
        'borders: top thin, bottom thin, left thin, right thin;'
        'pattern: pattern solid, back_colour light_yellow, fore_colour light_yellow'
    )

    headers = xlwt.easyxf(
        'font: height 200, name Arial, colour_index black, bold on; '
        'align: wrap on, vert centre, horiz center; '
        'borders: top thin, bottom thin, left thin, right thin; '
        'pattern: pattern solid, back_colour light_orange, fore_colour light_orange; '
    )
