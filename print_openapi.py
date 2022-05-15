#!/usr/bin/env python

import yaml

from app import app

print(yaml.dump(app.openapi()))
