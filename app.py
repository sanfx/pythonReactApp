import tg
from tg import AppConfig
from tg import TGController
from tg import expose
import kajiki

page = kajiki.XMLTemplate(u'''<html>
	<head></head>
	<body>
	  <div id="isomor">${render_react('HelloWorld.HelloWorld', name='from React on master branch')}</div>

	  <script py:for="m in g.webassets['bundle.js'].urls()"
			  src="$m">
	  </script>
	  <script>
ReactDOM.render(
	React.createElement(js.HelloWorld.HelloWorld, { name: "from React on master branch" }),
	document.getElementById('isomor')
);
	  </script>
	</body>
</html>
''', mode='html5')



class RootController(TGController):
	@expose()
	def index(self):
		return page(dict(
			render_react=tg.config['react_renderer'].render,
			g=tg.app_globals
		)).render()


import json
from dukpy import JSInterpreter, jsx_compile
from markupsafe import Markup


class ReactRenderer(object):
	def __init__(self, jspath):
		self.jspath = jspath
		self.jsi = JSInterpreter()
		self.jsi.loader.register_path(self.jspath)
		self.components = {}
		self.initialized = False

	def _init(self):
		if self.initialized:
			return

		bundle_js = tg.app_globals.webassets['bundle.js']
		self.jsi.evaljs(
			[f.data() for f in bundle_js.build()] +
			["var ReactDOM = require('react-dom-server');"]
		)
		self.initialized = True

	def render(self, component, **kwargs):
		self._init()
		code = "ReactDOM.renderToString(React.createElement({component}, {args}), null);".format(component=component, args=json.dumps(kwargs))
		return Markup(self.jsi.evaljs(code))


config = AppConfig(minimal=True, root_controller=RootController())
config.renderers = ['kajiki']
config.serve_static = True
config.paths['static_files'] = '/app'
config.react_renderer = ReactRenderer("/app/js")

from webassets.filter import register_filter
from dukpy.webassets import BabelJSX
register_filter(BabelJSX)

import tgext.webassets as wa
wa.plugme(
	config,
	options={
		'babel_modules_loader': 'umd'
	},
	bundles={
		'bundle.js': wa.Bundle(
			'js/react.js',
			'js/react-dom.js',
			wa.Bundle(
				'js/HelloWorld.jsx',
				filters='babeljsx',
			),
			output='assets/bundle.js'
		)
	}
)

application = config.make_wsgi_app()

from wsgiref.simple_server import make_server
print(__file__)
print("Serving on port 8080...")
httpd = make_server('', 8080, application)
httpd.serve_forever()
