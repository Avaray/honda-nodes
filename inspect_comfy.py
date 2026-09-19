import sys
import inspect
try:
    from comfy_api.latest import io
    print(inspect.signature(io.Autogrow.TemplatePrefix.__init__))
except Exception as e:
    print(e)
