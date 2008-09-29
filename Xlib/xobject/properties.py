# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.
# Originally part of whimsy http://incise.org/whimsy.html Public Domain
# Modified and adapted by Dan Roberts 2008

# NOTES: I had some good plans for this,
# However I still need to organize things in my head
# I'm only committing this so that there's *something*
# in the git repos

from Xlib.protocol import request, rq
from Xlib import X, Xatom, protocol
from Xlib.Xatom import XAtom, atom
from Xlib.xobject import drawable
import types


# FIXME: USE ADAPTER PATTERN?

#datatype_sizes = {
#    'ATOM': 32,
#    'CARDINAL': 32,
#    'STRING': 8,
#    'UTF8_STRING': 8,
#    'WINDOW': 32,
#    XAtom: 32,
#    int: 32,
#    string: 8,
#    unicode: 8,
#    Window: 32,
#}
#
#class prop_definition(object):
#    def __init__(self, type, aggregate_type='single', aggregate_size_multiple=1):
#        self.type = type
#        self.aggregate_type = aggregate_type
#        self.aggregate_size_multiple = aggregate_size_multiple
#
#    @property
#    def format(self):
#        return datatype_sizes[self.type]
#
#    def validate(self, agg):
#        if self.aggregate_type != 'array':
#            self.validate_single_element(agg)
#            return
#        iter(agg)
#        assert len(agg) % self.aggregate_size_multiple == 0
#        for x in agg:
#            self.validate_single_element(x)
#
#    def validate_single_element(self, val):
#        # unicode stuff is still seriously retarded
#        if self.type == 'UTF8_STRING':
#            assert val == unicode(val)
#        elif self.type == 'STRING':
#            assert val == str(val)
#        elif self.type in ('ATOM', 'CARDINAL', 'WINDOW'):
#            assert (
#                isinstance(val, types.LongType) or isinstance(val, types.IntType)
#                or (self.type == 'WINDOW' and isinstance(val, drawable.Window))
#            )
#
#    def convert(self, val):
#        if self.aggregate_type == 'array':
#            return [ self.convert_single_element(v) for v in val ]
#        elif self.aggregate_type == 'nullarray':
#            return [ self.convert_single_element(v) + '\0' for v in val ]
#        elif self.format == 32:
#            return [ self.convert_single_element(val) ]
#        return self.convert_single_element(val)
#
#    def convert_single_element(self, val):
#        # doing change_prop(..., [ w.id for w in windows ]) gets real old, so
#        # whereas python-xlib only takes numerical window ids for a WINDOW
#        # property, we allow window objects to be passed in and we use the id
#        # property of the objects automatically
#        if self.type == 'WINDOW' and isinstance(val, drawable.Window):
#            return val.id
#        return val

class PropertyTypeError(TypeError):
	def __init__(self, expected, value):
		TypeError.__init__(self,
			"Property is of type %s, received a value of type %s" %
			(str(expected), str(type(value)))
				)
		self.expected = expected
		self.value = value

def get_text_property(window, display, property_name):
	property = XAtom(display, property_name)
        r = request.GetProperty(display = display,
                                delete = False,
                                window = window,
                                property = int(property),
                                type = 0,
                                long_offset = 0,
                                long_length = 1000000)
	
	UTF8_STRING = XAtom(display, "UTF8_STRING")
	if r.property_type == Xatom.STRING:
		return str(r.value)
	elif r.property_type == Xatom.ATOM:
		atom = XAtom.from_card(r.property_type)
		return str(atom)
	elif r.property_type == int(UTF8_STRING):
		return unicode(r.value)
	else:
		raise TypeError("Property is of type %s not a text type" % str(atom(r.value)))

class Property(object):
	def __init__(self, type):
		self.type = type
	def validate(self, value):
		if self.type == XAtom:
			if type(value) in (string, unicode): return

		try:
			self.type(value)
		except TypeError:
			raise PropertyTypeError(self.type, value)

	def convert(self, value):
		return self.type(value)

class PropertyArray(Property):
	def __init__(self, window, property):
		self.property = property
		self.count = count
	def append(self, value):
			
	def extend(self, value):
		
def array_of(type, count=0):
	if count != 0:
		return PropertyArray(Property(type), count)
	else:
		raise UnimplementedError("Multi length arrays haven't been implemented yet")

_NET_WM = {
    "_NET_WM_NAME":              unicode,
    "_NET_WM_VISIBLE_NAME":      unicode,
    "_NET_WM_ICON_NAME":         unicode,
    "_NET_WM_VISIBLE_ICON_NAME": unicode,

    "_NET_WM_WINDOW_TYPE":       [XAtom],
    "_NET_WM_STATE":             [XAtom],
    "_NET_WM_ALLOWED_ACTIONS":   [XAtom],

    "_NET_WM_DESKTOP":           int,
    "_NET_WM_PID":               int,
    "_NET_WM_USER_TIME":         int,

    "_NET_DESKTOP_GEOMETRY":     array_of("CARDINAL", "array", 2), #
    "_NET_WM_ICON_GEOMETRY":     array_of("CARDINAL", "array", 4), #  what to do
    "_NET_FRAME_EXTENTS":        array_of("CARDINAL", "array", 4), # 
    "_NET_WM_STRUT":             array_of("CARDINAL", "array", 4), # 
    "_NET_WM_STRUT_PARTIAL":     array_of("CARDINAL", "array", 12), #

    # client and root
    "_NET_SUPPORTING_WM_CHECK":  array_of("WINDOW"),

    # root
    "_NET_NUMBER_OF_DESKTOPS":   array_of(int),
    "_NET_SHOWING_DESKTOP":      array_of(int),
    "_NET_CURRENT_DESKTOP":      array_of(int),

    "_NET_ACTIVE_WINDOW":        array_of("WINDOW"),

    "_NET_DESKTOP_NAMES":        array_of("UTF8_STRING", "array"),

    "_NET_SUPPORTED":            array_of("ATOM", "array"),

    "_NET_CLIENT_LIST":          array_of("WINDOW", "array"),
    "_NET_CLIENT_LIST_STACKING": array_of("WINDOW", "array"),
    "_NET_VIRTUAL_ROOTS":        array_of("WINDOW", "array"),

    "_NET_DESKTOP_VIEWPORT":     array_of("CARDINAL", "array", 2),
    "_NET_WORKAREA":             array_of("CARDINAL", "array", 4),

    "_NET_DESKTOP_LAYOUT":       array_of("CARDINAL", "array", 4),
}

window_hints = {
    "WM_STATE":                  int,
    "WM_NAME":                   string,
    "WM_CLASS":                  [string],
    "WM_ICON_NAME":              string,
    "WM_PROTOCOLS":              [XAtom]
}

def supported_props():
    return all_props.keys()

def send_window_message(dpy, win, name, data,
        ev_win=X.NONE,
        event_mask=X.SubstructureNotifyMask|X.SubstructureRedirectMask):

    format = all_props[name].format

    data += [0] * (160/format - len(data))
    win.send_event(
        protocol.event.ClientMessage(
            window = ev_win,
            client_type = dpy.get_atom(name),
            data = (format, data),
        ),
        event_mask=event_mask
    )

def prepare_prop_for_write(dpy, name, value):
    definition = all_props[name]
    definition.validate(value)
    return (
        dpy.get_atom(definition.type),
        definition.format,
        definition.convert(value)
    )

def change_prop(dpy, win, name, value):
    type, format, processed_val = prepare_prop_for_write(dpy, name, value)
    win.change_property(dpy.get_atom(name), int(type), format, processed_val)

def get_prop(dpy, win, name):
    definition = all_props[name]
    prop = win.get_full_property(dpy.get_atom(name), dpy.get_atom(definition.type))

    if prop is None:
        return None if definition.aggregate_type == 'single' else []

    if definition.aggregate_type == 'array':
        return list(prop.value)

    if definition.aggregate_type == 'nullarray':
        return prop.value.split('\0')[:-1]

    if definition.format == 32:
        assert len(prop.value) in (0, 1)
        if not len(prop.value):
            return None
        return prop.value[0]
    return prop.value

def delete_prop(dpy, win, name):
    win.delete_property(dpy.get_atom(name))

class Properties(object):
	properties = {}
	def __init__(self, window):
		self.window = window
		self.properties = {}
		self.property_sources = [window.display, Properties, self.properties]
	def _get_property_source(self, property_name, property):
		property_source = None
		for property_source_try in self.property_sources:
			property_source = property_source_try
			if not property_name in property_source_try.properties:
				break
	def get_property(self, property_name):
		if property_name in self.properties:
			return self.properties[property_name]
		elif property_name in properties:
			return properties[property_name]
		else:
			raise NameError("Property %s is not handled" % property_name)
	def __getitem__(self, name): 
		property = self._get_property_source(name)[name]
	def __setitem__(self, name, value):
		property = self._get_property_source(name)[name]
		change_prop(self.window.display, self.window, name, value)
	def __delitem__(self, name):
		request.DeleteProperty(self.window, atom(name))
	def keys(self):
		response = request.ListProperties(display = self.window.display, window = self.window)
		print response.value
		return [str(value) for value in response.value]
