import os
import pkgutil
import importlib
import sys
import traceback

# Ensure project root is on sys.path when running this script from ./scripts
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import click_inflation_chatbot.agents as agents_pkg

ok = []
errors = []

print('Discovering modules under click_inflation_chatbot.agents...')
for finder, name, ispkg in pkgutil.iter_modules(agents_pkg.__path__):
    full_name = 'click_inflation_chatbot.agents.' + name
    try:
        importlib.import_module(full_name)
        ok.append(name)
        print('OK:', full_name)
    except Exception:
        tb = traceback.format_exc()
        errors.append((name, tb))
        print('ERROR importing', full_name)
        print(tb)

print('\nSummary:')
print('  OK modules:', len(ok))
print('  Error modules:', len(errors))

if errors:
    print('\nDetailed errors available for the first 5 failures:')
    for name, tb in errors[:5]:
        print('\n-- Module:', name)
        print(tb)
    sys.exit(2)

sys.exit(0)
