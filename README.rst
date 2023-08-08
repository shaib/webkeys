===================================
 Webkeys: A keyboard layout editor
===================================

This project is on ice
======================
This project hasn't been touched in 11 years, and likely won't be
updated very soon. The front-end framework (Dojo) probably needs
replacing (last updated Feb 2022), Django has changed so much since
in 11 years that it isn't funny, so what's needed to bring this to
life is effectively a full rewrite.


Layout Editor
=============

This is a little Django application for very specific keyboard
layout editing needs. Its specific features include:

* Fixed 4 shift levels
* Reference layout (QWERTY) optionally shown
* Generation of both KLC and XKB mapping files
* Special support for presenting certain characters, including:

  - Unicode joiner characters
  - Unicode BiDi direction markers (RLM & LRM)
  - Hebrew points (ניקוד)
  - Hebrew accents (טעמים)

The app relies on certain HTML5 and CSS3 features, and likely
doesn't work at all on IE<9. It was tested (more or less) on
Firefox 10 and Chrome. It uses the Dojo toolkit.

The app is supported by a Pinax-based project, but is
intended not to depend on it (i.e. be reusable). If this
isn't the case, it's a bug.

Installation and use
====================

The Pinax project does not include an explicit reference
to the layouteditor app; it is written to just find it
on the Python path.

The way I achieve this is by putting in the site-packages
folder of my virtualenv (you are using one, right?) a file
named webkeys.pth whose contents are one line -- the path
to the folder containing both ``layouteditor`` and ``proj_pinax``.

Other than that, pretty standard; the ``pip`` requirements
file is ``proj_pinax/requirements/project.txt``, as usual
for Pinax based projects.

The ``layouteditor`` app expects that if there is a user profile,
it supports the properties ``name`` and ``affiliation``, and a method
``copyright(start_year, end_year)`` returning a copyright notice. 
A user profile is not mandatory, though.

Roadmap
=======

-----------
Release 0.3
-----------

* Export/Import (save layout as local file that can be restored)
* I18n, specifically Hebrew
* Comments on layouts
* Support for standard-compliant layouts:
  + At best, when user selects to make the layout standard,
    make bindings defined by the standard unchangeable.
  + At least, add an easy indication whether the layout
    is standard-compliant
* Django 1.5 

------
Future
------

* Allow making layouts readonly without making them system
* Export Mac keymaps
* Tests
* "Social" features:

  + Link layout clones to originals
  + Clone counts and clone lists from originals
  + Diff from clone to original
  + Suggestions to original, a-la Pull Request


