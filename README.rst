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
  - Unicode BiDi direction markers (RTL & LTR)
  - Hebrew points (ניקוד)
  - Hebrew accents (טעמים)

The app relies on certain HTML5 and CSS3 features, and likely
doesn't work at all on IE<9. It was tested (more or less) on
Firefox 3.5/3.6 and Chrome 9. It uses the Dojo toolkit.

To do
=====

This started as an exercise, and this heritage still shows. Things
to do if and when:

* Make consistent use of Dojo controls
* Make layouts belong to users, in the sense of permissions to edit
* Allow making layouts readonly
* Export Mac keymaps
* Improve KLC export
* Improve presentation
* Structured font selection
* Tests

