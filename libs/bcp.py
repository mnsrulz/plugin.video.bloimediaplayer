import abc


class BaseClassPlugin(object):
    __metaclass__ = abc.ABCMeta
    '''
    Your plugin needs to implement the abstract methods in this interface if
    it wants to be able to resolve URLs

    domains: (array) List of domains handled by this plugin. (Use ["*"] for universal resolvers.)
    '''
    domains = ['localdomain']
