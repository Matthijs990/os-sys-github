import functools
from pathlib import Path

from server.conf import settings
from server.template.backends.server import ServerTemplates
from server.template.loader import get_template
from server.utils.functional import cached_property
from server.utils.module_loading import import_string

try:
    from server.template.backends.jinja2 import Jinja2
except ImportError:
    def Jinja2(params):
        raise ImportError("jinja2 isn't installed")

ROOT = Path(__file__).parent


@functools.lru_cache()
def get_default_renderer():
    renderer_class = import_string(settings.FORM_RENDERER)
    return renderer_class()


class BaseRenderer:
    def get_template(self, template_name):
        raise NotImplementedError('subclasses must implement get_template()')

    def render(self, template_name, context, request=None):
        template = self.get_template(template_name)
        return template.render(context, request=request).strip()


class EngineMixin:
    def get_template(self, template_name):
        return self.engine.get_template(template_name)

    @cached_property
    def engine(self):
        return self.backend({
            'APP_DIRS': True,
            'DIRS': [str(ROOT / self.backend.app_dirname)],
            'NAME': 'serverforms',
            'OPTIONS': {},
        })


class ServerTemplates(EngineMixin, BaseRenderer):
    """
    Load Server templates from the built-in widget templates in
    server/forms/templates and from apps' 'templates' directory.
    """
    backend = ServerTemplates


class Jinja2(EngineMixin, BaseRenderer):
    """
    Load Jinja2 templates from the built-in widget templates in
    server/forms/jinja2 and from apps' 'jinja2' directory.
    """
    backend = Jinja2


class TemplatesSetting(BaseRenderer):
    """
    Load templates using template.loader.get_template() which is configured
    based on settings.TEMPLATES.
    """
    def get_template(self, template_name):
        return get_template(template_name)
