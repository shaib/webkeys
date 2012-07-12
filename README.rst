===================================
 Webkeys: A keyboard layout editor
===================================

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
Firefox 3.5/3.6 and Chrome 9. It uses the Dojo toolkit.

The app is supported by a Pinax-based project, but is
intended not to depend on it (i.e. be reusable). If this
isn't the case, it's a bug.

To do
=====

This started as an exercise, and this heritage still shows. Things
to do if and when:

* Allow making layouts readonly without making them system
* Export Mac keymaps
* Tests

To do before release
====================

App
-----
* Only owners can edit layouts
* Export/Import (save layout as local file that can be restored)
* I18n, specifically Hebrew
* Undo
* Xkb features:
  + Level 3 selection
  + 6-level key type (for crazy caps and shift-caps behavior)
  + Downloadable patch files to ease installation
* KLC features:
  + Company name, author, copyright notice etc.

Project
-------
* User and layout search
* Comments on layouts

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
