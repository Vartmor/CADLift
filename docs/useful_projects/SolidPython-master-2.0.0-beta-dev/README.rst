SolidPython
===========
   
OpenSCAD for Python
-------------------

SolidPython is a generalization of Phillip Tiefenbacher's openscad
module, found on `Thingiverse <http://www.thingiverse.com/thing:1481>`__. It
generates valid OpenSCAD code from Python code with minimal overhead. Here's a
simple example:

This Python code:

.. code:: python

    from solid2 import *
    d = cube(5) + sphere(5).right(5) - cylinder(r=2, h=6)

Generates this OpenSCAD code:

.. code::

    difference(){
        union(){
            cube(5);
            translate( [5, 0,0]){
                sphere(5);
            }
        }
        cylinder(r=2, h=6);
    }

As can be clearly seen, the SolidPython code is a lot shorter (and I think a lot better readable and maintainable) than the OpenSCAD code it compiles to.

Advantages
----------

In contrast to OpenSCAD -- which is a constrained domain specific language --
Python is a full blown modern programming language and as such supports
pretty much all modern programming features. Furthermore a huge number of
libraries is available.

SolidPython lets you use all these fancy python features to generate your
constructive solid geometry models.

On the one hand it makes the generation of your models a lot easier, because
you don't need to learn another domain specific language and you can use all
the programming technique you're already familiar with. On the other hand it
gives you a lot more power, because you can use all the comprehensive python
libraries to generate your models.


Getting Started
---------------

The `wiki <https://github.com/jeff-dh/SolidPython/wiki>`__ is the place to look for docs and tutorials. Furthermore the `examples <https://github.com/jeff-dh/SolidPython/tree/master-2.0.0-beta-dev/solid2/examples>`__ might be interesting to you too.

Contact
=======

Enjoy!

If you have any questions or bug reports please report them to the SolidPython
`GitHub page <https://github.com/jeff-dh/SolidPython>`__!

Cheers!

License
=======

This library is free software; you can redistribute it and/or modify it
under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation; either version 2.1 of the License, or (at
your option) any later version.

This library is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
General Public License for more details.

`Full text of the
license <http://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt>`__.

Some class docstrings are derived from the `OpenSCAD User Manual
<https://en.wikibooks.org/wiki/OpenSCAD_User_Manual>`__, so 
are available under the `Creative Commons Attribution-ShareAlike License
<https://creativecommons.org/licenses/by-sa/3.0/>`__. 

