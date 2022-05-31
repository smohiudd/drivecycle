Battery Model
=========================

.. sectnum::

The battery module is used to simulate battery power requirements and battery
state of charger for a battery electric bus. It is determined using the following 
steps.

Total Tractive Force
---------------------


Rolling Resistance Force
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. math::

   F_r = \mu m g
   
* :math:`\mu`, is the coefficient of rolling resisance
* :math:`m`, mass of the vehicle in :math:`kg`
* :math:`g`, is the gravitational acceleration constant

Aerodynamic Drag Force
~~~~~~~~~~~~~~~~~~~~~~~

.. math::

   F_{ad} = \frac{1}{2}\ \rho A C_d v^2

* :math:`\rho`, density of air
* :math:`A`, frontal area in :math:`m^2`
* :math:`C_d`, drag coefficient
* :math:`v`, velocity in :math:`m/s`


Hill Climbing Force
~~~~~~~~~~~~~~~~~~~~

.. math::

   F_h = m g sin(\alpha)

* :math:`\alpha`, grade of the slope

Acceleration Force
~~~~~~~~~~~~~~~~~~~

.. math::

   F_a = m a

* :math:`a`, acceleration of the vehicle in :math:`m/s^2`


Total Tractive Force
~~~~~~~~~~~~~~~~~~~~

.. math::

   F_t = F_r + F_{ad} + F_h + F_a


Energy to move the Vehicle
---------------------------

.. math::

   P_t = F_t v

Energy Flow
------------

.. figure:: ../../images/energy_flow.png
    
    Electric Vehicle Technology Explained Second Edition


References
-----------

1. Electric Vehicle Technology Explained Second Edition
2. A Study on the Open Circuit Voltage and State of Charge Characterization of High Capacity Lithium-Ion Battery Under Different Temperature






