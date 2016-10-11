import pickle

class Default:
  _options = []
  
  _members = []
  
  def __init__(self, *args, init_members=True, **kwargs):
    self._ezpickle_args = args
    self._ezpickle_kwargs = kwargs
    
    for opt in self._options:
      value = None
      if opt.name in kwargs:
        value = kwargs[opt.name]
      if value is None:
        value = opt.default
      setattr(self, opt.name, value)
    
    if init_members:
      self._init_members(**kwargs)
  
  def _init_members(self, **kwargs):
    for name, cls in self._members:
      setattr(self, name, cls(**kwargs))
  
  def items(self):
    for opt in self._options:
      yield opt.name, getattr(self, opt.name)
    for name, _ in self._members:
      yield name, getattr(self, name)
  
  def label(self):
    label = self.__class__.__name__
    for item in self.items():
      label += "_%s_%s" % item
    return label
  
  def __repr__(self):
    fields = ", ".join("%s=%s" % (name, str(value)) for name, value in self.items())
    return "%s(%s)" % (self.__class__.__name__, fields)
  
  @classmethod
  def full_opts(cls):
    yield from cls._options
    for _, cls_ in cls._members:
      yield from cls_.full_opts()
  
  def __getstate__(self):
    return {"_ezpickle_args" : self._ezpickle_args, "_ezpickle_kwargs": self._ezpickle_kwargs}
  def __setstate__(self, d):
    self.__init__(*d["_ezpickle_args"], **d["_ezpickle_kwargs"])
  
  def dump(self, f):
    pickle.dump(self._ezpickle_kwargs)
  
  @classmethod
  def load(cls, f, **override):
    kwargs = pickle.load(f)
    kwargs.update(**override)
    return cls.__init__(**kwargs)
  
class Option:
  def __init__(self, name, **kwargs):
    self.name = name
    self.default = None
    self.__dict__.update(kwargs)
    self.kwargs = kwargs
  
  def update_parser(self, parser):
    flag = "--" + self.name
    if flag in parser._option_string_actions:
      print("warning: already have option %s. skipping"%self.name)
    else:
      parser.add_argument(flag, **self.kwargs)
