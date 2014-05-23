# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2009–2014 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import codecs
import os
from setuptools import setup, find_packages
from version import get_version

version = get_version()

with codecs.open('README.txt', encoding='utf-8') as f:
    long_description = f.read()
with codecs.open(os.path.join("docs", "HISTORY.txt"), encoding='utf-8') as f:
    long_description += '\n' + f.read()

setup(name='Products.GSGroup',
      version=version,
      description="",
      long_description=long_description,
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Michael JasonSmith',
      author_email='mpj17@onlinegroups.net',
      url='http://source.iopen.net/groupserver/Products.GSGroup/',
      license='ZPL 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'pytz',
          'sqlalchemy',
          'AccessControl',
          'zope.app.folder',
          'zope.component',
          'zope.interface',
          'zope.schema',
          'gs.cache',
          'gs.core',
          'gs.database',
          'gs.groups',
          'Products.CustomUserFolder',
          'Products.GSGroupMember',  # Eh?
          'Products.XWFCore',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
