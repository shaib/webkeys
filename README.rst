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

Roadmap
=======

-----------
Release 0.2
-----------

App
-----
* Undo
* Xkb features:

  + Downloadable patch files to ease installation

* KLC features:

  + Company name, author, copyright notice etc.
    
    - Actually, these fit well in a user profile; we should
      add a description per layout as well. Whichever of the
      fields don't have entries for them in the file format,
      can be pushed in as comments. And then they can all go
      in xkb as well.

* Pre-installed system layouts (code for generation exists)
* Links to help from within editor and key-edit dialog


Project
-------
* User profile page
* User and layout search
* Comments on layouts
* Missing semi-static pages (use-klc, about, ...)

-----------
Release 0.3
-----------

* Export/Import (save layout as local file that can be restored)
* I18n, specifically Hebrew

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


