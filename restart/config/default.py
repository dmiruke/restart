# The mapping of request methods to resource actions.
ACTION_MAP = {
    'POST': 'create',
    'GET': 'read',
    'PUT': 'replace',
    'PATCH': 'update',
    'DELETE': 'delete',
    'OPTIONS': 'options',
    'HEAD': 'head',
    'TRACE': 'trace',
}

# The default Parser class and Renderer class
PARSER_CLASS = 'restart.parser.JSONParser'
RENDERER_CLASS = 'restart.renderer.JSONRenderer'
