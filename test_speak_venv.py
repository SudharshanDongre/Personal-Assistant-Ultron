import sys
import platform
import traceback

print('platform:', platform.platform())
print('python executable:', sys.executable)

def try_import(name):
    try:
        m = __import__(name)
        v = getattr(m, '__version__', repr(m))
        print(f"{name} imported, version/obj: {v}")
        return m
    except Exception as e:
        print(f"{name} import error:", repr(e))
        return None

pyttsx3 = try_import('pyttsx3')
comtypes = try_import('comtypes')
win32 = try_import('win32api')

if pyttsx3:
    try:
        engine = pyttsx3.init()
        print('engine object:', type(engine))
        engine.say('This is a quick test from the test script.')
        engine.runAndWait()
        print('runAndWait completed successfully')
    except Exception:
        traceback.print_exc()
        print('engine runtime error')
